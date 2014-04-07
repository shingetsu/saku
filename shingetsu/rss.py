"""Data structure of RSS and useful functions.
"""
#
# Copyright (c) 2005-2012 shinGETsu Project.
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
import cgi

from template import Template


class Item:
    """One item."""

    title = ""
    link  = ""
    description = ""
    date  = 0           # Seconds from 1970-01-01T00:00

    def __init__(self, link="", title="", date=0, creator='', subject=None,
                 description="", content=""):
        """Constructor."""
        del_eos = re.compile(r'[\r\n]*')
        self.link  = link
        self.date  = date
        self.creator = creator
        if subject:
            self.subject = subject
        else:
            self.subject = []
        self.title = del_eos.sub('', title)
        self.description = del_eos.sub('', description)
        self.content = content

class RSS(dict):
    """RSS.

    It is the dictionary which key is URI.
    """

    encode = "utf-8"
    lang   = "en"
    title  = ""
    parent = ""         # Place where is documents or RSS
    link   = ""         # URI of main page
    uri    = ""         # URI of RSS
    description = ""

    def __init__(self, encode="utf-8", lang="en", title="",
            parent="", link="", uri="", description="", xsl=""):
        """Constructor."""

        self.encode = encode
        self.lang   = lang
        self.title  = title
        self.description = description
        self.parent = parent
        self.xsl = xsl

        if parent and parent[-1] != "/":
            parent += "/"
            self.parent += "/"

        if link != "":
            self.link = link
        else:
            self.link = parent
        if uri != "":
            self.uri = uri
        else:
            self.uri = parent + "rss.xml"

    def append(self, link,
                title = "",
                date = 0,
                creator = '',
                subject = None,
                description = "",
                content = "",
                abs = False):
        """Add an item."""

        if not abs:
            link = self.parent + link
        item = Item(link,
                    title = title,
                    date = date,
                    creator = creator,
                    subject = subject,
                    description = description,
                    content = content)
        self[link] = item

    def keys(self):
        """List of links sorted by date."""

        links = dict.keys(self)
        links.sort(key=lambda x: self[x].date, reverse=True)
        return links

    def __iter__(self):
        return iter(self.keys())

def make_rss1(rss):
    '''Generate RSS 1.0.
    '''
    def w3cdate(date):
        from time import strftime, gmtime
        return strftime('%Y-%m-%dT%H:%M:%SZ', gmtime(date))
    var = {
        'rss': rss,
        'feed': [rss[uri] for uri in rss],
        'w3cdate': w3cdate,
        'escape': cgi.escape,
    }
    return Template().display('rss1', var)
