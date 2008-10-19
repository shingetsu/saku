'''Saku Mobile Gateway.
'''
#
# Copyright (c) 2007,2008 shinGETsu Project.
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
# $Id$
#

import re
import cgi
from time import time
from compatible import md5

import config
import gateway
import basecgi
import spam
from tmpaddr import TmpAddress
from cache import *
from node import NodeList
from template import Template
from updatequeue import UpdateQueue

__version__ = "$Revision$"

class BodyFilter(basecgi.BodyFilter):
    def write(self, msg):
        '''Wrapper for sys.stdout.write().

        Argument msg must be unicode string or utf-8 string.
        '''
        if not isinstance(msg, unicode):
            msg = unicode(str(msg), 'utf-8', 'replace')
        msg = msg.encode('shift-jis', 'replace')
        basecgi.BodyFilter.write(self, msg)
# End of BodyFilter


class CGI(gateway.CGI):

    def run(self):
        self.stdout = BodyFilter(self.environ, self.stdout)
        self.form = cgi.FieldStorage(environ=self.environ, fp=self.stdin)
        self.host = config.server_name
        self.message = gateway.Message(config.file_dir + '/message-ja.txt')
        cmd = self.form.getfirst('cmd', '')
        title = self.form.getfirst('thread', '')
        try:
            page = int(self.form.getfirst('page', '0'))
        except ValueError:
            page = 0
        id = self.form.getfirst('id', '')
        self.obj_template.set_defaults({'message': self.message})

        if not self.check_visitor():
            self.print403()
            return
        elif cmd == 'motd':
            self.print_motd()
        elif cmd == 'changes':
            self.print_changes()
        elif cmd == 'post' and \
             self.form.getfirst('file', '').startswith('thread_') and \
             self.environ['REQUEST_METHOD'] == 'POST':
            id = self.do_post('', self.form)
            if not id:
                return
            datfile = self.form.getfirst("file", "")
            title = self.str_encode(self.file_decode(datfile))
            self.print302('%s?thread=%s#bottom' % (self.mobile_cgi, title))
            return
        elif title:
            self.print_thread(title, id=id, page=page)
        else:
            self.print_title()

    def header(self, title='', rss='', cookie=None, deny_robot=False):
        '''Print CGI and HTTP header.
        '''
        if rss == '':
            rss = self.gateway_cgi + self.sep + 'rss'
        message = self.message
        var = {
            'title': title,
            'rss': rss,
            'deny_robot': deny_robot,
        }
        self.stdout.write(self.template('mobile_header', var))

    def footer(self):
        self.stdout.write(self.template('mobile_footer'))

    def print_jump(self, next):
        '''Print jump anchor.'''
        var = {
            'next': next,
        }
        self.stdout.write(self.template('mobile_jump', var))

    def make_list_item(self, cache, remove=True, target='changes'):
        title = self.file_decode(cache.datfile)
        str_title = self.str_encode(title)
        var = {
            'cache': cache,
            'title': title,
            'str_title': str_title,
        }
        return self.template('mobile_list_item', var)

    def print_index_list(self, cachelist, target="", footer=True):
        """Print index list."""
        for type in config.types:
            self.stdout.write('<ul id="%s_index">\n' % type)
            for cache in cachelist:
                if cache.type == type:
                    try:
                        buf = self.make_list_item(cache, target=target)
                        if buf:
                            self.stdout.write(buf)
                    except KeyError:
                        pass
            self.stdout.write("</ul>\n")
        if footer:
            self.footer()

    def print_title(self):
        message = self.message
        cachelist = CacheList()
        cachelist.sort(lambda a,b: cmp(b.valid_stamp, a.valid_stamp))
        now = int(time())
        output_cachelist = []
        for cache in cachelist:
            if now <= cache.valid_stamp + config.top_recent_range:
                output_cachelist.append(cache)
        var = {
            'cachelist': output_cachelist,
            'target': 'changes',
            'make_list_item': self.make_list_item,
        }
        self.header(message['logo'] + ' - ' + message['description'])
        self.stdout.write(self.template('mobile_top', var))
        self.footer()

    def print_changes(self):
        """Print changes page."""
        title = self.message['changes']
        self.header(title)
        cachelist = CacheList()
        cachelist.sort(lambda a,b: cmp(b.valid_stamp, a.valid_stamp))
        self.print_index_list(cachelist, "changes")

    def print_motd(self):
        self.header(self.message['agreement'])
        self.stdout.write('<pre>')
        try:
            f = file(config.motd)
            for line in f:
                self.stdout.write(unicode(line, 'utf-8'))
            f.close()
        except IOError:
            self.stderr.write(config.motd + ": IOError\n")
        self.stdout.write('</pre>')
        self.footer()

    def print_page_navi(self, page, cache, path, str_path, id):
        var = {
            'page': page,
            'cache': cache,
            'path': path,
            'str_path': str_path,
            'id': id,
            'archive_uri': self.archive_uri,
        }
        self.stdout.write(self.template('mobile_page_navi', var))

    def print_thread(self, path, id='', page=0):
        str_path = self.str_encode(path)
        file_path = self.file_encode('thread', path)
        self.archive_uri = '%s%s/' % (config.archive_uri,
                                      md5.new(file_path).hexdigest())
        cache = Cache(file_path)
        if cache.has_record():
            pass
        elif self.check_get_cache():
            self.get_cache(cache)
        else:
            self.print404(id=id)
            return
        ids = cache.keys()
        self.header(path)
        form = self.form
        self.stdout.write('<p id="pagenavi">\n')
        self.stdout.write('<a href="%s" accesskey="0">[0]%s</a> | ' %
                          (self.mobile_cgi, self.message['top']))
        self.stdout.write(
            '  <a href="#bottom" id="top" accesskey="8">[8]%s</a>\n' %
            self.message['bottom_of_page'])
        self.print_page_navi(page, cache, path, str_path, id)
        self.stdout.write('</p>\n<div id="records">\n')
        page_size = config.mobile_page_size
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
                self.print_record(cache, rec, path, str_path, id)
                printed = True
            rec.free()
        self.stdout.write("</div>\n")
        if id and (not printed) and config.archive_uri:
            self.print_jump('%s%s.html' % (self.archive_uri, id))
        escaped_path = cgi.escape(path)
        escaped_path = re.sub(r'  ', '&nbsp;&nbsp;', escaped_path)
        var = {
            'cache': cache,
        }
        self.stdout.write(self.template('mobile_thread_top', var))
        if len(cache):
            self.print_page_navi(page, cache, path, str_path, id)
            self.stdout.write('</p>\n')
        self.print_post_form(cache, id=id)
        self.remove_file_form(cache, escaped_path)
        self.footer()

    def res_anchor(self, id, appli, title, absuri=False):
        title = self.str_encode(title)
        return '<a href="%s?thread=%s&amp;id=%s" class="innerlink">' % \
               (self.mobile_cgi, title, id)

    def bracket_link(self, link, appli, absuri=False):
        """Encode bracket string to link.

        See WikiWikiWeb.
        """
        if absuri:
            prefix = 'http://' + self.host
        else:
            prefix = ''
        m = re.search(r"^/(thread)/([^/]+)/([0-9a-f]{8})$", link)
        if m is not None:
            uri = '%s?thread=%s&amp;id=%s' % \
                  (self.mobile_cgi, self.str_encode(m.group(2)), m.group(3))
            return '<a href="' + uri + '">[[' + link + ']]</a>'

        m = re.search(r"^/(thread)/([^/]+)$", link)
        if m is not None:
            uri = prefix + self.appli[m.group(1)] + self.sep + \
                  self.str_encode(m.group(2))
            return '<a href="' + uri + '">[[' + link + ']]</a>'

        m = re.search(r"^([^/]+)/([0-9a-f]{8})$", link)
        if m is not None:
            uri = prefix + appli + self.sep + \
                  self.str_encode(m.group(1)) + \
                  '/' + m.group(2)
            return '<a href="' + uri + '">[[' + link + ']]</a>'

        m = re.search(r"^([^/]+)$", link)
        if m is not None:
            uri = prefix + appli + self.sep + \
                  self.str_encode(m.group(1))
            return '<a href="' + uri + '">[[' + link + ']]</a>'

        return "[[" + link + "]]"

    def print_record(self, cache, rec, path, str_path, id=''):
        if 'attach' in rec:
            attach_file = rec.attach_path()
            attach_size = rec.attach_size(attach_file)
            suffix = rec.get('suffix', '')
            if not re.search('^[0-9A-Za-z]+$', suffix):
                suffix = 'txt'
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
            'res_mode': id != '',
        }
        self.stdout.write(self.template('mobile_record', var))

    def print_post_form(self, cache, id=''):
        tmpaddr = TmpAddress().getaddress()
        if id:
            id_http = '&gt;&gt;%s\n' % self.escape(id)
            id_smtp = self.str_encode('>>' + id)
        else:
            id_http = ''
            id_smtp = ''
        ua = self.environ.get('HTTP_USER_AGENT', '')
        mail_message_smtp = self.message['mail_message']
        if 'SoftBank' not in ua:
            mail_message_smtp = \
                unicode(mail_message_smtp, 'utf-8', 'replace'). \
                encode('shift-jis', 'replace')
        mail_message_smtp = self.str_encode(mail_message_smtp)
        var = {
            'cache': cache,
            'id': id,
            'id_http': id_http,
            'id_smtp': id_smtp,
            'mail_message_smtp': mail_message_smtp,
            'tmpaddr': tmpaddr,
        }
        self.stdout.write(self.template('mobile_post_form', var))

    def do_post(self, path, form):
        """Post article."""
        if form.getfirst("error", "") != "":
            stamp = self.error_time()
        else:
            stamp = int(time())

        body = {}
        for key in ("base_stamp", "base_id", "name", "mail", "body"):
            value = form.getfirst(key, "")
            if value != "":
                value = unicode(value, 'shift-jis', 'replace')
                value = value.encode('utf-8', 'replace')
                body[key] = self.escape(value)

        if not body:
            self.header(self.message["null_article"], deny_robot=True)
            self.footer()
            return None

        cache = Cache(form.getfirst("file"))
        rec = Record(datfile=cache.datfile)
        id = rec.build(stamp, body)

        if len(rec.recstr) > config.record_limit*1024:
            self.header(self.message['big_file'], deny_robot=True)
            self.footer()
            return None
        elif spam.check(rec.recstr):
            self.header(self.message['spam'], deny_robot=True)
            self.footer()
            return None

        if cache.exists():
            cache.add_data(rec)
            cache.sync_status()
        else:
            self.print404()
            return None

        if form.getfirst("dopost", "") != "":
            queue = UpdateQueue()
            queue.append(cache.datfile, stamp, id, None)
            queue.start()

        return id[:8]

# End of CGI
