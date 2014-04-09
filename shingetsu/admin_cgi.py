"""Saku Admin CGI methods.
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

import os
import cgi
import re
from random import random
from compatible import md5

import config
import gateway
from cache import *
from node import *
from tag import UserTagList


class CGI(gateway.CGI):

    """Class for /admin.cgi."""

    def run(self):
        path = self.path_info()
        form = cgi.FieldStorage(environ=self.environ, fp=self.stdin)

        cmd = form.getfirst('cmd', '')
        if not self.isadmin:
            self.print403()
            return
        elif (cmd == 'rdel') or (cmd == 'fdel'):
            rm_files = form.getlist('file')
            rm_records = form.getlist('record')
            if (not rm_files) or ((cmd == 'rdel') and (not rm_records)):
                self.print404()
            elif cmd == 'fdel':
                self.print_delete_file(rm_files)
            else:
                self.print_delete_record(rm_files[0], rm_records)
        elif ((cmd == 'xrdel') or (cmd == 'xfdel')) and \
             self.environ["REQUEST_METHOD"] == "POST" and \
             self.check_sid(form.getfirst("sid", "")):
            rm_files = form.getlist('file')
            rm_records = form.getlist('record')
            if (not rm_files) or ((cmd == 'xrdel') and (not rm_records)):
                self.print404()
            elif cmd == 'xfdel':
                self.do_delete_file(rm_files)
            else:
                self.do_delete_record(rm_files[0],
                                      rm_records,
                                      form.getfirst("dopost", ""),
                                      form)
        elif path == "status":
            self.print_status()
        elif path == 'edittag':
            datfile = form.getfirst('file', '')
            if datfile:
                self.print_edittag(datfile)
            else:
                print404()
        elif path == 'savetag':
            datfile = form.getfirst('file', '')
            tags = form.getfirst('tag', '')
            if datfile:
                self.save_tag(datfile, tags)
            else:
                print404()
        elif path.startswith("search"):
            self.print_search(path, form)
        else:
            self.print404()

    def make_sid(self):
        """Make admin sid for security."""
        sidfile = config.admin_sid
        r = ""
        for i in range(4):
            r += str(random())
        sid = md5.new(r).hexdigest()
        try:
            file(sidfile, "wb").write(sid + "\n")
        except IOError, err:
            self.stderr.write("%s: IOError: %s\n" % (sidfile, err))
        return sid

    def check_sid(self, sid):
        """Check admin sid for security."""
        sidfile = config.admin_sid
        try:
            saved = file(sidfile).read().strip()
            os.remove(sidfile)
            return sid == saved
        except IOError, err:
            self.stderr.write("%s: IOError: %s\n" % (sidfile, err))
            return False
        except OSError, err:
            self.stderr.write("%s: OSError: %s\n" % (sidfile, err))
            return sid == saved

    def print_delete_record(self, datfile, records):
        '''Delete record dialog.
        '''
        sid = self.make_sid()
        recs = [Record(datfile=datfile, idstr=r) for r in records]
        def getbody(rec):
            rec.load_body()
            recstr = unicode(cgi.escape(rec.recstr), 'utf-8', 'replace')
            rec.free()
            return recstr
        var = {
            'datfile': datfile,
            'records': recs,
            'sid': sid,
            'getbody': getbody,
        }
        self.header(self.message['del_record'], deny_robot=True)
        self.stdout.write(self.template('delete_record', var))
        self.footer()

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
        self.print302(next)

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
                contents.append(unicode(cgi.escape(rec.recstr), 'utf-8', 'replace'))
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
        self.header(self.message['del_file'], deny_robot=True)
        self.stdout.write(self.template('delete_file', var))
        self.footer()

    def do_delete_file(self, files):
        for c in files:
            cache = Cache(c)
            cache.remove()
        self.print302(self.gateway_cgi + self.sep + "changes")

    def print_search_form(self, query=''):
        var = {
            'query': query,
        }
        self.stdout.write(self.template('search_form', var))

    def print_search_result(self, query):
        str_query = unicode(cgi.escape(query, True), 'utf-8', 'replace')
        title = '%s : %s' % (self.message['search'], str_query)
        self.header(title, deny_robot=True)
        self.print_paragraph(self.message['desc_search'])
        self.print_search_form(str_query)
        try:
            query = re.compile(unicode(cgi.escape(query), 'utf-8'), re.I)
            cachelist = CacheList()
            result = cachelist.search(query)
            for i in cachelist:
                if i in result:
                    continue
                datfile = self.file_decode(i.datfile)
                if query.search(datfile):
                    result.append(i)
            result.sort(key=lambda x: x.stamp, reverse=True)
            self.print_index_list(result, footer=False)
        except (re.error, UnicodeDecodeError):
            self.print_paragraph(self.message['regexp_error'])
        self.footer()

    def print_search(self, path, form):
        query = form.getfirst('query', '')
        if query == '':
            query = path[len('search/'):]
        if query == '':
            query = self.environ.get('QUERY_STRING', '')
            query = self.str_decode(query)

        if query == '':
            self.header(self.message['search'], deny_robot=True)
            self.print_paragraph(self.message['desc_search'])
            self.print_search_form()
            self.footer()
        else:
            self.print_search_result(query)

    def print_status(self):
        nodelist = NodeList()
        searchlist = SearchList()
        cachelist = CacheList()
        records = 0
        size = 0
        for cache in cachelist:
            records += len(cache)
            size += cache.size
        myself = nodelist.myself()
        status = (('linked_nodes', len(nodelist)),
                  ('known_nodes', len(searchlist)),
                  ('files', len(cachelist)),
                  ('records', records),
                  ('cache_size', '%.1f%s' % (size/1024/1024,
                                             self.message['mb'])),
                  ('self_node', myself))
        node_status = (('linked_nodes', nodelist),
                       ('known_nodes', searchlist))
        var = {
            'status': status,
            'node_status': node_status,
        }
        self.header(self.message['status'], deny_robot=True)
        self.stdout.write(self.template('status', var))
        self.footer()

    def print_edittag(self, datfile):
        str_title = self.file_decode(datfile)
        cache = Cache(datfile)
        datfile = cgi.escape(datfile)
        if not cache.exists():
            print404()
            return
        var = {
            'datfile': datfile,
            'tags': str(cache.tags),
            'sugtags': cache.sugtags,
            'usertags': UserTagList(),
        }
        self.header('%s: %s' %
                        (self.message['edit_tag'], str_title),
                    deny_robot=True)
        self.stdout.write(self.template('edit_tag', var))
        self.footer()

    def save_tag(self, datfile, tags):
        cache = Cache(datfile)
        print cache
        if not cache.exists():
            print404()
            return
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
        self.print302(next)

# End of CGI
