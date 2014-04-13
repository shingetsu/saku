#!/usr/bin/python3
#
'''Make shinGETsu Live Link.

1. Run command:
    mksuggest > suggest.js
2. Write tags in HTML files:
    <p><a href="http://example.com/" id="shingetsu_link">foo</a></p>
    ...
    <script type="text/javascript"
     src="http://example.com/suggest.js" charset="utf-8"></script>
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
import re
import sys
import cgi
import socket
import urllib.request, urllib.error, urllib.parse

from . import config
from .template import Template

socket.setdefaulttimeout(10)

server = config.server_name
port = config.port
docroot = config.apache_docroot

def get_titles():
    f = urllib.request.urlopen('http://localhost:%d/gateway.cgi/csv/changes/title' %
                        port)
    titles = []
    for line in f:
        line = line.strip()
        line = re.sub(r'^"|"$', '', line)
        line = line.replace('""', '"')
        titles.append(line)
    return titles

def print_jsfile(titles, fp):
    var = {
        'escape_simple': lambda s: cgi.escape(s, True),
        'titles': titles,
        'server': server,
    }
    fp.write(Template().display('suggest_js', var))

def main():
    titles = get_titles()
    print_jsfile(titles, sys.stdout)

if __name__ == '__main__':
    main()
