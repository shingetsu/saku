"""IP address utilities.
"""
#
# Copyright (c) 2023 shinGETsu Project.
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
import re
import socket

from . import config


class MatchPattern:
    def __init__(self, src, compat):
        self.cidrs = []
        self.regexp = None

        if compat:
            self.regexp = re.compile(compat)
            return

        for s in src.split(','):
            self.cidrs.append(ipaddress.ip_network(s.strip()))

    def matches(self, addr):
        for c in self.cidrs:
            if addr in c:
                return True
        if self.regexp and self.regexp.search(str(addr)):
            return True
        return False

_admin = MatchPattern(config.admin_net, config.admin_old)
_friend = MatchPattern(config.friend, config.friend_old)
_visitor = MatchPattern(config.visitor, config.visitor_old)


class RemoteAddress:
    def __init__(self, addr):
        self.addr = ipaddress.ip_address(addr)
        if hasattr(self.addr, 'ipv4_mapped') and self.addr.ipv4_mapped:
            self.addr = self.addr.ipv4_mapped

    def __str__(self):
        return str(self.addr)

    def is_admin(self):
        return _admin.matches(self.addr)

    def is_friend(self):
        return _friend.matches(self.addr)

    def is_visitor(self):
        return _visitor.matches(self.addr)


def remote_addr(env):
    ra = env['REMOTE_ADDR']
    if config.use_x_forwarded_for and 'HTTP_X_FORWARDED_FOR' in env:
        ra = env['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
    return RemoteAddress(ra)

def host_has_addr(host, addr):
    if host == addr:
        return True
    try:
        info = socket.getaddrinfo(host, 80, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False
    for i in info:
        try:
            ipaddr = i[4][0]
        except IndexError:
            continue
        if addr == ipaddr:
            return True
    return False
