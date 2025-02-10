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

import shingetsu.node as node


class NodeTest(unittest.TestCase):
    def test_node_init_dnsname(self):
        n = node.Node('example.com:8000/server.cgi')
        self.assertEqual(n.nodestr, 'example.com:8000/server.cgi')
        self.assertFalse(n.isv6)

    def test_node_init_dnsname_nodestr_xstring(self):
        n = node.Node('example.com:8000+server.cgi')
        self.assertEqual(n.nodestr, 'example.com:8000/server.cgi')
        self.assertFalse(n.isv6)

    def test_node_init_dnsname(self):
        n = node.Node(host='example.com', port=8000, path='/server.cgi')
        self.assertEqual(n.nodestr, 'example.com:8000/server.cgi')
        self.assertFalse(n.isv6)

    def test_node_init_dnsname_xstring(self):
        n = node.Node(host='example.com', port=8000, path='+server.cgi')
        self.assertEqual(n.nodestr, 'example.com:8000/server.cgi')
        self.assertFalse(n.isv6)

    def test_node_init_ipv4(self):
        n = node.Node('192.0.2.1:8000/server.cgi')
        self.assertEqual(n.nodestr, '192.0.2.1:8000/server.cgi')
        self.assertFalse(n.isv6)

    def test_node_init_ipv4_nodestr_xstring(self):
        n = node.Node('192.0.2.1:8000+server.cgi')
        self.assertEqual(n.nodestr, '192.0.2.1:8000/server.cgi')
        self.assertFalse(n.isv6)

    def test_node_init_ipv4(self):
        n = node.Node(host='192.0.2.1', port=8000, path='/server.cgi')
        self.assertEqual(n.nodestr, '192.0.2.1:8000/server.cgi')
        self.assertFalse(n.isv6)

    def test_node_init_ipv4_xstring(self):
        n = node.Node(host='192.0.2.1', port=8000, path='+server.cgi')
        self.assertEqual(n.nodestr, '192.0.2.1:8000/server.cgi')
        self.assertFalse(n.isv6)

    def test_node_init_ipv6(self):
        n = node.Node('[2001:db8::1]:8000/server.cgi')
        self.assertEqual(n.nodestr, '[2001:db8::1]:8000/server.cgi')
        self.assertTrue(n.isv6)

    def test_node_init_ipv6_nodestr_xstring(self):
        n = node.Node('[2001:db8::1]:8000+server.cgi')
        self.assertEqual(n.nodestr, '[2001:db8::1]:8000/server.cgi')
        self.assertTrue(n.isv6)

    def test_node_init_ipv6(self):
        n = node.Node(host='[2001:db8::1]', port=8000, path='/server.cgi')
        self.assertEqual(n.nodestr, '[2001:db8::1]:8000/server.cgi')
        self.assertTrue(n.isv6)

    def test_node_init_ipv6_xstring(self):
        n = node.Node(host='[2001:db8::1]', port=8000, path='+server.cgi')
        self.assertEqual(n.nodestr, '[2001:db8::1]:8000/server.cgi')
        self.assertTrue(n.isv6)

    def test_node_init_ipv6_raw(self):
        n = node.Node(host='2001:db8::1', port=8000, path='/server.cgi')
        self.assertEqual(n.nodestr, '[2001:db8::1]:8000/server.cgi')
        self.assertTrue(n.isv6)

    def test_node_init_ipv6_raw_xstring(self):
        n = node.Node(host='2001:db8::1', port=8000, path='+server.cgi')
        self.assertEqual(n.nodestr, '[2001:db8::1]:8000/server.cgi')
        self.assertTrue(n.isv6)


def _test():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NodeTest))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.errors or result.failures:
        sys.exit(1)


if __name__ == "__main__":
    _test()
