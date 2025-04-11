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

import unittest

import shingetsu.attachutil as attachutil


def get_image_type(suffix):
    def image_type(path):
        return suffix
    return image_type

class AttachUtilTest(unittest.TestCase):
    orig_image_type = None

    def setUp(self):
        self.orig_image_type = attachutil.image_type

    def tearDown(self):
        attachutil.image_type = self.orig_image_type

    def test_get_wellknown_suffix(self):
        self.assertEqual(attachutil.get_wellknown_suffix(''), 'txt')
        self.assertEqual(attachutil.get_wellknown_suffix('x'), 'txt')
        self.assertEqual(attachutil.get_wellknown_suffix('x.png'), 'png')
        self.assertEqual(attachutil.get_wellknown_suffix('x.y.png'), 'png')
        self.assertEqual(attachutil.get_wellknown_suffix('x.php'), 'txt')
        self.assertEqual(attachutil.get_wellknown_suffix('x.shingetsu'), 'txt')

    def test_seem_html(self):
        self.assertTrue(attachutil.seem_html('x.html'))
        self.assertTrue(attachutil.seem_html('x.xhtml'))
        self.assertFalse(attachutil.seem_html('x.txt'))

    def test_is_valid_image_true(self):
        attachutil.image_type = get_image_type("png")
        self.assertTrue(attachutil.is_valid_image("image/png", "foo"))

    def test_is_valid_image_type_isnot_image(self):
        attachutil.image_type = get_image_type("png")
        self.assertFalse(attachutil.is_valid_image("text/html", "foo"))

    def test_is_valid_image_file_isnot_image(self):
        attachutil.image_type = get_image_type(None)
        self.assertFalse(attachutil.is_valid_image("image/png", "foo"))

    def test_is_valid_image_not_same_image_type(self):
        attachutil.image_type = get_image_type("jpeg")
        self.assertFalse(attachutil.is_valid_image("image/png", "foo"))

    def test_is_valid_image_none(self):
        attachutil.image_type = get_image_type("jpeg")
        self.assertFalse(attachutil.is_valid_image("image/png", None))
