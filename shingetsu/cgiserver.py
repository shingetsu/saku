"""Tiny HTTP server supporting threading CGI.
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

import re
import sys
import http.server
import socketserver
from threading import RLock

from . import config
from . import cgirunner
from . import admin_cgi, server_cgi, gateway_cgi, thread_cgi

_cgimodule = {
    "admin.cgi": admin_cgi,
    "server.cgi": server_cgi,
    "gateway.cgi": gateway_cgi,
    "thread.cgi": thread_cgi,
}


class ConnectionCounter:
    '''Connection Counter.
    '''
    def __init__(self):
        self.counter = 0
        self.lock = RLock()

    def inclement(self):
        try:
            self.lock.acquire(True)
            self.counter += 1
        finally:
            self.lock.release()

    def declement(self):
        try:
            self.lock.acquire(True)
            self.counter -= 1
        finally:
            self.lock.release()

    def __int__(self):
        return self.counter

# End of ConnectionCounter

_counter = ConnectionCounter()


class HTTPRequestHandler(cgirunner.CGIRunnerMixin, http.server.CGIHTTPRequestHandler):
    cgimodule = _cgimodule
    counter = _counter

    """Tiny HTTP Server.

    Exec CGI if script name ends with .cgi.
    The CGI script runs in same process.
    """
    root_index = "/"

    def parse_request(self):
        ok = super().parse_request()
        if not ok:
            return False
        found = re.search(r'^/+([?].*)?$', self.path)
        if found:
            if found.group(1):
                self.path = self.root_index + found.group(1)
            else:
                self.path = self.root_index
        return True

    def is_cgi(self):
        """Test request URI is *.cgi."""
        found = re.search(r"^(.*?)/([^/]+\.cgi.*)", self.path)
        if found:
            self.cgi_info = found.groups()
            return True
        else:
            return False

    def address_string(self):
        host, port = self.client_address[:2]
        m = re.search(r'^::ffff:([\d.]+)$', host)
        if m:
            return m.group(1)
        return host

    def log_request(self, code='-', size='-'):
        buf = [self.requestline]
        if hasattr(self, "headers"):
            buf.extend((self.headers.get("Referer", ""),
                        self.headers.get("User-Agent", "")))
        self.log_message("%s", "<>".join(buf))

    def log_message(self, format, *args):
        if hasattr(self, 'headers'):
            proxy_client = self.headers.get('X-Forwarded-For', 'direct')
        else:
            proxy_client = '?'
        sys.stderr.write('%s<>%s<>%s\n' %
                         (self.address_string(),
                          proxy_client,
                          format % args))

    def copyfile(self, source, outputfile):
        #XXX parent method does not work on some environment
        while True:
            c = source.read(1024)
            if c == b'':
                break
            outputfile.write(c)


class HTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass
