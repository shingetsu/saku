'''Temporary Address to Post Article.
'''
#
# Copyright (c) 2007 shinGETsu Project.
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
import sys
import md5
from random import random
from time import time

try:
    from threading import RLock
except ImportError:
    from dummy_threading import RLock

import shingetsu.config as config

__version__ = "$Revision$"
__all__ = ['TmpAddress']

lock = RLock()


class TmpAddress:
    '''Temporary Address to Post Article.

    Last some addresses are available.
    '''

    def __init__(self):
        self.path = config.tmpaddr_file
        self.available = []
        try:
            for line in file(self.path):
                try:
                    addr, stamp = line.strip().split('<>')
                    stamp = int(stamp)
                    self.available.append((addr, stamp))
                except ValueError:
                    pass
        except (IOError, OSError), err:
            sys.stderr.write('IOError/OSError: %s\n' % err)
        self.update()

    def update(self):
        now = int(time())
        tmp = []
        changed = False
        for addr, stamp in self.available:
            if now < stamp + config.tmpaddr_span:
                tmp.append((addr, stamp))
            else:
                changed = True
        if len(tmp) < config.tmpaddr_size:
            r = ''
            for i in range(4):
                r += str(random())
            addr = md5.new(r).hexdigest()
            tmp.append((addr, now))
            changed = True
        if changed:
            self.available = tmp
            self.sync()

    def sync(self):
        try:
            try:
                lock.acquire(True)
                f = file(self.path, 'wb')
                for addr, stamp in self.available:
                    f.write('%s<>%d\n' % (addr, stamp))
                f.close()
            finally:
                lock.release()

        except (IOError, OSError), err:
            sys.stderr.write('IOError/OSError: %s\n' % err)

    def check(self, addr):
        found = re.search(r'(.*?)\@', addr)
        if found:
            addr = found.group(1)
        for address, stamp in self.available:
            if address == addr:
                return True
        return False

    def getaddress(self):
        return self.available[-1][0]

# End of TmpAddress
