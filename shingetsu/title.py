'''Title Utilities.
'''
#
# Copyright (c) 2005-2014 shinGETsu Project.
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
import urllib.request, urllib.error, urllib.parse
import sys

from . import config
from .compatible import md5

__all__ = ['str_encode', 'str_decode', 'file_encode', 'file_decode']


def str_encode(query):
    '''Encode for URI.

    >>> str_encode('~')
    '%7E'
    '''
    if isinstance(query, str):
        query = query.encode('utf-8', 'replace')
    return urllib.parse.quote(str(query))

def str_decode(query):
    '''Decode URI.

    >>> str_decode('%7E')
    '~'
    '''
    return urllib.parse.unquote(query)

def file_encode(type, query):
    '''Encode for filename.

    >>> file_encode('foo', '~')
    'foo_7E'
    '''
    buf = [type, '_']
    if isinstance(query, str):
        query = query.encode('utf-8', 'replace')
    for i in query:
        buf.append('%02X' % ord(i))
    return ''.join(buf)

def file_decode_type(query, type=None):
    """Decode file type.

    >>> file_decode_type('thread_41')
    'thread'
    """
    q = query.split('_')
    if len(q) < 2:
        return type
    return q[0]

def file_decode(query, type=None, as_unicode=True):
    '''Decode filename.

    >>> file_decode('foo_7E')
    '~'
    '''
    if isinstance(query, str):
        query = query.encode('utf-8', 'replace')
    q = query.split('_')
    if len(q) < 2:
        return None
    if type is not None:
        type = q[0]
    query = q[1]
    buf = []
    for i in range(0, len(query), 2):
        try:
            buf.append('%c' % int(query[i:i+2], 16))
        except (ValueError, IndexError):
            sys.stderr.write(query + ': ValueError/IndexError\n')
            return None
    ret = ''.join(buf)
    if as_unicode:
        return str(ret, 'utf-8', 'replace')
    else:
        return ret

def file_hash(query):
    """Make hash from filename.

    >>> import config
    >>> config.cache_hash_method = 'asis'
    >>> file_hash('thread_41')
    'thread_41'
    >>> config.cache_hash_method = 'md5'
    >>> file_hash('thread_41')
    'thread_7fc56270e7a70fa81a5935b72eacbe29'
    """
    methods = ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512')
    if config.cache_hash_method not in methods:
        # asis
        return query
    title = file_decode(query)
    type = file_decode_type(query)
    if title is None:
        sys.stderr.write('Invalid filename: %s\n' % query)
        return query
    hash = getattr(hashlib, config.cache_hash_method)()
    hash.update(title)
    return type + '_' + hash.hexdigest()


def _test(*args, **kwargs):
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test()
