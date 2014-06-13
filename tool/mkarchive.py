#!/usr/bin/python3
#
'''Make archive, 1 HTML for 1 record
'''
#
# Copyright (c) 2006-2014 shinGETsu Project.
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
import re
import os
import sys
import time
from shutil import copy

import shingetsu.config
from shingetsu.util import md5digest, opentext
from shingetsu.cache import *
from shingetsu.title import *

archive_dir = shingetsu.config.archive_dir
archive_uri = shingetsu.config.archive_uri

def localtime(stamp=0):
    """Return YYYY-mm-dd HH:MM."""
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(int(stamp)))

def escape(msg):
    msg = msg.replace("&", "&amp;")
    msg = re.sub(r"&amp;(#\d+|#[Xx][0-9A-Fa-f]+|[A-Za-z0-9]+);",
                 r"&\1;",
                 msg)
    msg = msg.replace("<", "&lt;")
    msg = msg.replace(">", "&gt;")
    msg = msg.replace("\r", "")
    msg = msg.replace("\n", "<br>")
    return msg

def res_anchor(id):
    return ('<a href="%s.html" class="innerlink">') % id

def html_format(plain):
    buf = plain.replace("<br>", "\n")
    buf = escape(buf)
    buf = re.sub(r"<br>",
                 "<br />\n    ",
                 buf)
    buf = re.sub(r"(&gt;&gt;)([0-9a-f]{8})",
                 res_anchor(r"\2") + r"\g<0></a>",
                 buf)
    buf = re.sub(r"https?://[^\x00-\x20\"'()<>\[\]\x7F-\xFF]{2,}",
                 r'<a href="\g<0>">\g<0></a>',
                 buf)
    buf = re.sub(r"\[\[<a.*?>(.*?)\]\]</a>",
                 r"[[\1]]",
                 buf)

    tmp = ""
    while buf:
        m = re.search(r"\[\[([^<>]+?)\]\]", buf)
        if m is not None:
            tmp += buf[:m.start()]
            tmp += bracket_link(m.group(1))
            buf = buf[m.end():]
        else:
            tmp += buf
            buf = ""
    return tmp

def bracket_link(link):
    m = re.search(r"^/(thread)/([^/]+)/([0-9a-f]{8})$", link)
    if m is not None:
        title = md5digest(file_encode(m.group(1), m.group(2)))
        id = m.group(3)
        uri = '/%s/%s.html' % (title, id)
        return '<a href="' + uri + '">[[' + link + ']]</a>'

    m = re.search(r"^/(thread)/([^/]+)$", link)
    if m is not None:
        title = md5digest(file_encode(m.group(1), m.group(2)))
        uri = '/%s/' % title
        return '<a href="' + uri + '">[[' + link + ']]</a>'

    m = re.search(r"^([^/]+)/([0-9a-f]{8})$", link)
    if m is not None:
        title = md5digest(file_encode('thread', m.group(1)))
        id = m.group(2)
        uri = '/%s/%s.html' % (title, id)
        return '<a href="' + uri + '">[[' + link + ']]</a>'

    m = re.search(r"^([^/]+)$", link)
    if m is not None:
        title = md5digest(file_encode('thread', m.group(1)))
        uri = '/%s/' % title
        return '<a href="' + uri + '">[[' + link + ']]</a>'

    return "[[" + link + "]]"

