"""Unittest for Node.
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

import os.path
import sys
import unittest

sys.path.insert(0, ".")

from shingetsu.basecgi import OutputBuffer

class OutputBufferTest(unittest.TestCase):
    def test_lines(self):
        buf = OutputBuffer()
        buf.write('Content-Type: text/plain\r\n')
        buf.write('\r\n')
        buf.write('Hello World')
        self.assertEqual(buf.status, '200 OK')
        self.assertEqual(buf.headers, [('Content-Type', 'text/plain')])
        self.assertEqual(buf.body, [b'Hello World'])

    def test_chunk(self):
        buf = OutputBuffer()
        buf.write(
            'Content-Type: text/plain\r\n'
            '\r\n'
            'Hello World')
        self.assertEqual(buf.status, '200 OK')
        self.assertEqual(buf.headers, [('Content-Type', 'text/plain')])
        self.assertEqual(buf.body, [b'Hello World'])

    def test_status(self):
        buf = OutputBuffer()
        buf.write('404 Not Found\r\n')
        buf.write('Content-Type: text/plain\r\n')
        buf.write('\r\n')
        buf.write('Hello World')
        self.assertEqual(buf.status, '404 Not Found')
        self.assertEqual(buf.headers, [('Content-Type', 'text/plain')])
        self.assertEqual(buf.body, [b'Hello World'])


def _test():
    suite = unittest.TestSuite()
    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(OutputBufferTest))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.errors or result.failures:
        sys.exit(1)


if __name__ == "__main__":
    _test()
