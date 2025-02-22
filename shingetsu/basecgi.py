'''Base CGI module.
'''
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

import os
import sys

from . import util

__all__ = ['CGI']


class OutputBuffer:
    def __init__(self):
        self.writing_headers = True
        self.status = '200 OK'
        self.headers = []
        self.body = []

    def write(self, msg):
        if isinstance(msg, str):
            msg = msg.encode('utf-8', 'replace')
        if not self.writing_headers:
            self.body.append(msg)
            return

        for line in msg.splitlines(True):
            if not line:
                continue
            elif not self.writing_headers:
                self.body.append(line)
            elif not self.headers and b':' not in line:
                self.status = line.strip()
            elif line == b'\n' or line == b'\r\n':
                self.writing_headers = False
            else:
                line_str = line.decode('utf-8', 'replace')
                k, v = line_str.strip().split(':', 1)
                self.headers.append((k.strip(), v.strip()))

# End of OutputBuffer


class CGI:

    """Base CGI class.

    start(): start the CGI.
    run(): main routine for CGI.

    """

    def __init__(self, environ):
        self.stdin = environ['wsgi.input']
        self.stdout = OutputBuffer()
        self.stderr = sys.stderr
        self.environ = environ

    def start(self):
        """Start the CGI."""
        import socket
        try:
            self.run()
        except (IOError, socket.error, socket.timeout) as strerror:
            self.stderr.write("%s: %s\n" %
                              (util.get_http_remote_addr(self.environ), strerror))

    def run(self):
        """Main routine for CGI."""
        pass

# End of CGI
