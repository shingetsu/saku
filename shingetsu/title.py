'''Title Utilities.
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

import hashlib
import urllib.parse
import sys

from shingetsu import config

__all__ = ['str_encode', 'str_decode', 'file_encode', 'file_decode',
           'is_valid_file']

_allchars_quoter = urllib.parse.Quoter('')
_allchars_quoter.safe = []


def str_encode(query):
    '''Encode for URI.

    >>> str_encode('#')
    '%23'
    >>> str_encode(b'#')
    '%23'
    '''
    if not isinstance(query, bytes):
        query = str(query)
    return urllib.parse.quote(query)

def str_decode(query):
    '''Decode URI.

    >>> str_decode('%23')
    '#'
    '''
    return urllib.parse.unquote(query)

def file_encode(type, query):
    '''Encode for filename.

    >>> file_encode('foo', 'a')
    'foo_61'
    >>> file_encode('foo', '#')
    'foo_23'
    '''
    buf = [type, '_']
    if isinstance(query, str):
        query = query.encode('utf-8', 'replace')
    quoted = ''.join([_allchars_quoter[char] for char in query])
    return ''.join([type, '_', quoted.replace('%', '')])
                   
def file_decode_type(query, type=None):
    """Decode file type.

    >>> file_decode_type('thread_41')
    'thread'
    """
    q = query.split('_')
    if len(q) < 2:
        return type
    return q[0]

def file_decode(query, type=None):
    '''Decode filename.

    >>> file_decode('foo_23')
    '#'
    '''
    q = query.split('_')
    if len(q) < 2:
        return None
    if type is not None:
        type = q[0]
    query = q[1]
    buf = []
    for i in range(0, len(query), 2):
        try:
            buf.append(int(query[i:i+2], 16).to_bytes(1, 'big'))
        except (ValueError, IndexError):
            sys.stderr.write(query + ': ValueError/IndexError\n')
            return None
    return str(b''.join(buf), 'utf-8', 'replace')

def is_valid_file(query, type=None):
    '''Validate filename.

    >>> is_valid_file('thread_23')
    True
    >>> is_valid_file('foo_23x')
    False
    '''
    q = query.split('_')
    if len(q) < 2:
        return False
    if type is not None and q[0] != type:
        return False
    query = q[1]
    buf = []
    for i in range(0, len(query), 2):
        try:
            buf.append(int(query[i:i+2], 16).to_bytes(1, 'big'))
        except (ValueError, IndexError):
            return False
    try:
        str(b''.join(buf), 'utf-8', 'strict')
        return True
    except UnicodeError:
        return False

def file_hash(query):
    """Make hash from filename.

    >>> import shingetsu.config
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
    hash.update(title.encode('utf-8', 'replace'))
    return type + '_' + hash.hexdigest()


def _test(*args, **kwargs):
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test()
