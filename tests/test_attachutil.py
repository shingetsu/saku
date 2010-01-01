"""Unittest for Attached Files Utilities.
"""
#
# Copyright (c) 2009 shinGETsu Project.
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

import imghdr
import sys
import unittest

sys.path.append('.')

import shingetsu.attachutil as attachutil

__version__ = '$Revision$'


class ImghdrMock:
    def __init__(self, type):
        self.type = type
        self.path = None

    def what(self, path):
        self.path = path
        return self.type


class AttachUtilTest(unittest.TestCase):
    def tearDown(self):
        attachutil._imghdr = imghdr

    def test_is_valid_image_true(self):
        attachutil._imghdr = ImghdrMock('png')
        self.assertTrue(attachutil.is_valid_image('image/png', 'foo'))
        self.assertEquals('foo', attachutil._imghdr.path)

    def test_is_valid_image_type_isnot_image(self):
        attachutil._imghdr = ImghdrMock('png')
        self.assertFalse(attachutil.is_valid_image('text/html', 'foo'))
        self.assertEquals('foo', attachutil._imghdr.path)
 
    def test_is_valid_image_file_isnot_image(self):
        attachutil._imghdr = ImghdrMock(None)
        self.assertFalse(attachutil.is_valid_image('image/png', 'foo'))
        self.assertEquals('foo', attachutil._imghdr.path)

    def test_is_valid_image_not_same_image_type(self):
        attachutil._imghdr = ImghdrMock('jpeg')
        self.assertFalse(attachutil.is_valid_image('image/png', 'foo'))
        self.assertEquals('foo', attachutil._imghdr.path)


def _test():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AttachUtilTest))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.errors or result.failures:
        sys.exit(1)


if __name__ == '__main__':
    _test()
