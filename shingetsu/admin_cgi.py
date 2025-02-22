"""Saku Admin CGI methods.
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

import html
import os
import re
from random import random

from . import config
from . import gateway
from . import forminput
from .cache import *
from .node import *
from .tag import UserTagList
from .util import *


class CGI(gateway.CGI):

    """Class for /admin.cgi."""

    def run(self, environ, start_response):
        path = self.path_info()
        form = forminput.read(environ, environ['wsgi.input'])

        cmd = form.getfirst('cmd', '')
        if not self.isadmin:
            return self.print403()
        elif (cmd == 'rdel') or (cmd == 'fdel'):
            rm_files = form.getlist('file')
            rm_records = form.getlist('record')
            if (not rm_files) or ((cmd == 'rdel') and (not rm_records)):
                return self.print404()
            elif cmd == 'fdel':
                self.http_header()
                return self.print_delete_file(rm_files)
            else:
                self.http_header()
                return self.print_delete_record(rm_files[0], rm_records)
        elif ((cmd == 'xrdel') or (cmd == 'xfdel')) and \
             environ["REQUEST_METHOD"] == "POST" and \
             self.check_sid(form.getfirst("sid", "")):
            rm_files = form.getlist('file')
            rm_records = form.getlist('record')
            if (not rm_files) or ((cmd == 'xrdel') and (not rm_records)):
                self.http_header()
                return self.print404()
            elif cmd == 'xfdel':
                return self.do_delete_file(rm_files)
            else:
                return self.do_delete_record(
                    rm_files[0],
                    rm_records,
                    form.getfirst("dopost", ""),
                    form)
        elif path == "status":
            self.http_header()
            return self.print_status()
        elif path == 'edittag':
            datfile = form.getfirst('file', '')
            if datfile:
                self.http_header()
                return self.print_edittag(datfile)
            else:
                return print404()
        elif path == 'savetag':
            datfile = form.getfirst('file', '')
            tags = form.getfirst('tag', '')
            if datfile:
                self.save_tag(datfile, tags)
            else:
                return print404()
        elif path.startswith("search"):
            self.http_header()
            return self.print_search(path, form)
        else:
            return self.print404()

    def make_sid(self):
        """Make admin sid for security."""
        sidfile = config.admin_sid
        r = ""
        for i in range(4):
            r += str(random())
        sid = md5digest(r)
        try:
            opentext(sidfile, 'w').write(sid + '\n')
        except IOError as err:
            self.stderr.write("%s: IOError: %s\n" % (sidfile, err))
        return sid

    def check_sid(self, sid):
        """Check admin sid for security."""
        sidfile = config.admin_sid
        try:
            saved = open(sidfile).read().strip()
            os.remove(sidfile)
            return sid == saved
        except IOError as err:
            self.stderr.write("%s: IOError: %s\n" % (sidfile, err))
            return False
        except OSError as err:
            self.stderr.write("%s: OSError: %s\n" % (sidfile, err))
            return sid == saved

    def print_delete_record(self, datfile, records):
        '''Delete record dialog.
        '''
        sid = self.make_sid()
        recs = [Record(datfile=datfile, idstr=r) for r in records]
        def getbody(rec):
            rec.load_body()
            recstr = html.escape(rec.recstr)
            rec.free()
            return recstr
        var = {
            'datfile': datfile,
            'records': recs,
            'sid': sid,
            'getbody': getbody,
        }
        yield self.header(self.message['del_record'], deny_robot=True)
        yield self.bytes(self.template('delete_record', var))
        yield self.footer()

    def do_delete_record(self, datfile, records, dopost="", form=None):
        for type in config.types:
            title = self.str_encode(self.file_decode(datfile))
            if datfile.startswith(type + "_"):
                next = self.appli[type] + self.sep + title
                break
        else:
            next = self.root
        cache = Cache(datfile)
        for r in records:
            rec = Record(datfile=datfile, idstr=r)
            cache.size -= rec.size()
            removed = rec.remove()
            if removed:
                cache.count -= 1
                if dopost != '':
                    cache.sync_status()
                    self.post_delete_message(cache, rec, form)
                    break
        if not dopost:
            cache.sync_status()
        return self.print302(next)

    def post_delete_message(self, cache, rec, form):
        """Post delete message to other nodes."""
        stamp = self.error_time()

        body = {}
        for key in ("name", "body"):
            if form.getfirst(key, "") != "":
                body[key] = self.escape(form.getfirst(key, ""))
        body["remove_stamp"] = str(rec.stamp)
        body["remove_id"] = rec.id
        passwd = form.getfirst("passwd", "")
        id = rec.build(stamp, body, passwd=passwd)
        cache.add_data(rec)
        cache.sync_status()

        updatelist = UpdateList()
        updatelist.append(rec)
        updatelist.sync()
        recentlist = RecentList()
        recentlist.append(rec)
        recentlist.sync()
        nodelist = NodeList()
        nodelist.tell_update(cache, stamp=stamp, id=id)

    def print_delete_file(self, files):
        '''Delete file dialog.
        '''
        sid = self.make_sid()
        files = [Cache(c) for c in files]
        def gettitle(cache):
            for type in config.types:
                if cache.datfile.startswith(type + '_'):
                    return self.file_decode(cache.datfile)
            return cache.datfile
        def getcontents(cache):
            contents = []
            for rec in cache:
                rec.load_body()
                contents.append(html.escape(rec.recstr))
                rec.free()
                if (len(contents) > 2):
                    return contents
            return contents
        var = {
            'sid': sid,
            'files': files,
            'gettitle': gettitle,
            'getcontents': getcontents,
        }
        yield self.header(self.message['del_file'], deny_robot=True)
        yield self.bytes(self.template('delete_file', var))
        yield self.footer()

    def do_delete_file(self, files):
        for c in files:
            cache = Cache(c)
            cache.remove()
        return self.print302(self.gateway_cgi + self.sep + "changes")

    def print_search_form(self, query=''):
        var = {
            'query': query,
        }
        return self.bytes(self.template('search_form', var))

    def print_search_result(self, query):
        str_query = html.escape(query, True)
        title = '%s : %s' % (self.message['search'], str_query)
        yield self.header(title, deny_robot=True)
        yield self.print_paragraph(self.message['desc_search'])
        yield self.print_search_form(str_query)
        try:
            query = re.compile(html.escape(query), re.I)
            cachelist = CacheList()
            result = cachelist.search(query)
            for i in cachelist:
                if i in result:
                    continue
                datfile = self.file_decode(i.datfile)
                if query.search(datfile):
                    result.append(i)
            result.sort(key=lambda x: x.stamp, reverse=True)
            yield self.print_index_list(result, footer=False)
        except (re.error, UnicodeDecodeError):
            yield self.print_paragraph(self.message['regexp_error'])
        yield self.footer()

    def print_search(self, path, form):
        query = form.getfirst('query', '')
        if query == '':
            query = path[len('search/'):]
        if query == '':
            query = self.environ.get('QUERY_STRING', '')
            query = self.str_decode(query)

        if query == '':
            yield self.header(self.message['search'], deny_robot=True)
            yield self.print_paragraph(self.message['desc_search'])
            yield self.print_search_form()
            yield self.footer()
        else:
            yield self.print_search_result(query)

    def print_status(self):
        nodelist = NodeList()
        searchlist = SearchList()
        cachelist = CacheList()
        records = 0
        size = 0
        for cache in cachelist:
            records += len(cache)
            size += cache.size
        myself4, myself6 = nodelist.myself()
        status = (('linked_nodes', len(nodelist)),
                  ('known_nodes', len(searchlist)),
                  ('files', len(cachelist)),
                  ('records', records),
                  ('cache_size', '%.1f%s' % (size/1024/1024,
                                             self.message['mb'])),
                  ('node_version', config.version),
                  ('self_node_ipv4', myself4),
                  ('self_node_ipv6', myself6))
        node_status = (('linked_nodes', nodelist),
                       ('known_nodes', searchlist))
        var = {
            'status': status,
            'node_status': node_status,
        }
        yield self.header(self.message['status'], deny_robot=True)
        yield self.bytes(self.template('status', var))
        yield self.footer()

    def print_edittag(self, datfile):
        str_title = self.file_decode(datfile)
        cache = Cache(datfile)
        datfile = html.escape(datfile)
        if not cache.exists():
            return self.print404()
        var = {
            'datfile': datfile,
            'tags': str(cache.tags),
            'sugtags': cache.sugtags,
            'usertags': UserTagList(),
        }
        yield self.header('%s: %s' %
                          (self.message['edit_tag'], str_title),
                          deny_robot=True)
        yield self.bytes(self.template('edit_tag', var))
        yield self.footer()

    def save_tag(self, datfile, tags):
        cache = Cache(datfile)
        if not cache.exists():
            return self.print404()
        taglist = tags.split()
        cache.tags.update(taglist)
        cache.tags.sync()
        user_tag_list = UserTagList()
        user_tag_list.add(taglist)
        user_tag_list.sync()
        for type in config.types:
            title = self.str_encode(self.file_decode(datfile))
            if datfile.startswith(type + "_"):
                next = self.appli[type] + self.sep + title
                break
        else:
            next = self.root
        return self.print302(next)

# End of CGI
