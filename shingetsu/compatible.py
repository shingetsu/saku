''' Import compatible modules.
'''
#
# This module contributed by a shinGETsu user.
# http://archive.shingetsu.info/b1129f37d45b15269a0db850ac053d46/16186b33.html
#
# Copyright (c) 2008 shinGETsu Project.
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


__all__ = ['threading', 'RLock', 'Thread', 'listdir', 'md5', 'Set', 'StringIO']

import os
import sys


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
    

try:
    import threading
except ImportError:
    import dummy_threading as threading

RLock = threading.RLock
Thread = threading.Thread

if hasattr(sys, "winver"):
    from os import listdir
else:
    from dircache import listdir


try:
    Set = set
except NameError:
    from sets import Set


try:
    import hashlib
    class _md5(object):
        new = __call__ = hashlib.md5
    md5 = _md5()
except ImportError:
    import md5

