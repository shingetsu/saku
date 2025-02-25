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

import unittest

import shingetsu.node as node


class NodeTest(unittest.TestCase):
    def test_node_init_dnsname_ipv4(self):
        n = node.Node('node-ipv4.shingetsu.info:8000/server.cgi')
        self.assertEqual(n.nodestr, 'node-ipv4.shingetsu.info:8000/server.cgi')
        self.assertFalse(n.is_ipv6())
        self.assertFalse(n.is_ipv6())

    def test_node_init_dnsname_ipv4_nodestr_xstring(self):
        n = node.Node('node-ipv4.shingetsu.info:8000+server.cgi')
        self.assertEqual(n.nodestr, 'node-ipv4.shingetsu.info:8000/server.cgi')
        self.assertFalse(n.is_ipv6())

    def test_node_init_dnsname_ipv4(self):
        n = node.Node(host='node-ipv4.shingetsu.info', port=8000, path='/server.cgi')
        self.assertEqual(n.nodestr, 'node-ipv4.shingetsu.info:8000/server.cgi')
        self.assertFalse(n.is_ipv6())

    def test_node_init_dnsname_ipv4_xstring(self):
        n = node.Node(host='node-ipv4.shingetsu.info', port=8000, path='+server.cgi')
        self.assertEqual(n.nodestr, 'node-ipv4.shingetsu.info:8000/server.cgi')
        self.assertFalse(n.is_ipv6())

    def test_node_init_dnsname_ipv6(self):
        n = node.Node('node.shingetsu.info:8000/server.cgi')
        self.assertEqual(n.nodestr, 'node.shingetsu.info:8000/server.cgi')
        self.assertTrue(n.is_ipv6())
        self.assertTrue(n.is_ipv6())

    def test_node_init_dnsname_ipv6_nodestr_xstring(self):
        n = node.Node('node.shingetsu.info:8000+server.cgi')
        self.assertEqual(n.nodestr, 'node.shingetsu.info:8000/server.cgi')
        self.assertTrue(n.is_ipv6())

    def test_node_init_dnsname_ipv6(self):
        n = node.Node(host='node.shingetsu.info', port=8000, path='/server.cgi')
        self.assertEqual(n.nodestr, 'node.shingetsu.info:8000/server.cgi')
        self.assertTrue(n.is_ipv6())

    def test_node_init_dnsname_ipv6_xstring(self):
        n = node.Node(host='node.shingetsu.info', port=8000, path='+server.cgi')
        self.assertEqual(n.nodestr, 'node.shingetsu.info:8000/server.cgi')
        self.assertTrue(n.is_ipv6())

    def test_node_init_ipv4(self):
        n = node.Node('192.0.2.1:8000/server.cgi')
        self.assertEqual(n.nodestr, '192.0.2.1:8000/server.cgi')
        self.assertFalse(n.is_ipv6())

    def test_node_init_ipv4_nodestr_xstring(self):
        n = node.Node('192.0.2.1:8000+server.cgi')
        self.assertEqual(n.nodestr, '192.0.2.1:8000/server.cgi')
        self.assertFalse(n.is_ipv6())

    def test_node_init_ipv4(self):
        n = node.Node(host='192.0.2.1', port=8000, path='/server.cgi')
        self.assertEqual(n.nodestr, '192.0.2.1:8000/server.cgi')
        self.assertFalse(n.is_ipv6())

    def test_node_init_ipv4_xstring(self):
        n = node.Node(host='192.0.2.1', port=8000, path='+server.cgi')
        self.assertEqual(n.nodestr, '192.0.2.1:8000/server.cgi')
        self.assertFalse(n.is_ipv6())

    def test_node_init_ipv6(self):
        n = node.Node('[2001:db8::1]:8000/server.cgi')
        self.assertEqual(n.nodestr, '[2001:db8::1]:8000/server.cgi')
        self.assertTrue(n.is_ipv6())

    def test_node_init_ipv6_nodestr_xstring(self):
        n = node.Node('[2001:db8::1]:8000+server.cgi')
        self.assertEqual(n.nodestr, '[2001:db8::1]:8000/server.cgi')
        self.assertTrue(n.is_ipv6())

    def test_node_init_ipv6(self):
        n = node.Node(host='[2001:db8::1]', port=8000, path='/server.cgi')
        self.assertEqual(n.nodestr, '[2001:db8::1]:8000/server.cgi')
        self.assertTrue(n.is_ipv6())

    def test_node_init_ipv6_xstring(self):
        n = node.Node(host='[2001:db8::1]', port=8000, path='+server.cgi')
        self.assertEqual(n.nodestr, '[2001:db8::1]:8000/server.cgi')
        self.assertTrue(n.is_ipv6())

    def test_node_init_ipv6_raw(self):
        n = node.Node(host='2001:db8::1', port=8000, path='/server.cgi')
        self.assertEqual(n.nodestr, '[2001:db8::1]:8000/server.cgi')
        self.assertTrue(n.is_ipv6())

    def test_node_init_ipv6_raw_xstring(self):
        n = node.Node(host='2001:db8::1', port=8000, path='+server.cgi')
        self.assertEqual(n.nodestr, '[2001:db8::1]:8000/server.cgi')
        self.assertTrue(n.is_ipv6())