def print_record(fp, rec):
    sid = rec["id"][:8]
    stamp = '<span class="stamp" id="s%s">%s</span>' % \
                (rec['stamp'], localtime(rec['stamp']))
    if ("name" in rec) and (rec["name"] != ""):
        name = rec["name"]
    else:
        name = 'Anonymous'

    if ("mail" in rec) and (rec["mail"] != ""):
        mail = "\n    [" + rec["mail"] + "]"
    else:
        mail = ""

    if "body" in rec:
        body = rec["body"]
    else:
        body = ""
    body = html_format(body)

    if ("suffix" in rec) and rec["suffix"]:
        suffix = rec["suffix"]
    else:
        suffix = "txt"

    attach = ""
    if "attach" in rec:
        attach = '    <a href="%sx.%s">%sx.%s</a>\n' % \
                    (sid, suffix, sid, suffix,)
    sign = ""
    if "pubkey" in rec:
        sign = ' <span class="sign" title="[%s]">%s</span>' % \
               (rec["target"], rec["pubkey"])

    fp.write('  <dt id="r%s">\n' % sid)
    fp.write(
        '    %s :<span class="name">%s</span>' % (sid, name) +
        mail + sign + "\n" +
        '    ' + stamp + "\n" +
        attach +
        "  </dt>\n" +
        '  <dd id="b%s">\n' % sid +
        "    " + body + "\n")
    fp.write("  </dd>\n")

def write_html(fp, rec):
    fp.write(
        '<!DOCTYPE html>\n' +
        '<html xmlns="http://www.w3.org/1999/xhtml"' +
        ' lang="ja" xml:lang="ja">\n' +
        '<head>\n' +
        '  <meta http-equiv="content-type"' +
        ' content="text/html; charset=UTF-8" />\n' +
        '  <title>%s</title>\n' % file_decode(rec.datfile) +
        '  <link rel="author" href="http://www.shingetsu.info/" />\n' +
        '  <link rel="contents" href="/" />\n' +
        '  <link rel="stylesheet" type="text/css" href="/default.css" />\n' +
        '</head>\n' +
        '<body>\n' +
        '<h1><a href="./">%s</a></h1>\n' % file_decode(rec.datfile) +
        '<dl>\n')
    print_record(fp, rec)
    fp.write(
        '</dl>\n' +
        '<address>Powered by' +
        ' <a href="http://www.shingetsu.info/">shinGETsu</a>.</address>\n')
    fp.write(
        '</body>\n' +
        '</html>\n')

def make_html(cache):
    title = md5digest(cache.datfile)
    dstdir = os.path.join(archive_dir, title)
    if not os.path.isdir(dstdir):
        os.makedirs(dstdir)
    count = 0
    for rec in cache:
        sid = rec.id[:8]
        dstfile = '%s/%s/%s.html' % (archive_dir, title, sid)
        if not os.path.exists(dstfile):
            rec.load_body()
            f = opentext(dstfile, 'w')
            write_html(f, rec)
            f.close()
            os.utime(dstfile, (rec.stamp, rec.stamp))
            rec.free()
            count += 1
    return count

def copy_attach(cache):
    title = md5digest(cache.datfile)
    srcdir = os.path.join(shingetsu.config.cache_dir, cache.datfile)
    srcdir = os.path.join(srcdir, 'attach')
    dstdir = os.path.join(archive_dir, title)
    if not os.path.isdir(dstdir):
        os.makedirs(dstdir)
    for f in os.listdir(srcdir):
        m = re.search(r'([0-9]+)_([0-9a-f]{32})\.(.*)', f)
        stamp, id, suffix = m.groups()
        stamp = int(stamp)
        srcfile = os.path.join(srcdir, f)
        dstfile = os.path.join(dstdir, '%sx.%s' % (id[:8], suffix))
        if not os.path.exists(dstfile):
            copy(srcfile, dstfile)
            os.utime(dstfile, (stamp, stamp))

def make_sitemap():
    f = opentext(os.path.join(archive_dir, 'sitemap.txt'), 'w')
    f.write('%s\n' % archive_uri)
    for d in os.listdir(archive_dir):
        if (len(d) != 32) or \
           (not os.path.isdir(os.path.join(archive_dir, d))):
            continue
        for html in os.listdir(os.path.join(archive_dir, d)):
            if (len(html) != 8+5) or (not html.endswith('.html')):
                continue
            f.write('%s%s/%s\n' % (archive_uri, d, html))

def main():
    cachelist = CacheList()
    for cache in cachelist:
        n = make_html(cache)
        if n:
            print(n, file_decode(cache.datfile))
        copy_attach(cache)
    make_sitemap()

if __name__ == '__main__':
    main()
