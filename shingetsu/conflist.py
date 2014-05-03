'''List Style Config.

The object is tied a file.
When the file is updated, the object is updated too.

Encoding must be UTF-8.
'''
#
# Copyright (c) 2006,2014 shinGETsu Project.
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
import sys
import os.path

from .util import opentext

__all__ = ['ConfList', 'RegExpList']


class ConfList:
    '''List Style Config.
    '''
    def __init__(self, path):
        self.mtime = 0
        self.path = path
        self.update()

    def update(self):
        try:
            if not os.path.exists(self.path):
                self.data = []
                return
            mtime = os.path.getmtime(self.path)
            if mtime <= self.mtime:
                return
            self.mtime = mtime
            self.data = []
            f = opentext(self.path)
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    self.data.append(self.compile(line))
            f.close()
        except (IOError, OSError) as err:
            sys.stderr.write('IOError/OSError: %s\n' % err)

    def compile(self, pat):
        return pat

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

# End of ConfList


class RegExpList(ConfList):
    '''RegExp list.

    One regexp per one line.
    '''

    def compile(self, pat):
        try:
            return re.compile(pat)
        except re.error as e:
            sys.stderr.write('RegExp Error: %s: %s\n' % (pat, e))
            return None

    def check(self, target):
        '''Match target for all regexp.
        '''
        for r in self.data:
            if r.search(target):
                return True
        return False

# End of RegExpList
