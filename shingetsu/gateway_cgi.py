"""Gateway CGI methods.
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
import re
import csv
from io import StringIO
from operator import attrgetter
from time import time

from . import config
from . import forminput
from . import gateway
from .cache import *
from .tag import UserTagList
from .rss import RSS, make_rss1
from .util import opentext


class CGI(gateway.CGI):

    """Class for /gateway.cgi."""

    def run(self, environ, start_response):
        path = self.path_info()
        self.form = forminput.read(environ, environ['wsgi.input'])
        try:
            filter = self.form.getfirst('filter', '')
            tag = self.form.getfirst('tag', '')
            if filter:
                self.filter = filter.lower()
                self.str_filter = html.escape(filter, True)
            elif tag:
                self.tag = tag.lower()
                self.str_tag = html.escape(tag, True)
        except (re.error, UnicodeDecodeError):
            def errpage():
                yield self.header(self.message['regexp_error'],
                                  deny_robot=True)
                yield self.footer()
            return errpage()

        if config.server_name:
            self.host = config.server_name
        else:
            self.host = environ.get('HTTP_HOST', 'localhost')

        if not self.check_visitor():
            return self.print403()
        elif path == "motd":
            return self.print_motd()
        elif path == "mergedjs":
            return self.print_mergedjs()
        elif path == "rss":
            return self.print_rss()
        elif path == 'recent_rss':
            return self.print_recent_rss()
        elif path == "index":
            return self.print_index()
        elif path == "changes":
            return self.print_changes()
        elif path in ("recent", "new"):
            if (not self.isfriend) and (not self.isadmin):
                return self.print403()
            elif path == "recent":
                return self.print_recent()
            elif path == "new":
                def newpage():
                    yield self.header(self.message["new"], deny_robot=True)
                    yield self.print_new_element_form()
                    yield self.footer()
                return newpage()
            else:
                return self.print404()
        elif self.form.getfirst("cmd", "") == "new":
            return self.jump_new_file()
        elif path.startswith("csv"):
            return self.print_csv(path)
        elif re.search(r"^(thread)", path):
            m = re.search(r"^(thread)/?([^/]*)$", path)
            if m is None:
                return self.print_title()
            elif m.group(2) != "":
                uri = self.appli[m.group(1)] + self.sep + \
                      self.str_encode(m.group(2))
            elif environ.get("QUERY_STRING", "") != "":
                uri = self.appli[m.group(1)] + self.sep + \
                      environ["QUERY_STRING"]
            else:
                return self.print_title()

            return self.print302(uri)
        elif path == '':
            return self.print_title()
        else:
            return self.print404()

    def print_title(self):
        message = self.message
        cachelist = CacheList()
        cachelist.sort(key=lambda x: x.valid_stamp, reverse=True)
        now = int(time())
        output_cachelist = []
        for cache in cachelist:
            if now <= cache.valid_stamp + config.top_recent_range:
                output_cachelist.append(cache)
        self.http_header()
        var = {
            'cachelist': output_cachelist,
            'target': 'changes',
            'taglist': UserTagList(),
            'mch_url': self.mch_url(),
            'mch_categories': self.mch_categories()
        }
        def page():
            yield self.header(message['logo'] + ' - ' + message['description'])
            yield self.bytes(self.template('top', var))
            yield self.print_new_element_form()
            yield self.footer()
        return page()

    def print_index(self):
        """Print index page."""
        if self.str_filter:
            title = '%s : %s' % (self.message['index'], self.str_filter)
        else:
            title = self.message['index']
        cachelist = CacheList()
        cachelist.sort(key=attrgetter('velocity', 'count'), reverse=True)
        self.http_header()
        def page():
            yield self.header(title)
            yield self.print_paragraph(self.message['desc_index'])
            yield self.print_index_list(cachelist, "index")
        return page()

    def print_changes(self):
        """Print changes page."""
        if self.str_filter:
            title = '%s : %s' % (self.message['changes'], self.str_filter)
        else:
            title = self.message['changes']
        cachelist = CacheList()
        cachelist.sort(key=lambda x: x.valid_stamp, reverse=True)
        self.http_header()
        def page():
            yield self.header(title)
            yield self.print_paragraph(self.message['desc_changes'])
            yield self.print_index_list(cachelist, "changes")
        return page()

    def make_recent_cachelist(self):
        """Make dummy cachelist from recentlist."""
        recentlist = RecentList()[:]
        recentlist.sort(key=lambda x: x.stamp, reverse=True)
        cachelist = []
        check = []
        for rec in recentlist:
            if rec.datfile not in check:
                cache = Cache(rec.datfile)
                cache.recent_stamp = rec.stamp
                cachelist.append(cache)
                check.append(rec.datfile)
        return cachelist

    def print_recent(self):
        """Print changes page."""
        if self.str_filter:
            title = '%s : %s' % (self.message['recent'], self.str_filter)
        else:
            title = self.message['recent']
        cachelist = self.make_recent_cachelist()
        this.http_header()
        def page():
            yield self.header(title)
            yield self.print_paragraph(self.message['desc_recent'])
            yield self.print_index_list(cachelist, "recent",
                                        search_new_file=True)
        return page()

    def print_csv(self, path):
        """CSV output as API."""
        found = re.search(r"^csv/([^/]+)/(.+)", path)
        if found:
            target, cols = found.groups()
        else:
            return self.print404()
        cols = cols.split(",")
        if target == "index":
            cachelist = CacheList()
        elif target == "changes":
            cachelist = CacheList()
            cachelist.sort(key=lambda x: x.valid_stamp, reverse=True)
        elif target == "recent":
            if (not self.isfriend) and (not self.isadmin):
                return self.print403()
            cachelist = self.make_recent_cachelist()
        else:
            return self.print404()
        self.start_response('200 OK', [
            ('Content-Type', 'text/comma-separated-values; charset=UTF-8')
        ])
        buf = StringIO()
        writer = csv.writer(buf)
        for cache in cachelist:
            title = self.file_decode(cache.datfile)
            if cache.type in config.types:
                type = cache.type
                path = self.appli[cache.type] + self.sep + \
                       self.str_encode(title)
            else:
                type = ""
                path = ""
            row = []
            for c in cols:
                if c == "file":
                    row.append(cache.datfile)
                elif c == "stamp":
                    row.append(cache.valid_stamp)
                elif c == "date":
                    row.append(self.localtime(cache.valid_stamp))
                elif c == "path":
                    row.append(path)
                elif c == "uri":
                    if self.host and path:
                        row.append(config.gateway_protocol + "://" + self.host + path)
                    else:
                        row.append("")
                elif c == "type":
                    row.append(cache.type)
                elif c == "title":
                    row.append(title)
                elif c == "records":
                    row.append(len(cache))
                elif c == "size":
                    row.append(cache.size)
                elif c == 'tag':
                    row.append(str(cache.tags))
                elif c == 'sugtag':
                    row.append(str(cache.sugtags))
                else:
                    row.append("")
            writer.writerow(row)
        return self.body([str(buf)])

    def jump_new_file(self):
        def errpage(msg):
            yield self.header(self.message[msg], deny_robot=True)
            yield self.footer()

        if self.form.getfirst("link", "") == "":
            return errpage("null_title")
        elif re.search(r"[/\[\]<>]", self.form.getfirst("link", "")):
            return errpage("bad_title")
        elif self.form.getfirst("type", "") == "":
            return errpage("bad_type")
        elif self.form.getfirst("type", "") in config.types:
            tag = self.str_encode(self.form.getfirst('tag', ''))
            search = self.str_encode(self.form.getfirst('search_new_file', ''))
            return self.print302(
                self.appli[self.form.getfirst("type", "")] +
                self.sep +
                self.str_encode(self.form.getfirst("link", "")) +
                '?tag=' + tag +
                '&search_new_file=' + search)
        else:
            return self.print404()

    def rss_text_format(self, plain):
        buf = plain.replace("<br>", " ")
        buf = buf.replace("&", "&amp;")
        buf = re.sub(r'&amp;(#\d+|lt|gt|amp);', r'&\1;', buf)
        buf = buf.replace("<", "&lt;")
        buf = buf.replace(">", "&gt;")
        buf = buf.replace("\r", "")
        buf = buf.replace("\n", "")
        return buf

    def rss_html_format(self, plain, appli, path):
        title = self.str_decode(path)
        buf = self.html_format(plain, appli, title, absuri=True)
        if buf:
            buf = '<p>%s</p>' % buf
        return buf

    def print_rss(self):
        rss = RSS(encode = "UTF-8",
                  title = self.message["logo"],
                  parent = config.gateway_protocol + "://" + self.host,
                  uri = config.gateway_protocol + "://" + self.host
                                  + self.gateway_cgi + self.sep + "rss",
                  description = self.message["description"],
                  xsl = config.xsl)
        cachelist = CacheList()
        now = int(time())
        for cache in cachelist:
            if cache.valid_stamp + config.rss_range >= now:
                title = self.escape(self.file_decode(cache.datfile))
                path = self.appli[cache.type]+self.sep+self.str_encode(title)
                for r in cache:
                    if r.stamp + config.rss_range < now:
                        continue
                    r.load_body()
                    desc = self.rss_text_format(r.get("body", ""))
                    content = self.rss_html_format(r.get("body", ""),
                                                   self.appli[cache.type],
                                                   title)
                    attach = r.get('attach', '')
                    if attach:
                        suffix = r.get('suffix', '')
                        if not re.search(r'^[0-9A-Za-z]+$', suffix):
                            suffix = txt
                        content += '\n    <p>' + \
                            '<a href="%s://%s%s%s%s/%s/%d.%s">%d.%s</a></p>'\
                            % (config.gateway_protocol, self.host,
                               self.appli[cache.type], self.sep,
                               cache.datfile,
                               r.id, r.stamp, suffix,
                               r.stamp, suffix)
                    if cache.type == "thread":
                        permapath = "%s/%s" % (path[1:], r.id[:8])
                    else:
                        permapath = path[1:]
                    rss.append(
                        permapath,
                        date = r.stamp,
                        title = title,
                        creator = self.rss_text_format(r.get('name', '')),
                        subject = [str(i) for i in cache.tags],
                        description = desc,
                        content = content)
                    r.free()

        headers = [('Content-Type', 'text/xml; charset=UTF-8')]
        try:
            headers.append(('Last-Modified',
                            self.rfc822_time(rss[list(rss.keys())[0]].date)))
        except (IndexError, KeyError):
            pass
        self.start_response('200 OK', headers)
        return self.body([make_rss1(rss)])

    def print_recent_rss(self):
        rss = RSS(encode = 'UTF-8',
                  title = '%s - %s' % (
                          self.message['recent'], self.message['logo']),
                  parent = config.gateway_protocol + '://' + self.host,
                  uri = config.gateway_protocol + '://' + self.host
                                  + self.gateway_cgi + self.sep + 'recent_rss',
                  description = self.message['desc_recent'],
                  xsl = config.xsl)
        cachelist = self.make_recent_cachelist()
        for cache in cachelist:
            title = self.escape(self.file_decode(cache.datfile))
            tags = list(set([str(t) for t in cache.tags + cache.sugtags]))
            if cache.type not in self.appli:
                continue
            rss.append(
                self.appli[cache.type][1:]+self.sep+self.str_encode(title),
                date = cache.recent_stamp,
                title = title,
                subject = tags,
                content = html.escape(title))

        headers = [('Content-Type', 'text/xml; charset=UTF-8')]
        try:
            headers.append(('Last-Modified',
                            self.rfc822_time(rss[list(rss.keys())[0]].date)))
        except (IndexError, KeyError):
            pass
        self.start_response('200 OK', headers)
        return self.body([make_rss1(rss)])

    def print_mergedjs(self):
        self.start_response('200 OK', [
            ('Content-Type', 'application/javascript; charset=UTF-8'),
            ('Last-Modified', self.rfc822_time(self.jscache.mtime)),
        ])
        return self.body([self.jscache.script])

    def print_motd(self):
        self.start_response('200 OK', [
            ('Content-Type', 'text/plain;charset=UTF-8')])
        try:
            return self.body(opentext(config.motd))
        except IOError:
            self.stderr.write(config.motd + ": IOError\n")
            return []

# End of CGI
