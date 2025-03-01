"""Unittest for address utilities.
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

import shingetsu.address as address
import shingetsu.config as config


class AddressTest(unittest.TestCase):
    def test_match_pattern_addr(self):
        pat = address.MatchPattern('::1, 127.0.0.1', '')
        self.assertTrue(pat.matches(ipaddress.ip_address('::1')))
        self.assertTrue(pat.matches(ipaddress.ip_address('127.0.0.1')))
        self.assertFalse(pat.matches(ipaddress.ip_address('2001:db8::1')))
        self.assertFalse(pat.matches(ipaddress.ip_address('192.0.2.1')))

    def test_match_pattern_cidr(self):
        pat = address.MatchPattern('2001:db8::/32, 192.0.2.0/24', '')
        self.assertTrue(pat.matches(ipaddress.ip_address('2001:db8::1')))
        self.assertTrue(pat.matches(ipaddress.ip_address('192.0.2.1')))
        self.assertFalse(pat.matches(ipaddress.ip_address('::1')))
        self.assertFalse(pat.matches(ipaddress.ip_address('127.0.0.1')))

    def test_match_pattern_regexp(self):
        pat = address.MatchPattern('2001:db8::/32', '^::1$|^127')
        self.assertTrue(pat.matches(ipaddress.ip_address('::1')))
        self.assertTrue(pat.matches(ipaddress.ip_address('127.0.0.1')))
        self.assertFalse(pat.matches(ipaddress.ip_address('2001:db8::1')))
        self.assertFalse(pat.matches(ipaddress.ip_address('192.0.2.1')))

    def test_remote_address(self):
        addr = address.RemoteAddress('::1')
        self.assertEqual(str(addr), '::1')

        addr = address.RemoteAddress('127.0.0.1')
        self.assertEqual(str(addr), '127.0.0.1')

        addr = address.RemoteAddress('::ffff:127.0.0.1')
        self.assertEqual(str(addr), '127.0.0.1')

    def test_remote_addr(self):
        orig = config.use_x_forwarded_for
        try:
            config.use_x_forwarded_for = False
            self.assertEqual(
                str(address.remote_addr({
                    'REMOTE_ADDR': '127.0.0.1',
                    'HTTP_X_FORWARDED_FOR': '::1'})),
                '127.0.0.1')

            config.use_x_forwarded_for = True
            self.assertEqual(
                str(address.remote_addr({
                    'REMOTE_ADDR': '127.0.0.1',
                    'HTTP_X_FORWARDED_FOR': '::1'})),
                '::1')
            self.assertEqual(
                str(address.remote_addr({
                    'REMOTE_ADDR': '127.0.0.1',
                    'HTTP_X_FORWARDED_FOR': '127.0.0.1, ::1'})),
                '::1')
        finally:
            config.use_x_forwarded_for = orig

    def test_host_has_addr(self):
        self.assertTrue(address.host_has_addr('192.0.2.1', '192.0.2.1'))
        self.assertFalse(address.host_has_addr('192.0.2.1', '192.0.2.2'))

        self.assertTrue(address.host_has_addr('node.shingetsu.info', '133.125.52.31'))
        self.assertFalse(address.host_has_addr('node.shingetsu.info', '192.0.2.1'))

        self.assertTrue(address.host_has_addr(
            'node.shingetsu.info', '2401:2500:204:1150:133:125:52:31'))
        self.assertFalse(address.host_has_addr('node.shingetsu.info', '2002:db8::1'))

        self.assertFalse(address.host_has_addr('not.found.example.com', '192.0.2.1'))
