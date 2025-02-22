'''Tiny HTTP server running in another thread.
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

import mimetypes
import os
import re
import socket
import socketserver
import sys
import threading
from http import HTTPStatus
from wsgiref import simple_server

from . import config
from . import middleware
from . import admin_cgi, server_cgi, gateway_cgi, thread_cgi


class ConnectionCounter:
    def __init__(self):
        self.counter = 0
        self.lock = threading.RLock()

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

_counter = ConnectionCounter()


@middleware.head
@middleware.simple_range
@middleware.last_modified
@middleware.gzipped
def root_app(environ, start_response):
    path = environ.get('PATH_INFO', '')
    if not path or path == '/':
        path = config.root_index

    if config.max_connection < int(_counter):
        return send_error(environ, start_response,
                          HTTPStatus.SERVICE_UNAVAILABLE)

    routes = [
        ('/admin.cgi', admin_cgi.CGI),
        ('/server.cgi', server_cgi.CGI),
        ('/gateway.cgi', gateway_cgi.CGI),
        ('/thread.cgi', thread_cgi.CGI),
    ]
    for (route, cgiclass) in routes:
        if path.startswith(route):
            env = environ.copy()
            env['PATH_INFO'] = environ['PATH_INFO'][len(route):]
            try:
                _counter.inclement()
                try:
                    cgiobj = cgiclass(env, start_response)
                    return cgiobj.start(env, start_response)
                except SystemExit as sts:
                    sys.stderr.write("CGI script exit status %s\n", str(sts))
            finally:
                _counter.declement()

    docroot = os.path.abspath('.')
    filepath = os.path.join(docroot, path.lstrip('/'))
    if filepath.startswith(docroot) and os.path.isfile(filepath):
        filetype, _ = mimetypes.guess_type(filepath)
        start_response('200 OK', [('Content-Type', filetype)])
        return environ['wsgi.file_wrapper'](open(filepath, 'rb'), 1024)

    return send_error(environ, start_response, HTTPStatus.NOT_FOUND)

def send_error(environ, start_response, status):
    msg = f'{status.value} {status.phrase}'
    start_response(msg, [('Content-Type', 'text/plain')])
    return [msg.encode('utf-8')]
    

class Httpd(threading.Thread):
    """Tiny HTTP server running in another thread.
    """

    server = None

    def __init__(self):
        threading.Thread.__init__(self)

        if not config.bind_addr or ':' in config.bind_addr:
            Server.address_family = socket.AF_INET6
        
        self.server = simple_server.make_server(
            config.bind_addr,
            config.port,
            root_app,
            server_class=Server,
            handler_class=RequestHandler)

    def run(self):
        os.chdir(config.docroot)
        simple_server.ServerHandler.server_software = config.version
        self.server.serve_forever()


class Server(socketserver.ThreadingMixIn, simple_server.WSGIServer):
    pass


class RequestHandler(simple_server.WSGIRequestHandler):
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
