"""Server CGI methods.
"""
#
# Copyright (c) 2005 shinGETsu Project.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHORS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

import gzip
import re
from http import HTTPStatus
from io import TextIOWrapper
from time import time
from random import choice

from . import address
from . import config
from . import basecgi
from . import title
from .cache import *
from .node import *
from .updatequeue import UpdateQueue
from .util import opentext


class CGI(basecgi.CGI):
    """Class for /server.cgi.
    """

    def run(self):
        path = self.path_info()

        httphost = self.environ["HTTP_HOST"]
        if (config.dnsname and
            config.dnsname_should_match and
            f'{config.dnsname}:{config.port}' != httphost):
            return self.send_error(HTTPStatus.FORBIDDEN,
                                   'error: invalid http host')

        if not self.environ["REQUEST_METHOD"] in ("GET", "HEAD"):
            return self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)
        elif path == "":
            return self.do_motd()
        elif path == "ping":
            return self.do_ping()
        elif path == "node":
            return self.do_node()
        elif path.startswith("join"):
            return self.do_join(path)
        elif path.startswith("bye"):
            return self.do_bye(path)
        elif path.startswith("have"):
            return self.do_have(path)
        elif path.startswith("head") or path.startswith("get"):
            return self.do_get_head(path)
        elif path.startswith("recent"):
            return self.do_recent(path)
        elif path.startswith("update"):
            return self.do_update(path)
        elif path.startswith("version"):
            return self.do_version()
        else:
            return self.send_error(HTTPStatus.NOT_FOUND,
                                   'error: command not found')

    def path_info(self):
        '''Parse PATH_INFO.'''
        path = self.environ.get('PATH_INFO', '')
        if path.startswith('/'):
            path = path[1:]
        return path

    def header(self, content='text/plain; charset=UTF-8', additional=None):
        headers = [('Content-Type', content)]
        if additional:
            for k in additional:
                headers.append((k, additional[k]))
        self.start_response('200 OK', headers)

    def do_motd(self):
        self.header()
        try:
            with opentext(config.motd) as f:
                return self.body(f)
        except IOError:
            self.stderr.write(config.motd + ": IOError\n")
            return []

    def do_ping(self):
        self.header()
        remote_addr = address.remote_addr(self.environ)
        return self.body(["PONG\n" + str(remote_addr) + "\n"])

    def do_node(self):
        nodes = NodeList()
        self.header()
        try:
            return self.body([str(nodes[0]) + "\n"])
        except IndexError:
            inode = choice(init_node())
            return self.body(["%s\n" % inode])

    def get_remote_hostname(self, host):
        remote_addr = address.remote_addr(self.environ)
        if host == '':
            return str(remote_addr)
        if address.host_has_addr(host, str(remote_addr)):
            return host
        return None

    def do_join(self, path_info):
        self.header()
        m = re.search(r"^join/([^:]*):(\d+)(.*)", path_info)
        if m is None:
            return []
        (host, port, path) = m.groups()
        host = self.get_remote_hostname(host)
        if not host:
            return []
        try:
            node = Node(host=host, port=port, path=path)
        except ValueError:
            return []
        if (not node_allow().check(str(node)) and
            node_deny().check(str(node))):
            return []
        if not node.ping():
            return []

        nodelist = NodeList()
        searchlist = SearchList()
        if node in nodelist:
            searchlist.append(node)
            searchlist.sync()
            return self.body(["WELCOME\n"])
        elif nodelist.is_within_limit(node):
            nodelist.append(node)
            nodelist.sync()
            searchlist.append(node)
            searchlist.sync()
            return self.body(["WELCOME\n"])
        else:
            searchlist.append(node)
            searchlist.sync()
            suggest = nodelist[0]
            nodelist.remove(suggest)
            nodelist.append(node)
            nodelist.sync()
            suggest.bye()
            return self.body(["WELCOME\n%s\n" % suggest])

    def do_bye(self, path_info):
        self.header()
        m = re.search(r"^bye/([^:]*):(\d+)(.*)", path_info)
        if m is None:
            return []
        (host, port, path) = m.groups()
        host = self.get_remote_hostname(host)
        if not host:
            return []
        try:
            node = Node(host=host, port=port, path=path)
        except ValueError:
            return []
        nodelist = NodeList()
        try:
            nodelist.remove(node)
            nodelist.sync()
        except ValueError:
            pass
        return self.body(["BYEBYE\n"])

    def do_have(self, path):
        self.header()
        m = re.search(r"^have/([0-9A-Za-z_]+)$", path)
        if m is None:
            return []
        cache = Cache(m.group(1))
        if (len(cache) > 0):
            return self.body([("YES\n")])
        else:
            return self.body(["NO\n"])

    def do_get_head(self, path):
        m = re.search(r"^(get|head)/([0-9A-Za-z_]+)/([-0-9A-Za-z/]*)$", path)
        if m is None:
            self.header()
            return []
        (method, datfile, stamp) = m.groups()
        cache = Cache(datfile)
        begin, end, id = self.parse_stamp(stamp, cache.stamp)
        def gen():
            for r in cache:
                if id and r.idstr.endswith(id):
                    pass
                elif r.stamp < begin or end < r.stamp:
                    continue
                if method == "get":
                    r.load()
                    yield self.bytes(str(r) + '\n')
                    r.free()
                else:
                    yield self.bytes(r.idstr.replace('_', '<>') + '\n')
        return self.gzipped(gen())

    def parse_stamp(self, stamp, last):
        buf = stamp.split("/")
        if len(buf) > 1:
            id = buf[1]
            stamp = buf[0]
        else:
            id = None
        try:
            buf = stamp.split("-")
            if (stamp == "") or (stamp == "-"):
                return (0, last, id)
            elif stamp.endswith("-"):
                return (int(buf[0]), last, id)
            elif len(buf) == 1:
                return (int(buf[0]), int(buf[0]), id)
            elif buf[0] == "":
                return (0, int(buf[1]), id)
            else:
                return (int(buf[0]), int(buf[1]), id)
        except ValueError:
            return (0, 0, None)

    def do_recent(self, path):
        m = re.search(r"^recent/?([-0-9A-Za-z/]*)$", path)
        if m is None:
            self.header()
            return []
        stamp = m.group(1)
        recent = RecentList()
        last = int(time()) + config.recent_range
        begin, end, id = self.parse_stamp(stamp, last)
        def gen():
            for i in recent:
                if i.stamp < begin or end < i.stamp:
                    continue
                cache = Cache(i.datfile)
                if cache.tags:
                    tagstr = '<>tag:%s' % cache.tags
                else:
                    tagstr = ''
                line = '%s<>%s<>%s%s\n' % (i.stamp, i.id, i.datfile, tagstr)
                yield self.bytes(line)
        return self.gzipped(gen())

    def do_update(self, path_info):
        self.header()
        m = re.search(r"^update/(\w+)/(\d+)/(\w+)/([^:]*):(\d+)(.*)",path_info)
        if m is None:
            return []
        (datfile, stamp, id, host, port, path) = m.groups()
        if not title.is_valid_file(datfile, 'thread'):
            return []
        if not host:
            host = self.get_remote_hostname(host)
        if not host:
            return []
        try:
            node = Node(host=host, port=port, path=path)
        except ValueError:
            return []
        if (not node_allow().check(str(node))) and \
             node_deny().check(str(node)):
            return []
        if not self._seem_valid_relay_node(host, node, datfile):
            return []
        searchlist = SearchList()
        searchlist.append(node)
        searchlist.sync()
        lookuptable = LookupTable()
        lookuptable.add(datfile, node)
        lookuptable.sync()

        now = int(time())
        if (int(stamp) < now - config.update_range) or \
           (int(stamp) > now + config.update_range):
            return []
        rec = Record(datfile=datfile, idstr=stamp+"_"+id)
        updatelist = UpdateList()
        if rec in updatelist:
            return self.body(["OK\n"])
        else:
            queue = UpdateQueue()
            queue.append(datfile, stamp, id, node)
            queue.start()
            return self.body(["OK\n"])
        
    def do_version(self):
        self.header()
        return self.body(["{}".format(config._get_version()) + "\n"])

    def _seem_valid_relay_node(self, host, node, datfile):
        remote_addr = address.remote_addr(self.environ)
        if address.host_has_addr(host, str(remote_addr)):
            return True
        cache = Cache(datfile)
        if not cache.exists():
            return True
        if cache.node and node in cache.node:
            return True
        return False

# End of CGI
