"""Unittest for apollo signature module.
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

import ipaddress
import unittest

import shingetsu.apollo as apollo
import shingetsu.util as util


class ApolloTest(unittest.TestCase):
    def test_sign(self):
        pubkey, prikey = apollo.key_pair('password')
        md = util.md5digest('text')
        sign = apollo.sign(md, pubkey, prikey)
        self.assertEqual(pubkey,
            'lUQ3+GeVo87zMGk2Mau8GdroAyXS3UZDrYO3w2iEEkIFLo0OD0JNQQXCiNqPUNTyBwoa8fT4DwAnc7C+WBsKHA')
        self.assertEqual(prikey,
            'BuWGiEhQbZarDke7HEYOPVdQTp9uN5BDblXdcYGxx0w7DYSqInF6PrYCOHjWnAAms//1NfOQlPBD5vWwl8F0AA')
        self.assertEqual(sign,
            'c0BJVtXFitLg0T3cpHQ+K+ZJgIL63GLSpq6huhE4O1mq7rM6xLw4aLJ48EkxQZOk1Tm7qjou+Z7GQDpc874ABA')

    def test_verify(self):
        md = util.md5digest('text')
        sign = \
            'c0BJVtXFitLg0T3cpHQ+K+ZJgIL63GLSpq6huhE4O1mq7rM6xLw4aLJ48EkxQZOk1Tm7qjou+Z7GQDpc874ABA'
        pubkey = \
            'lUQ3+GeVo87zMGk2Mau8GdroAyXS3UZDrYO3w2iEEkIFLo0OD0JNQQXCiNqPUNTyBwoa8fT4DwAnc7C+WBsKHA'
        self.assertTrue(apollo.verify(md, sign, pubkey))
        self.assertEqual(apollo.cut_key(pubkey), 'acx4KueICfB')
