'''Tagging.
'''
#
# Copyright (c) 2005-2023 shinGETsu Project.
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

from . import config
from .tiedobj import *

__all__ = ['TagList', 'UserTagList', 'SuggestedTagList', 'SuggestedTagTable']


class Tag:
    '''Tag.

    Including tag-string and its weight.
    '''

    def __init__(self, tagstr, weight=0):
        self.tagstr = str(tagstr)
        self.weight = weight

    def __str__(self):
        return self.tagstr

# End of Tag


class TagList(list):

    '''File includes list.

    One element par one line.
    '''

    def __init__(self, datfile, path, caching=False):
        self.datfile = datfile
        self.path = path
        self.caching = caching
        self.tiedlist = tiedlist(path, Tag, caching)
        list.__init__(self, self.tiedlist.data)

    def __str__(self):
        return ' '.join([str(i) for i in self])

    def check_append(self, value):
        if re.search(r'[<>&]', str(value)):
            return
        else:
            self.append(Tag(value, 1))
            self.tiedlist.append(Tag(value, 1), False)

    def update(self, values):
        for tag in self:
            self.tiedlist.remove(tag)
        del self[0:]
        for v in values:
            self.check_append(v)

    def add(self, values):
        for v in values:
            including = False
            for i in self:
                if str(i) == str(v):
                    i.weight += 1
                    including = True
                    break
            if not including:
                self.check_append(v)

    def sync(self):
        self.tiedlist.sync()

# End of TagList


class UserTagList(TagList):
    '''User's All Tags.
    '''

    def __init__(self):
        TagList.__init__(self, None, config.taglist, True)

    def update_all(self):
        from .cache import CacheList
        cachelist = CacheList()
        self.update([])
        for cache in cachelist:
            self.add(cache.tags)
        self.sync()

    def sync(self):
        self.sort(key=lambda x: str(x))
        TagList.sync(self)

# End of UserTagList


class SuggestedTagList(TagList):
    def __init__(self, table, datfile, values=None):
        if values is None:
            values = []
        list.__init__(self, [Tag(i) for i in values])
        self.table = table
        self.datfile = datfile
        self.tiedlist = tiedlist(None, Tag)
        for i in self:
            self.tiedlist.append(i)

    def prune(self, size=config.tag_size):
        self.sort(key=lambda x: x.weight, reverse=True)
        for tag in self[size:]:
            self.tiedlist.remove(tag)
        del self[size:]

    def sync(self):
        self.table[self.datfile] = self

# End of SuggestedTagList


class SuggestedTagTable:
    '''Suggested Tag Table.

    data: sugtags[filename] = [tag1, tag2, ...]
    '''
    def __init__(self):
        def sugtaglist():
            return SuggestedTagList(self, None)
        self.tieddict = tieddict(config.sugtag, Tag, True, sugtaglist)

    def __setitem__(self, key, taglist):
        self.tieddict[key] = taglist

    def __getitem__(self, key):
        return self.tieddict[key]

    def __getitem__(self, key):
        return self.tieddict[key]

    def __contains__(self, key):
        return key in self.tieddict

    def __delitem__(self, key):
        del self.tieddict[key]

    def keys(self):
        return list(self.tieddict.keys())

    def sync(self):
        self.tieddict.sync()

    def prune(self, recentlist):
        tmp = set(list(self.keys()))
        for r in recentlist:
            tmp.discard(r.datfile)
            if r.datfile in self:
                self[r.datfile].prune()
        for datfile in tmp:
            del self[datfile]
            del self.tieddict[datfile]

# Enf of SuggestedTagTable
