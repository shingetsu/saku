"""Saku Gateway base module.
"""
#
# Copyright (c) 2005-2008 shinGETsu Project.
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

import cgi
import os.path
import re
import urllib
import sys
import time
if hasattr(sys, "winver"):
    from os import listdir
else:
    from dircache import listdir

import basecgi
import config
import spam
from cache import *
from node import *
from title import *
from tag import *
from template import Template
from updatequeue import UpdateQueue

__version__ = "$Revision$"


class Message(dict):

    """Multi-language message for gateway."""

    def __init__(self, file):
        dict.__init__(self)
        try:
            f = open(file)
            del_eos = re.compile(r"[\r\n]*")
            iscomment = re.compile(r"^#$").search
            for line in f:
                line = del_eos.sub("", line)
                if iscomment(line):
                    pass
                else:
                    buf = line.split("<>")
                    if len(buf) == 2:
                        buf[1] = urllib.unquote(buf[1])
                        self[buf[0]] = buf[1]
            f.close()
        except IOError:
            sys.stderr.write(file + ": IOError\n")

# End of Message


def search_message(accept_language):
    """Search message file.

    Example of accept_language: "ja,en-us;q=0.7,en;q=0.3"
    """
    q = {}
    lang = []
    if accept_language != "":
        for i in accept_language.split(","):
            found = re.search(r"(\S+)\s*;\s*q=(\S+)", i)
            if found:
                try:
                    q[found.group(1)] = float(found.group(2))
                except ValueError:
                    pass
            else:
                q[i] = 1

        lang = q.keys()
        lang.sort(lambda a,b: cmp(q[b], q[a]))
    lang.append(config.language)
    for i in lang:
        short_lang = i.split('-')[0]
        for j in (i, short_lang):
            file = config.file_dir + "/" + "message-" + j + ".txt"
            if re.search(r'^[-A-Za-z0-9]+$', j) and os.path.isfile(file):
                return Message(file)
    return None

# End of search_message


