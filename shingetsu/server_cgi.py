"""Server CGI methods.
"""
#
# Copyright (c) 2005-2014 shinGETsu Project.
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
import socket
from time import time
from random import choice

from . import config
from . import basecgi
from .cache import *
from .node import *
from .updatequeue import UpdateQueue


class CGI(basecgi.CGI):

    """Class for /server.cgi."""

    def run(self):
        path = self.path_info()

        if not self.environ["REQUEST_METHOD"] in ("GET", "HEAD"):
            self.header("text/plain")
        elif path == "":
            self.do_motd()
        elif path == "ping":
            self.do_ping()
        elif path == "node":
            self.do_node()
        elif path.startswith("join"):
            self.do_join(path)
        elif path.startswith("bye"):
            self.do_bye(path)
        elif path.startswith("have"):
            self.do_have(path)
        elif path.startswith("head") or path.startswith("get"):
            self.do_get_head(path)
        elif path.startswith("recent"):
            self.do_recent(path)
        elif path.startswith("update"):
            flag = self.do_update(path)
            if flag:
                self.stdout.write("OK\n")

    def path_info(self):
        '''Parse PATH_INFO.'''
        path = self.environ.get('PATH_INFO', '')
        if path.startswith('/'):
            path = path[1:]
        return path

    def header(self, content='text/plain', addtional=None):
        self.stdout.write('Content-Type: %s\r\n' % content)
        if addtional:
            for k in addtional:
                self.stdout.write('%s: %s\r\n' % (k, addtional[k]))
        self.stdout.write('\r\n')

    def do_motd(self):
        self.header("text/plain")
        try:
            f = open(config.motd)
            for line in f:
                self.stdout.write(line)
            f.close()
        except IOError:
            self.stderr.write(config.motd + ": IOError\n")

    def do_ping(self):
        self.header("text/plain")
        self.stdout.write("PONG\n" + self.environ["REMOTE_ADDR"] + "\n")

    def do_node(self):
        nodes = NodeList()
        self.header("text/plain")
        try:
            self.stdout.write(str(nodes[0]) + "\n")
        except IndexError:
            inode = choice(init_node())
            self.stdout.write("%s\n" % inode)

    def get_remote_hostname(self, host):
        remote_addr = self.environ['REMOTE_ADDR']
        if host == '':
            return remote_addr
        ipaddr = socket.gethostbyname(host)
        if ipaddr == remote_addr:
            return host
        return None

    def do_join(self, path_info):
        self.header("text/plain")
        m = re.search(r"^join/([^:]*):(\d+)(.*)", path_info)
        if m is None:
            return
        (host, port, path) = m.groups()
        host = self.get_remote_hostname(host)
        if not host:
            return
        node = Node(host=host, port=port, path=path)
        nodelist = NodeList()
        searchlist = SearchList()
        if (not node_allow().check(str(node))) and \
             node_deny().check(str(node)):
            pass
        elif not node.ping():
            pass
        elif node in nodelist:
            searchlist.append(node)
            searchlist.sync()
            self.stdout.write("WELCOME\n")
        elif len(nodelist) < config.nodes:
            nodelist.append(node)
            nodelist.sync()
            searchlist.append(node)
            searchlist.sync()
            self.stdout.write("WELCOME\n")
        else:
            searchlist.append(node)
            searchlist.sync()
            suggest = nodelist[0]
            nodelist.remove(suggest)
            nodelist.sync()
            suggest.bye()
            self.stdout.write("WELCOME\n%s\n" % suggest)

    def do_bye(self, path_info):
        self.header("text/plain")
        m = re.search(r"^bye/([^:]*):(\d+)(.*)", path_info)
        if m is None:
            return
        (host, port, path) = m.groups()
        host = self.get_remote_hostname(host)
        if not host:
            return
        node = Node(host=host, port=port, path=path)
        nodelist = NodeList()
        try:
            nodelist.remove(node)
            nodelist.sync()
        except ValueError:
            pass
        self.stdout.write("BYEBYE\n")

    def do_have(self, path):
        self.header("text/plain")
        m = re.search(r"^have/([0-9A-Za-z_]+)$", path)
        if m is None:
            return
        cache = Cache(m.group(1))
        if (len(cache) > 0):
            self.stdout.write("YES\n")
        else:
            self.stdout.write("NO\n")

    def output(self):
        encoding = self.environ.get("HTTP_ACCEPT_ENCODING", "")
        if (encoding.find("gzip") >= 0) or (encoding.find("*") >= 0):
            self.header("text/plain", {"Content-Encoding": "gzip"})
            fp = gzip.GzipFile(fileobj=self.stdout)
        else:
            self.header("text/plain")
            fp = self.stdout
        return fp

    def do_get_head(self, path):
        m = re.search(r"^(get|head)/([0-9A-Za-z_]+)/([-0-9A-Za-z/]*)$", path)
        if m is None:
            self.header("text/plain")
            return
        (method, datfile, stamp) = m.groups()
        cache = Cache(datfile)
        begin, end, id = self.parse_stamp(stamp, cache.stamp)
        fp = self.output()
        for r in cache:
            if (begin <= r.stamp) and (r.stamp <= end) \
                    and ((id is None) or r.idstr.endswith(id)):
                if method == "get":
                    r.load()
                    fp.write(str(r) + '\n')
                    r.free()
                else:
                    fp.write(r.idstr.replace("_", "<>") + '\n')

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
            self.header("text/plain")
            return
        stamp = m.group(1)
        recent = RecentList()
        last = int(time()) + config.recent_range
        begin, end, id = self.parse_stamp(stamp, last)
        fp = self.output()
        for i in recent:
            if (begin <= i.stamp) and (i.stamp <= end):
                cache = Cache(i.datfile)
                if cache.tags:
                    tagstr = '<>tag:%s' % cache.tags
                else:
                    tagstr = ''
                fp.write('%s<>%s<>%s%s\n' % (i.stamp, i.id, i.datfile, tagstr))

    def do_update(self, path_info):
        self.header("text/plain")
        m = re.search(r"^update/(\w+)/(\d+)/(\w+)/([^:]*):(\d+)(.*)",path_info)
        if m is None:
            return False
        (datfile, stamp, id, host, port, path) = m.groups()
        host = self.get_remote_hostname(host)
        if not host:
            return
        node = Node(host=host, port=port, path=path)
        searchlist = SearchList()
        searchlist.append(node)
        searchlist.sync()
        lookuptable = LookupTable()
        lookuptable.add(datfile, node)
        lookuptable.sync()

        now = int(time())
        if (int(stamp) < now - config.update_range) or \
           (int(stamp) > now + config.update_range):
            return False
        rec = Record(datfile=datfile, idstr=stamp+"_"+id)
        updatelist = UpdateList()
        if rec in updatelist:
            return True
        else:
            queue = UpdateQueue()
            queue.append(datfile, stamp, id, node)
            queue.start()
            return True

# End of CGI
