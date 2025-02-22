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
import socket
import sys
from http import HTTPStatus

from . import util

__all__ = ['CGI']


class CGI:

    """Base CGI class.

    start(): start the CGI.
    run(): main routine for CGI.

    """

    def __init__(self, environ, start_response):
        self.stdin = environ['wsgi.input']
        self.stderr = sys.stderr
        self.environ = environ
        self.start_response = start_response

    def bytes(self, data):
        if isinstance(data, bytes):
            return data
        if isinstance(data, str):
            return data.encode('utf-8', 'replace')
        return str(data).encode('utf-8', 'replace')

    def body(self, data):
        try:
            iter(data)
        except TypeError:
            yield str(data).encode('utf-8', 'replace')
        try:
            for d in data:
                if isinstance(d, bytes):
                    yield d
                else:
                    yield str(d).encode('utf-8', 'replace')
        finally:
            if hasattr(data, 'close'):
                data.close()

    def send_error(self, status, message=''):
        status_str = f'{status.value} {status.phrase}'
        if not message:
            message = status_str
        self.start_response(status_str, [
            ('Content-Type', 'text/plain;charset=UTF-8')])
        return self.bytes([message])
        
    def start(self, environ, start_response):
        """Start the CGI.
        """
        try:
            return self.run(environ, start_response)
        except (IOError, socket.error, socket.timeout) as err:
            self.stderr.write("%s: %s\n" %
                              (util.get_http_remote_addr(self.environ), err))
            return self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)

    def run(self, environ, start_response):
        """Main routine for CGI.
        """
        return self.send_error(HTTPStatus.NOT_FOUND)

# End of CGI
