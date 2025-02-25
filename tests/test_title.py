"""Unittest for title utilities.
"""
#
# Copyright (c) 2005 shinGETsu Project.
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

import unittest

import shingetsu.config as config
import shingetsu.title as title


class TitleTest(unittest.TestCase):
    def test_str_encode(self):
        self.assertEqual(title.str_encode('#'), '%23')
        self.assertEqual(title.str_encode(b'#'), '%23')

    def test_str_decode(self):
        self.assertEqual(title.str_decode('%23'), '#')

    def test_file_encode(self):
        self.assertEqual(title.file_encode('foo', 'a#j'), 'foo_61236A')

    def test_file_decode_type(self):
        self.assertEqual(title.file_decode_type('thread_41'), 'thread')

    def test_file_decode(self):
        self.assertEqual(title.file_decode('foo_23'), '#')

    def test_is_valid_file(self):
        self.assertTrue(title.is_valid_file('thread_23'))
        self.assertFalse(title.is_valid_file('foo_23x'))

    def test_file_hash(self):
        orig = config.cache_hash_method
        try:
            config.cache_hash_method = 'asis'
            self.assertEqual(title.file_hash('thread_41'), 'thread_41')
            config.cache_hash_method = 'md5'
            self.assertEqual(title.file_hash('thread_41'),
                             'thread_7fc56270e7a70fa81a5935b72eacbe29')
        finally:
            config.cache_hash_method = orig
