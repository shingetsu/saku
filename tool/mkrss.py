#!/usr/bin/python
#
'''Make Static Toppage, Sitemap and RSS.

Set server_name, proxy_destination and apache_docroot in saku.ini.
'''
#
# Copyright (c) 2006-2012 shinGETsu Project.
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
import sys
import socket
import urllib2
from shutil import copy

import shingetsu.config
import shingetsu.mksuggest
from shingetsu.cache import *
from shingetsu.title import *

socket.setdefaulttimeout(60)

server = shingetsu.config.server_name
destination = 'http://' + shingetsu.config.proxy_destination
docroot = shingetsu.config.apache_docroot
sep = shingetsu.config.query_separator


def urlopen(url, lang='en'):
    req = urllib2.Request(url)
    req.add_header('Accept-Language', '%s;q=1.0' % lang)
    return urllib2.urlopen(req)

def get_rss():
    rssfile = urlopen('%s%s%srss' % (destination,
                                     shingetsu.config.gateway,
                                     sep))
    date = rssfile.info().getheader("last-modified", "")
    rss = rssfile.read()
    rssfile.close()
    return date, rss

def get_html(src, dst, lang='en'):
    htmlfile = urlopen(src, lang)
    html = htmlfile.read()
    htmlfile.close()
    f = file(os.path.join(docroot, dst), 'w')
    f.write(html)
    f.close()

def check_date(date):
    rssdate = os.path.join(docroot, 'rssdate')
    try:
        olddate = file(rssdate).read().strip()
    except IOError:
        olddate = ""
    if date == olddate:
        sys.exit()
    else:
        file(rssdate, 'w').write(date)

def write_rss(rss):
    f = file(os.path.join(docroot, 'rss.rdf'), 'w')
    f.write(rss)
    f.close()

def get_links():
    yield 'http://%s/' % server
    for cache in CacheList():
        type, basename = str(cache).split('_', 1)
        link = 'http://%s%s%s%s' % (server,
                                    shingetsu.config.application[type],
                                    sep,
                                    str_encode(file_decode(str(cache))))
        yield link
        for record in cache:
            yield '%s/%s' % (link, record.id[:8])

def write_sitemap():
    f = file(os.path.join(docroot, 'sitemap.txt'), 'w')
    for i in get_links():
        f.write(i + "\n")
    f.close()

def make_suggest():
    fp = file(os.path.join(docroot, 'suggest.js'), 'w')
    titles = shingetsu.mksuggest.get_titles()
    shingetsu.mksuggest.print_jsfile(titles, fp)

def main():
    os.chdir(shingetsu.config.docroot)
    date, rss = get_rss()
    check_date(date)
    write_rss(rss)
    write_sitemap()
    get_html(destination, 'index.html')
    get_html(destination, 'index.en.html', 'en')
    get_html(destination, 'index.ja.html', 'ja')
    make_suggest()

if __name__ == "__main__":
    main()
