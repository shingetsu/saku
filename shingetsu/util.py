"""Utilities.
"""
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

import hashlib
import os.path
import sys
from . import config

__all__ = ['md5digest', 'fsdiff', 'opentext']


def md5digest(s):
    """Get MD5 hex digest.
    >>> md5digest('abc')
    '900150983cd24fb0d6963f7d28e17f72'
    >>> md5digest(b'abc')
    '900150983cd24fb0d6963f7d28e17f72'
    """
    if isinstance(s, str):
        s = s.encode('utf-8', 'replace')
    return hashlib.md5(s).hexdigest()


def fsdiff(f, s):
    '''Diff between file and string.

    Return same data or not.
    '''
    if isinstance(s, str):
        s = s.encode('utf-8', 'replace')
    try:
        if not os.path.isfile(f):
            return False
        elif os.path.getsize(f) != len(s):
            return False
        elif open(f, 'rb').read() != s:
            return False
        else:
            return True
    except (IOError, OSError) as e:
        sys.stderr.write('%s: %s\n' % (f, e))
        return False

def opentext(path, mode='r'):
    if mode == 'r':
        newline = None
    else:
        newline = '\n'
    return open(path, mode,
                encoding='utf-8', errors='replace',
                newline=newline)

def get_http_remote_addr(env):
    if not config.use_x_forwarded_for:
        return env['REMOTE_ADDR']
    else:
        if 'HTTP_X_FORWARDED_FOR' in env:
            return env['HTTP_X_FORWARDED_FOR']
        elif 'REMOTE_ADDR' in env:
            return env['REMOTE_ADDR']
    return None