class CGI(basecgi.CGI):

    root = config.root_path
    sep = config.query_separator
    appli = config.application
    gateway_cgi = config.gateway
    thread_cgi = config.thread_cgi
    admin_cgi = config.admin_cgi
    mobile_cgi = config.mobile_cgi
    message = None
    filter = None
    str_filter = ''
    tag = None
    str_tag = ''

    def __init__(self,
                 stdin=sys.stdin,
                 stdout=sys.stdout,
                 stderr=sys.stderr,
                 environ=os.environ):
        basecgi.CGI.__init__(self,
                             stdin=stdin,
                             stdout=stdout,
                             stderr=stderr,
                             environ=environ)
        if "HTTP_ACCEPT_LANGUAGE" in self.environ:
            al = self.environ["HTTP_ACCEPT_LANGUAGE"]
        else:
            al = ""
        self.message = search_message(al)
        addr = self.environ.get("REMOTE_ADDR", "")
        self.isadmin = config.re_admin.search(addr)
        self.isfriend = config.re_friend.search(addr)
        self.isvisitor = config.re_visitor.search(addr)
        self.obj_template = Template()
        self.template = self.obj_template.display
        var = {
            'cgi': self,
            'environ': self.environ,
            'ua': self.environ.get('HTTP_USER_AGENT', ''),
            'message': self.message,
            'lang': self.message['lang'],
            'config': config,
            'appli': self.appli,
            'gateway_cgi': self.gateway_cgi,
            'thread_cgi': self.thread_cgi,
            'admin_cgi': self.admin_cgi,
            'mobile_cgi': self.mobile_cgi,
            'root_path': config.root_path,
            'archive_uri': config.archive_uri,
            'types': config.types,
            'isadmin': self.isadmin,
            'isfriend': self.isfriend,
            'isvisitor': self.isvisitor,
            'localtime': self.localtime,
            'str_encode': self.str_encode,
            'file_decode': self.file_decode,
            'escape': self.escape,
            'escape_simple': lambda s: cgi.escape(s, True),
            'escape_space': self.escape_space,
            'make_list_item': self.make_list_item,
            'gateway_link': self.gateway_link,
        }
        self.obj_template.set_defaults(var)

    def path_info(self):
        """Parse PATH_INFO.

        If PATH_INFO is not defined, use QUERY_STRING.
        x.cgi?foo&bar=y -> path="foo".
        """
        m = re.search(r"([^&;=]*)(&|$)", self.environ.get("QUERY_STRING", ""))
        if self.environ.get("PATH_INFO", "") != "":
            path = self.environ["PATH_INFO"]
            if path.startswith("/"):
                path = path[1:]
        elif m is not None:
            path = m.group(1)
        else:
            path = ""
        path = self.escape(self.str_decode(path))
        return path

    def str_encode(self, query):
        return str_encode(query)

    def str_decode(self, query):
        return str_decode(query)

    def file_encode(self, type, query):
        return file_encode(type, query)

    def file_decode(self, query):
        return file_decode(query)

    def escape(self, msg):
        msg = msg.replace("&", "&amp;")
        msg = re.sub(r"&amp;(#\d+|#[Xx][0-9A-Fa-f]+|[A-Za-z0-9]+);",
                     r"&\1;",
                     msg)
        msg = msg.replace("<", "&lt;")
        msg = msg.replace(">", "&gt;")
        msg = msg.replace("\r", "")
        msg = msg.replace("\n", "<br>")
        return msg

    def gateway_link(self, cginame, command):
        var = {
            'cginame': cginame,
            'command': command,
            'description': self.message.get('desc_'+command, ''),
        }
        return self.template('gateway_link', var)

    def extension(self, suffix):
        filename = []
        for i in listdir(config.abs_docroot):
            if i.endswith('.%s' % suffix) and \
               (not (i.startswith('.') or i.startswith('_'))):
                filename.append(i)
        filename.sort()
        return filename

    def menubar(self, id='', rss=''):
        var = {
            'id': id,
            'rss': rss,
        }
        return self.template('menubar', var)

    def header(self, title='', rss='',
               cookie=None, deny_robot=False, mobile=''):
        '''Print CGI and HTTP header.
        '''
        if rss == '':
            rss = self.gateway_cgi + '/rss'
        var = {
            'title': title,
            'str_title': self.str_encode(title),
            'rss': rss,
            'cookie': cookie,
            'deny_robot': deny_robot,
            'mobile': mobile,
            'js': self.extension('js'),
            'css': self.extension('css'),
            'menubar': self.menubar('top', rss)
        }
        self.stdout.write(self.template('header', var))

    def footer(self):
        self.stdout.write(self.template('footer'))

    def localtime(self, stamp=0):
        """Return YYYY-mm-dd HH:MM."""
        return time.strftime('%Y-%m-%d %H:%M', time.localtime(int(stamp)))

    def rfc822_time(self, stamp=0):
        """Return date and time in RFC822 format."""
        return time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                             time.gmtime(int(stamp)))

    def res_anchor(self, id, appli, title, absuri=False):
        title = self.str_encode(title)
        if absuri:
            prefix = 'http://' + self.host
            innerlink = ''
        else:
            prefix = ''
            innerlink = ' class="innerlink"'
        return '<a href="%s%s%s%s/%s"%s>' % \
               (prefix, appli, self.sep, title, id, innerlink)

    def html_format(self, plain, appli, title, absuri=False):
        buf = plain.replace("<br>", "\n")
        buf = buf.expandtabs()
        buf = self.escape(buf)
        buf = re.sub(r"https?://[^\x00-\x20\"'()<>\[\]\x7F-\xFF]{2,}",
                     r'<a href="\g<0>">\g<0></a>',
                     buf)
        buf = re.sub(r"(&gt;&gt;)([0-9a-f]{8})",
                     self.res_anchor(r"\2", appli, title, absuri=absuri) +
                     r"\g<0></a>",
                     buf)
        buf = re.sub(r'\[\[<a.*?>(.*?)\]\]</a>', r'[[\1]]', buf)

        tmp = ""
        while buf:
            m = re.search(r"\[\[([^<>]+?)\]\]", buf)
            if m is not None:
                tmp += buf[:m.start()]
                tmp += self.bracket_link(m.group(1), appli, absuri=absuri)
                buf = buf[m.end():]
            else:
                tmp += buf
                buf = ""
        return self.escape_space(tmp)

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
            uri = prefix + self.thread_cgi + self.sep + \
                  self.str_encode(m.group(2)) + \
                  '/' + m.group(3)
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

    def remove_file_form(self, cache, title=''):
        var = {
            'cache': cache,
            'title': title,
        }
        self.stdout.write(self.template('remove_file_form', var))

    def print_jump(self, next):
        '''Print jump script.'''
        var = {
            'next': next,
        }
        self.stdout.write(self.template('jump', var))

    def print302(self, next):
        """Print CGI header (302 moved temporarily)."""
        self.header("Loading...")
        self.print_jump(next)
        self.footer()

    def print403(self):
        '''Print CGI header (403 forbidden).'''
        self.header(self.message['403'], deny_robot=True)
        self.print_paragraph(self.message['403_body'])
        self.footer()

    def print404(self, cache=None, id=None):
        '''Print CGI header (404 not found).'''
        self.header(self.message['404'], deny_robot=True)
        self.print_paragraph(self.message['404_body'])
        if hasattr(self, 'archive_uri'):
            if id:
                self.print_jump('%s%s.html' % (self.archive_uri, id))
            else:
                self.print_jump(self.archive_uri)
        if cache is not None:
            self.remove_file_form(cache)
        self.footer()

    def lock(self):
        if self.isadmin:
            lockfile = config.admin_search
        else:
            lockfile = config.search_lock
        if not os.path.isfile(lockfile):
            f = file(lockfile, 'wb')
            f.close()
            return True
        elif os.path.getmtime(lockfile) + config.search_timeout < time.time():
            f = file(lockfile, 'wb')
            f.close()
            return True
        else:
            return False

    def unlock(self):
        if self.isadmin:
            lockfile = config.admin_search
        else:
            lockfile = config.search_lock
        try:
            os.remove(lockfile)
        except (OSError, IOError), err:
            self.stderr.write('%s: OSError/IOError: %s\n' % (lockfile, err))
            return False

    def get_cache(self, cache):
        '''Search cache from network.'''
        result = cache.search()
        self.unlock()
        return result

    def print_new_element_form(self, parent=None):
        if not (self.isadmin or self.isfriend):
            return
        var = {
            'datfile': '',
            'cginame': self.gateway_cgi,
        }
        self.stdout.write(self.template('new_element_form', var))

    def error_time(self):
        from random import gauss
        return int(gauss(time.time(), config.time_error))

    def do_post(self, path, form):
        """Post article."""
        import base64
        try:
            attach = form['attach']
        except KeyError:
            attach = None
        str_attach = ''

        if (attach is not None) and attach.file:
            if len(attach.value) > config.record_limit*1024:
                self.header(self.message["big_file"], deny_robot=True)
                self.footer()
                return None
            str_attach = base64.encodestring(attach.value).replace("\n", "")
        guess_suffix = "txt"
        if (attach is not None) and attach.filename:
            found = re.search(r"\.([^.]+)$", attach.filename)
            if found:
                guess_suffix = found.group(1).lower()

        suffix = form.getfirst("suffix", "")
        if (suffix == "") or (suffix == "AUTO"):
            suffix = guess_suffix
        elif suffix.startswith("."):
            suffix = suffix[1:].lower()
        else:
            suffix = suffix.lower()
        suffix = re.sub(r"[^0-9A-Za-z]", "", suffix)

        if form.getfirst("error", "") != "":
            stamp = self.error_time()
        else:
            stamp = int(time.time())

        body = {}
        value = form.getfirst("body", "")
        if value != "":
            body["body"] = self.escape(value)

        if str_attach != "":
            body["attach"] = str_attach
            body["suffix"] = re.sub(r"[\r\n]", "", suffix)

        if not body:
            self.header(self.message["null_article"], deny_robot=True)
            self.footer()
            return None

        for key in ("base_stamp", "base_id", "name", "mail"):
            value = form.getfirst(key, "")
            if value != "":
                body[key] = self.escape(value)

        if not body:
            self.header(self.message["null_article"], deny_robot=True)
            self.footer()
            return None

        cache = Cache(form.getfirst("file"))
        rec = Record(datfile=cache.datfile)
        passwd = form.getfirst("passwd", "")
        id = rec.build(stamp, body, passwd=passwd)

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

    def check_get_cache(self):
        agent = self.environ.get("HTTP_USER_AGENT", "")
        if not (self.isfriend or self.isadmin):
            return False
        elif re.search(config.robot, agent):
            return False
        elif self.lock():
            return True
        else:
            return False

    def check_visitor(self):
        return self.isadmin or self.isfriend or self.isvisitor

    def escape_space(self, text):
        text = re.sub(r'  ', '&nbsp;&nbsp;', text)
        text = re.sub(r'<br> ', '<br>&nbsp;', text)
        text = re.sub(r'^ ', '&nbsp;', text)
        text = re.sub(r' $', '&nbsp;', text)
        text = text.replace('<br>', '<br />\n');
        return text

    def make_list_item(self, cache, remove=True, target='changes'):
        x = self.file_decode(cache.datfile)
        y = self.str_encode(x)
        u = unicode(x, 'utf-8', 'replace')
        if self.filter and (not self.filter.search(u)):
            return None
        elif self.tag:
            matchtag = False
            for t in (cache.tags + cache.sugtags):
                if str(t).lower() == self.tag:
                    matchtag = True
                    break
            if not matchtag:
                return None
        x = self.escape_space(x)
        if cache.tags:
            tags, tagclassname = cache.tags, 'tags'
        else:
            tags, tagclassname = cache.sugtags, 'sugtags'
        var = {
            'cache': cache,
            'title': x,
            'str_title': y,
            'tags': tags,
            'tagclassname': tagclassname,
            'target': target,
            'remove': remove,
        }
        return self.template('list_item', var)

    def print_index_list(self, cachelist, target='', footer=True):
        var = {
            'target': target,
            'filter': self.str_filter,
            'tag': self.str_tag,
            'taglist': UserTagList(),
            'cachelist': cachelist,
        }
        self.stdout.write(self.template('index_list', var))
        if footer:
            self.print_new_element_form();
            self.footer()

    def print_paragraph(self, contents):
        var = {'contents': contents}
        self.stdout.write(self.template('paragraph', var))

# End of CGI
