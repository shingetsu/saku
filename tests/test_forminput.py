"""Unittest for forminput.
"""
#
# Copyright (c) 2025 shinGETsu Project.
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

import io
import unittest

import shingetsu.forminput as forminput

multipart = b'''------WebKitFormBoundary8Anl9xG5LafoG08m
Content-Disposition: form-data; name="baz"

BAZ
------WebKitFormBoundary8Anl9xG5LafoG08m
Content-Disposition: form-data; name="qux"

QUX1
------WebKitFormBoundary8Anl9xG5LafoG08m
Content-Disposition: form-data; name="qux"

QUX2
------WebKitFormBoundary8Anl9xG5LafoG08m
Content-Disposition: form-data; name="attach"; filename="test.txt"
Content-Type: text/plain

1234

------WebKitFormBoundary8Anl9xG5LafoG08m
'''


class FormInputTest(unittest.TestCase):
    def test_read_from_query_string(self):
        env = {
            'REQUEST_METHOD': 'GET',
            'QUERY_STRING': 'foo=FOO&bar=BAR1&bar=BAR2'
        }
        form = forminput.read(env, io.StringIO())
        self.assertEqual(form.getfirst('foo'), 'FOO')
        self.assertEqual(form.getfirst('bar'), 'BAR1')
        self.assertEqual(form.getlist('bar'), ['BAR1', 'BAR2'])
        self.assertEqual(form.getfirst('not_found'), None) 
        self.assertEqual(form.getlist('not_found'), []) 

    def test_read_from_body(self):
        body = 'baz=BAZ&qux=QUX1&qux=QUX2'
        env = {
            'REQUEST_METHOD': 'POST',
            'QUERY_STRING': 'foo=FOO&bar=BAR1&bar=BAR2',
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': str(len(body))
        }
        form = forminput.read(env, io.StringIO(body))
        self.assertEqual(form.getfirst('foo'), 'FOO')
        self.assertEqual(form.getfirst('bar'), 'BAR1')
        self.assertEqual(form.getfirst('baz'), 'BAZ')
        self.assertEqual(form.getfirst('qux'), 'QUX1')
        self.assertEqual(form.getlist('qux'), ['QUX1', 'QUX2'])

    def test_read_from_multipart(self):
        env = {
            'REQUEST_METHOD': 'POST',
            'QUERY_STRING': 'foo=FOO&bar=BAR1&bar=BAR2',
            'CONTENT_TYPE': ('application/multipart/form-data;'
                             + ' boundary=----WebKitFormBoundary8Anl9xG5LafoG08m'),
            'CONTENT_LENGTH': str(len(multipart))
        }
        form = forminput.read(env, io.BytesIO(multipart))
        self.assertEqual(form.getfirst('foo'), 'FOO')
        self.assertEqual(form.getfirst('bar'), 'BAR1')
        self.assertEqual(form.getfirst('baz'), 'BAZ')
        self.assertEqual(form.getfirst('qux'), 'QUX1')
        self.assertEqual(form.getlist('qux'), ['QUX1', 'QUX2'])
        file = form.getfile('attach')
        self.assertEqual(file.filename, 'test.txt')
        self.assertEqual(file.value, b'1234\n')
        self.assertIsNone(form.getfile('not_found'))
