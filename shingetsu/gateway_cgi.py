"""Gateway CGI methods.
"""
#
# Copyright (c) 2005-2013 shinGETsu Project.
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
import csv
from time import time

import config
import gateway
from cache import *
from tag import UserTagList
from rss import RSS, make_rss1

__version__ = "$Revision$"


class CGI(gateway.CGI):

    """Class for /gateway.cgi."""

    def run(self):
        path = self.path_info()
        self.form = cgi.FieldStorage(environ=self.environ, fp=self.stdin)
        try:
            filter = self.form.getfirst('filter', '')
            tag = self.form.getfirst('tag', '')
            if filter:
                self.filter = re.compile(unicode(filter, 'utf-8'), re.I)
                self.str_filter = cgi.escape(filter, True)
            elif tag:
                self.tag = tag.lower()
                self.str_tag = cgi.escape(tag, True)
        except (re.error, UnicodeDecodeError):
            self.header(self.message['regexp_error'], deny_robot=True)
            self.footer()
            return

        if config.server_name:
            self.host = config.server_name
        else:
            self.host = self.environ.get('HTTP_HOST', 'localhost')

        if not self.check_visitor():
            self.print403()
            return
        elif path == "motd":
            self.print_motd()
        elif path == "rss":
            self.print_rss()
        elif path == "index":
            self.print_index()
        elif path == "changes":
            self.print_changes()
        elif path in ("recent", "new"):
            if (not self.isfriend) and (not self.isadmin):
                self.print403()
            elif path == "recent":
                self.print_recent()
            elif path == "new":
                self.header(self.message["new"], deny_robot=True)
                self.print_new_element_form()
                self.footer()
            else:
                self.print404()
        elif self.form.getfirst("cmd", "") == "new":
            self.jump_new_file()
        elif path.startswith("csv"):
            self.print_csv(path)
        elif re.search(r"^(thread)", path):
            m = re.search(r"^(thread)/?([^/]*)$", path)
            if m is None:
                self.print_title()
                return
            elif m.group(2) != "":
                uri = self.appli[m.group(1)] + self.sep + \
                      self.str_encode(m.group(2))
            elif self.environ.get("QUERY_STRING", "") != "":
                uri = self.appli[m.group(1)] + self.sep + \
                      self.environ["QUERY_STRING"]
            else:
                self.print_title()
                return

            self.print302(uri)
        elif path == '':
            self.print_title()
        else:
            self.print404()

    def print_title(self):
        message = self.message
        cachelist = CacheList()
        cachelist.sort(lambda a,b: cmp(b.valid_stamp, a.valid_stamp))
        now = int(time())
        output_cachelist = []
        for cache in cachelist:
            if now <= cache.valid_stamp + config.top_recent_range:
                output_cachelist.append(cache)
        self.header(message['logo'] + ' - ' + message['description'],
                    mobile = self.mobile_cgi)
        var = {
            'cachelist': output_cachelist,
            'target': 'changes',
            'taglist': UserTagList(),
        }
        self.stdout.write(self.template('top', var))
        self.print_new_element_form()
        self.footer()

    def print_index(self):
        """Print index page."""
        if self.str_filter:
            title = '%s : %s' % (self.message['index'], self.str_filter)
        else:
            title = self.message['index']
        self.header(title)
        self.print_paragraph(self.message['desc_index'])
        cachelist = CacheList()
        cachelist.sort(lambda a,b: cmp(a.datfile, b.datfile))
        self.print_index_list(cachelist, "index")

    def print_changes(self):
        """Print changes page."""
        if self.str_filter:
            title = '%s : %s' % (self.message['changes'], self.str_filter)
        else:
            title = self.message['changes']
        self.header(title)
        self.print_paragraph(self.message['desc_changes'])
        cachelist = CacheList()
        cachelist.sort(lambda a,b: cmp(b.valid_stamp, a.valid_stamp))
        self.print_index_list(cachelist, "changes")

    def make_recent_cachelist(self):
        """Make dummy cachelist from recentlist."""
        recentlist = RecentList()[:]
        recentlist.sort(lambda a,b: cmp(b.stamp, a.stamp))
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
        self.header(title)
        self.print_paragraph(self.message['desc_recent'])
        cachelist = self.make_recent_cachelist()
        self.print_index_list(cachelist, "recent", search_new_file=True)

    def print_csv(self, path):
        """CSV output as API."""
        found = re.search(r"^csv/([^/]+)/(.+)", path)
        if found:
            target, cols = found.groups()
        else:
            self.print404()
            return
        cols = cols.split(",")
        if target == "index":
            cachelist = CacheList()
        elif target == "changes":
            cachelist = CacheList()
            cachelist.sort(lambda a,b: cmp(b.valid_stamp, a.valid_stamp))
        elif target == "recent":
            if (not self.isfriend) and (not self.isadmin):
                self.print403()
                return
            cachelist = self.make_recent_cachelist()
        else:
            self.print404()
            return
        self.stdout.write("Content-Type: text/comma-separated-values;" +
                          " charset=UTF-8\n\n")
        writer = csv.writer(self.stdout)
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
                        row.append("http://" + self.host + path)
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

    def jump_new_file(self):
        if self.form.getfirst("link", "") == "":
            self.header(self.message["null_title"], deny_robot=True)
            self.footer()
        elif re.search(r"[/\[\]<>]", self.form.getfirst("link", "")):
            self.header(self.message["bad_title"], deny_robot=True)
            self.footer()
        elif self.form.getfirst("type", "") == "":
            self.header(self.message["null_type"], deny_robot=True)
            self.footer()
        elif self.form.getfirst("type", "") in config.types:
            tag = self.str_encode(self.form.getfirst('tag', ''))
            search = self.str_encode(self.form.getfirst('search_new_file', ''))
            self.print302(self.appli[self.form.getfirst("type", "")] +
                          self.sep +
                          self.str_encode(self.form.getfirst("link", "")) +
                          '?tag=' + tag +
                          '&search_new_file=' + search)
        else:
            self.print404()

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
                  parent = "http://" + self.host,
                  uri = "http://" + self.host
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
                            '<a href="http://%s%s%s%s/%s/%d.%s">%d.%s</a></p>'\
                            % (self.host, self.appli[cache.type], self.sep,
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

        self.stdout.write("Content-Type: text/xml; charset=UTF-8\n")
        try:
            self.stdout.write("Last-Modified: %s\n" %
                              self.rfc822_time(rss[rss.keys()[0]].date))
        except IndexError, KeyError:
            pass
        self.stdout.write("\n")
        self.stdout.write(make_rss1(rss))

    def print_motd(self):
        self.stdout.write("Content-Type: text/plain; charset=UTF-8\n\n")
        try:
            f = file(config.motd)
            for line in f:
                self.stdout.write(line)
            f.close()
        except IOError:
            self.stderr.write(config.motd + ": IOError\n")

# End of CGI
