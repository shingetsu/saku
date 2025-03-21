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

import gzip
import hashlib
import io
import os.path
import re
import sys
import time

from . import config

__all__ = ['md5digest', 'fsdiff', 'opentext', 'readtext']


def md5digest(s):
    """Get MD5 hex digest.
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
        if os.path.getsize(f) != len(s):
            return False
        with open(f, 'rb') as f:
            if f.read() != s:
                return False
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

def readtext(path):
    with open(path) as f:
        for line in f:
            yield line

def rfc822_time(t):
    """Return date and time in RFC822 format.
    """
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(t))

def gzip_compress(content):
        buf = io.BytesIO()
        comp = gzip.GzipFile(fileobj=buf, mode='wb')
        for chunk in content:
            comp.write(chunk)
            comp.flush()
            yield buf.getvalue()
            buf.seek(0)
            buf.truncate(0)
        comp.close()
        yield buf.getvalue()
        if hasattr(content, 'close'):
            content.close()
