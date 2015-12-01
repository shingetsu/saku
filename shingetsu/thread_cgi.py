'''Saku Thread CGI methods.
'''
#
# Copyright (c) 2005-2015 shinGETsu Project.
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

import cgi
import mimetypes
import re
import time
from http.cookies import SimpleCookie

from . import attachutil
from . import config
from . import gateway
from .cache import *
from .tag import UserTagList

import os.path


class CGI(gateway.CGI):

    """Class for /thread.cgi."""

    appli_type = "thread"

    def run(self):
        path = self.path_info()
        if config.server_name:
            self.host = config.server_name
        else:
            self.host = self.environ.get('HTTP_HOST', 'localhost')

        if not self.check_visitor():
            self.print403()
            return
        found = re.search(r'^([^/]+)/?$', path)
        if found:
            path = found.group(1)
            self.print_thread(path)
            return
        found = re.search(r'^([^/]+)/([0-9a-f]{8})$', path)
        if found:
            path, id = found.groups()
            self.print_thread(path, id=id)
            return
        found = re.search(r'^([^/]+)/p([0-9]+)$', path)
        if found:
            path, page = found.groups()
            try:
                self.print_thread(path, page=int(page))
            except ValueError:
                self.print_thread(path)
            return

        #found = re.search(r"^(thread_[0-9A-F]+)/([0-9a-f]{32})/(\d+)\.(\d+)x(\d+)\.(.*)",
        found = re.search(r"^(thread_[0-9A-F]+)/([0-9a-f]{32})/s(\d+)\.(\d+x\d+)\.(.*)",
                          path)
        if found:
            (datfile, stamp, id, thumbnail_size, suffix) = found.groups()
            self.print_attach(datfile, stamp, id, suffix, thumbnail_size)
            return

        found = re.search(r"^(thread_[0-9A-F]+)/([0-9a-f]{32})/(\d+)\.(.*)",
                          path)
        if found:
            (datfile, stamp, id, suffix) = found.groups()
            self.print_attach(datfile, stamp, id, suffix, None)
            return

        form = cgi.FieldStorage(environ=self.environ, fp=self.stdin)
        if form.getfirst("cmd", "") == "post" and \
           form.getfirst("file", "").startswith("thread_") and \
           self.environ["REQUEST_METHOD"] == "POST":
            id = self.do_post(path, form)
            if not id:
                return
            datfile = form.getfirst("file", "")
            title = self.str_encode(self.file_decode(datfile))
            self.print302(self.thread_cgi + self.sep + title + "#r" + id)
            return

        self.print404()

    def setcookie(self, cache, access):
        now = int(time.time())
        expires = time.strftime('%a, %d %b %Y %H:%M:%S GMT',
                                time.gmtime(now + config.save_cookie))
        path = self.thread_cgi + '/' + \
                  self.str_encode(self.file_decode(cache.datfile))
        cookie = SimpleCookie()
        cookie['access'] = str(now)
        cookie['access']['path'] = path
        cookie['access']['expires'] = expires
        if access:
            cookie['tmpaccess'] = str(access)
            cookie['tmpaccess']['path'] = '/'
        return cookie

    def print_page_navi(self, page, cache, path, str_path, id):
        size = config.thread_page_size
        first = len(cache) // size
        if len(cache) % size:
            first += 1
        var = {
            'page': page,
            'cache': cache,
            'path': path,
            'str_path': str_path,
            'id': id,
            'first': first,
        }
        self.stdout.write(self.template('page_navi', var))

    def print_tags(self, cache):
        for tags, classname, target in ((cache.tags, 'tags', 'changes'),):
            if not (self.isadmin or self.isfriend):
                target = 'changes'
            var = {
                'cache': cache,
                'tags': tags,
                'classname': classname,
                'target': target,
            }
            self.stdout.write(self.template('thread_tags', var))

    def print_thread(self, path, id='', page=0):
        str_path = self.str_encode(path)
        file_path = self.file_encode('thread', path)
        form = cgi.FieldStorage(environ=self.environ, fp=self.stdin)
        cache = Cache(file_path)
        if id and form.getfirst('ajax'):
            self.print_thread_ajax(path, id, form)
            return
        if cache.has_record():
            pass
        elif self.check_get_cache():
            if not form.getfirst('search_new_file', ''):
                cache.standby_directories()
                self.unlock()
            else:
                self.get_cache(cache)
        else:
            self.print404(id=id)
            return
        if config.use_cookie and len(cache) and (not id) and (not page):
            access = None
            try:
                cookie = SimpleCookie(self.environ.get('HTTP_COOKIE', ''))
                if 'access' in cookie:
                    access = cookie['access'].value
            except CookieError as err:
                self.stderr.write('%s\n' % err)
            newcookie = self.setcookie(cache, access)
        else:
            newcookie = ''
        rss = self.gateway_cgi + '/rss'
        self.header(path, rss=rss, cookie=newcookie)
        tags = form.getfirst('tag', '').strip().split()
        if self.isadmin and tags:
            cache.tags.add(tags)
            cache.tags.sync()
            user_tag_list = UserTagList()
            user_tag_list.add(tags)
            user_tag_list.sync()
        self.print_tags(cache)
        lastrec = None
        ids = list(cache.keys())
        if len(cache) and (not page) and (not id) and (not ids):
            lastrec = cache[ids[-1]]
        var = {
            'path': path,
            'str_path': str_path,
            'cache': cache,
            'lastrec': lastrec,
            'res_anchor': self.res_anchor,
        }
        self.stdout.write(self.template('thread_top', var))
        self.print_page_navi(page, cache, path, str_path, id)
        self.stdout.write('</p>\n<dl id="records">\n')
        page_size = config.thread_page_size
        if id:
            inrange = ids
        elif page:
            inrange = ids[-page_size*(page+1):-page_size*page]
        else:
            inrange = ids[-page_size*(page+1):]
        printed = False
        for k in inrange:
            rec = cache[k]
            if ((not id) or (rec.id[:8] == id)) and rec.load_body():
                self.print_record(cache, rec, path, str_path)
                printed = True
            rec.free()
        self.stdout.write("</dl>\n")
        escaped_path = cgi.escape(path)
        escaped_path = re.sub(r'  ', '&nbsp;&nbsp;', escaped_path)
        var = {
            'cache': cache,
        }
        self.stdout.write(self.template('thread_bottom', var))
        if len(cache):
            self.print_page_navi(page, cache, path, str_path, id)
            self.stdout.write('</p>\n')
        self.print_post_form(cache)
        self.print_tags(cache)
        self.remove_file_form(cache, escaped_path)
        self.footer(menubar=self.menubar('bottom', rss))

    def print_thread_ajax(self, path, id, form):
        self.stdout.write('Content-Type: text/html; charset=UTF-8\n\n')
        str_path = self.str_encode(path)
        file_path = self.file_encode('thread', path)
        cache = Cache(file_path)
        if not cache.has_record():
            return
        self.stdout.write('<dl>\n')
        for k in list(cache.keys()):
            rec = cache[k]
            if ((not id) or (rec.id[:8] == id)) and rec.load_body():
                self.print_record(cache, rec, path, str_path)
            rec.free()
        self.stdout.write('</dl>\n')

    def print_record(self, cache, rec, path, str_path):
        thumbnail_size = None
        if 'attach' in rec:
            attach_file = rec.attach_path()
            attach_size = rec.attach_size(attach_file)
            suffix = rec.get('suffix', '')
            if not re.search('^[0-9A-Za-z]+$', suffix):
                suffix = 'txt'
            (type, null) = mimetypes.guess_type("test." + suffix)
            if type is None:
                type = "text/plain"
            if attachutil.is_valid_image(type, attach_file):
                thumbnail_size = config.thumbnail_size
        else:
            attach_file = None
            attach_size = None
            suffix = None
        if 'body' in rec:
            body = rec['body']
        else:
            body = ''
        body = self.html_format(body, self.thread_cgi, path)
        var = {
            'cache': cache,
            'rec': rec,
            'sid': rec['id'][:8],
            'path': path,
            'str_path': str_path,
            'attach_file': attach_file,
            'attach_size': attach_size,
            'suffix': suffix,
            'body': body,
            'res_anchor': self.res_anchor,
            'thumbnail': thumbnail_size,
        }
        self.stdout.write(self.template('record', var))

    def print_post_form(self, cache):
        suffixes = list(mimetypes.types_map.keys())
        suffixes.sort()
        var = {
            'cache': cache,
            'suffixes': suffixes,
            'limit': config.record_limit * 3 // 4,
        }
        self.stdout.write(self.template('post_form', var))

    def print_attach(self, datfile, id, stamp, suffix, thumbnail_size=None):
        """Print attachment."""
        cache = Cache(datfile)
        (type, null) = mimetypes.guess_type("test." + suffix)
        if type is None:
            type = "text/plain"
        if cache.has_record():
            pass
        elif self.check_get_cache():
            self.get_cache(cache)
        else:
            self.print404(cache)
            return
        rec = Record(datfile=cache.datfile, idstr=stamp+'_'+id)
        if not rec.exists():
            self.print404(cache)
            return
        attach_file = rec.attach_path(suffix=suffix, thumbnail_size=thumbnail_size)
        if config.thumbnail_size is not None and not os.path.isfile(attach_file):
            if config.force_thumbnail or thumbnail_size == config.thumbnail_size:
                rec.make_thumbnail(suffix=suffix, thumbnail_size=thumbnail_size)
        if attach_file is not None:
            size = rec.attach_size(suffix=suffix, thumbnail_size=thumbnail_size)
            self.stdout.write(
                "Content-Type: " + type + "\n" +
                "Last-Modified: " + self.rfc822_time(stamp) + "\n" +
                "Content-Length: " + str(size) + "\n" +
                "X-Content-Type-Options: nosniff\n")
            if attachutil.seem_html(suffix):
                self.stdout.write("Content-Disposition: attachment\n")
            self.stdout.write("\n")
            try:
                f = open(attach_file, "rb")
                buf = f.read(1024)
                while (buf != b''):
                    self.stdout.write(buf)
                    buf = f.read(1024)
                f.close()
            except IOError:
                self.print404(cache)
