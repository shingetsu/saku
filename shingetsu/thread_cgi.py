'''Saku Thread CGI methods.
'''
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
import mimetypes
import re

from . import attachutil
from . import config
from . import forminput
from . import gateway
from .cache import *
from .tag import UserTagList

import os.path


class CGI(gateway.CGI):

    """Class for /thread.cgi."""

    appli_type = "thread"

    def run(self, environ, start_response):
        path = self.path_info()
        if config.server_name:
            self.host = config.server_name
        else:
            self.host = environ.get('HTTP_HOST', 'localhost')

        if not self.check_visitor():
            return self.print403()
        found = re.search(r'^([^/]+)/?$', path)
        if found:
            path = found.group(1)
            self.http_header()
            return self.print_thread(path)
        found = re.search(r'^([^/]+)/([0-9a-f]{8})$', path)
        if found:
            path, id = found.groups()
            self.http_header()
            return self.print_thread(path, id=id)
        found = re.search(r'^([^/]+)/p([0-9]+)$', path)
        if found:
            path, page = found.groups()
            self.http_header()
            try:
                return self.print_thread(path, page=int(page))
            except ValueError:
                return self.print_thread(path)

        found = re.search(r"^(thread_[0-9A-F]+)/([0-9a-f]{32})/s(\d+)\.(\d+x\d+)\.(.*)",
                          path)
        if found:
            (datfile, stamp, id, thumbnail_size, suffix) = found.groups()
            return self.print_attach(datfile, stamp, id, suffix, thumbnail_size)

        found = re.search(r"^(thread_[0-9A-F]+)/([0-9a-f]{32})/(\d+)\.(.*)",
                          path)
        if found:
            (datfile, stamp, id, suffix) = found.groups()
            return self.print_attach(datfile, stamp, id, suffix, None)

        form = forminput.read(environ, environ['wsgi.input'])
        if form.getfirst("cmd", "") == "post" and \
           form.getfirst("file", "").startswith("thread_") and \
           environ["REQUEST_METHOD"] == "POST":
            return self.do_post(path, form)

        return self.print404()

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
        return self.bytes(self.template('page_navi', var))

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
            return self.bytes(self.template('thread_tags', var))

    def print_thread(self, path, id='', page=0):
        str_path = self.str_encode(path)
        file_path = self.file_encode('thread', path)
        form = forminput.read(self.environ, self.environ['wsgi.input'])
        cache = Cache(file_path)
        if id and form.getfirst('ajax'):
            for b in self.print_thread_ajax(path, id, form):
                yield b
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
            for b in self.print404(id=id):
                yield b
            return
        rss = self.gateway_cgi + '/rss'
        yield self.header(path, rss=rss)
        tags = form.getfirst('tag', '').strip().split()
        if self.isadmin and tags:
            cache.tags.add(tags)
            cache.tags.sync()
            user_tag_list = UserTagList()
            user_tag_list.add(tags)
            user_tag_list.sync()
        yield self.print_tags(cache)
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
        yield self.bytes(self.template('thread_top', var))
        yield self.print_page_navi(page, cache, path, str_path, id)
        yield self.bytes('</p>\n<dl id="records">\n')
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
                yield self.print_record(cache, rec, path, str_path)
                printed = True
            rec.free()
        yield self.bytes("</dl>\n")
        escaped_path = html.escape(path)
        escaped_path = re.sub(r'  ', '&nbsp;&nbsp;', escaped_path)
        var = {
            'cache': cache,
        }
        yield self.bytes(self.template('thread_bottom', var))
        if len(cache):
            yield self.print_page_navi(page, cache, path, str_path, id)
            yield self.bytes('</p>\n')
        yield self.print_post_form(cache)
        yield self.print_tags(cache)
        yield self.remove_file_form(cache, escaped_path)
        yield self.footer(menubar=self.menubar('bottom', rss))

    def print_thread_ajax(self, path, id, form):
        self.start_response('200 OK', [
            ('Content-Type', 'text/html; charset=UTF-8')
        ])
        str_path = self.str_encode(path)
        file_path = self.file_encode('thread', path)
        cache = Cache(file_path)
        if not cache.has_record():
            return
        yield self.bytes('<dl>\n')
        for k in list(cache.keys()):
            rec = cache[k]
            if ((not id) or (rec.id[:8] == id)) and rec.load_body():
                yield self.print_record(cache, rec, path, str_path)
            rec.free()
        yield self.bytes('</dl>\n')

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
        return self.bytes(self.template('record', var))

    def print_post_form(self, cache):
        suffixes = list(mimetypes.types_map.keys())
        suffixes.sort()
        var = {
            'cache': cache,
            'suffixes': suffixes,
            'limit': config.record_limit * 3 // 4,
        }
        return self.bytes(self.template('post_form', var))

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
            return self.print404(cache)
        rec = Record(datfile=cache.datfile, idstr=stamp+'_'+id)
        if not rec.exists():
            return self.print404(cache)
        attach_file = rec.attach_path(suffix=suffix, thumbnail_size=thumbnail_size)
        if config.thumbnail_size is not None and not os.path.isfile(attach_file):
            if config.force_thumbnail or thumbnail_size == config.thumbnail_size:
                rec.make_thumbnail(suffix=suffix, thumbnail_size=thumbnail_size)
        if attach_file is not None:
            size = rec.attach_size(suffix=suffix, thumbnail_size=thumbnail_size)
            headers = [
                ("Content-Type", type),
                ("Last-Modified", self.rfc822_time(stamp)),
                ("Content-Length", str(size)),
                ("X-Content-Type-Options", "nosniff"),
            ]
            if attachutil.seem_html(suffix):
                headers.append(("Content-Disposition", "attachment"))
            self.start_response('200 OK', headers)
            try:
                return self.environ['wsgi.file_wrapper'](f, 1024)
            except IOError:
                return self.print404(cache)
