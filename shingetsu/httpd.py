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

import os
import socket
import socketserver
import sys
import threading
from wsgiref import simple_server
from wsgiref.headers import Headers

from . import config
from . import middleware


@middleware.simple_range
@middleware.last_modified
@middleware.gzipped
def root_app(environ, start_response):
    log_request(environ)
    path = environ.get('PATH_INFO', '')

    #routes = [
    #    (board_re, board_app),
    #    (subject_re, subject_app),
    #    (thread_re, thread_app),
    #    (post_comment_re, post.post_comment_app),
    #    (head_re, head_app)
    #]
    #try:
    #    for (route, app) in routes:
    #        m = route.match(path)
    #        if m:
    #            env['mch.path_match'] = m
    #            return app(env, resp)

    start_response("404 Not Found", [('Content-Type', 'text/plain')])
    return [b'404 Not Found']


def log_request(env):  # same as saku's log format
    fmt = '{host}<>{proxy}<>{method} {path} {protocol}<>{referer}<>{ua}'
    msg = fmt.format(host=env['REMOTE_ADDR'],
                     proxy=env.get('HTTP_X_FORWARDED_FOR', 'direct'),
                     method=env['REQUEST_METHOD'],
                     path=env['PATH_INFO'],
                     protocol=env['SERVER_PROTOCOL'],
                     referer=env.get('REFERER', ''),
                     ua=env.get('HTTP_USER_AGENT', ''))
    sys.stdout.write(msg)

class Httpd(threading.Thread):
    """Tiny HTTP server running in another thread.
    """

    server = None

    def __init__(self):
        threading.Thread.__init__(self)

        class Server(socketserver.ThreadingMixIn,
                     simple_server.WSGIServer):
            pass

        if not config.bind_addr or ':' in config.bind_addr:
            Server.address_family = socket.AF_INET6
        Server.server_version = config.version
        
        self.server = simple_server.make_server(
            config.bind_addr,
            config.port,
            root_app,
            server_class=Server)

    def run(self):
        os.chdir(config.docroot)
        self.server.serve_forever()
