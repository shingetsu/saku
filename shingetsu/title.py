'''Title Utilities.
'''
#
# Copyright (c) 2005-2007 shinGETsu Project.
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
# $Id: gateway.py 1296 2006-11-20 14:14:02Z fuktommy $
#

import urllib

__all__ = ['str_encode', 'str_decode', 'file_encode', 'file_decode']
__version__ = '$Revision$'


def str_encode(query):
    '''Encode for URI.

    ~ -> %7E
    '''
    return urllib.quote(str(query))

def str_decode(query):
    '''Decode URI.

    %7E -> ~
    '''
    return urllib.unquote(query)

def file_encode(type, query):
    '''Encode for filename.

    ~ -> 7E
    '''
    buf = [type, '_']
    for i in query:
        buf.append('%02X' % ord(i))
    return ''.join(buf)

def file_decode(query):
    '''Decode filename.

    7E -> ~
    '''
    q = query.split('_')
    if q < 2:
        return None
    else:
        query = q[1]
    buf = []
    for i in range(0, len(query), 2):
        try:
            buf.append('%c' % int(query[i:i+2], 16))
        except (ValueError, IndexError):
            self.stderr.write(query + ': ValueError/IndexError\n')
            return None
    return ''.join(buf)
