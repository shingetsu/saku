'''List Style Config.

The object is tied a file.
When the file is updated, the object is updated too.

Python style encode declaration can be used in first line,
like this:  ``-*- coding: utf-8 -*-''.

Write one string per one line.
Lines starts with '#' are comments.
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
# $Id: spam.py 1210 2006-06-07 06:42:15Z fuktommy $
#

import re
import sys
import os.path

__version__ = '$Revision$'
__all__ = ['ConfList', 'RegExpList']


class ConfList:
    '''List Style Config.
    '''
    def __init__(self, path):
        self.mtime = 0
        self.path = path
        self.update()

    def update(self):
        buf = []
        try:
            if not os.path.exists(self.path):
                self.data = []
                return
            mtime = os.path.getmtime(self.path)
            if mtime <= self.mtime:
                return
            self.mtime = mtime
            f = open(self.path)
            for line in f:
                buf.append(line.strip())
            f.close()
        except (IOError, OSError) as err:
            sys.stderr.write('IOError/OSError: %s\n' % err)
        declaration = re.compile(r'coding[=:]\s*([-\w_.]+)')
        encoding = 'utf-8'
        for pat in buf[:2]:
            found = declaration.search(pat)
            if found:
                encoding = found.group(1)
                break
        self.data = []
        for pat in buf:
            if pat and (not pat.startswith('#')):
                tmp = self.compile(pat, encoding)
                if tmp is not None:
                    self.data.append(tmp)

    def compile(self, pat, encoding=None):
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

    def compile(self, pat, encoding=None):
        try:
            if encoding:
                pat = str(pat, encoding)
            return re.compile(pat)
        except (re.error, UnicodeDecodeError) as e:
            sys.stderr.write('RegExp Error: %s: %s\n' % (pat, e))
            return None

    def check(self, target, encoding=None):
        '''Match target for all regexp.
        '''
        try:
            if encoding:
                target = str(target, encoding)
        except UnicodeDecodeError as e:
            sys.stderr.write('UnicodeDecodeError: %s\n' % e)
            return None
        for r in self.data:
            if r.search(target):
                return True
        return False

# End of RegExpList
