'''JavaScript Cache.
'''
#
# Copyright (c) 2014 shinGETsu Project.
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

import os.path
import sys
from glob import glob

from .util import opentext

__all__ = ['JsCache']


class JsCache:
    '''JavaScript Cache.
    '''
    def __init__(self, path):
        self._path = path
        self.mtime = 0
        self.script = ''
        self._files = set()
        self.update()

    def update(self):
        try:
            if not os.path.exists(self._path):
                return
            need_reload = False
            scripts = []
            for i in os.listdir(self._path):
                if not i.endswith('.js') or \
                   i.startswith('.') or i.startswith('_'):
                    continue
                scripts.append(i)
                mtime = os.path.getmtime(i)
                if self.mtime < mtime:
                    self.mtime = mtime
                    need_reload = True
            if not need_reload and self._files == set(scripts):
                return
            self._files = set(scripts)
            scripts.sort()
            buf = []
            for i in scripts:
                buf.append(opentext(i).read())
            self.script = '\n'.join(buf)
        except (IOError, OSError) as err:
            sys.stderr.write('IOError/OSError: %s\n' % err)

# End of JsCache
