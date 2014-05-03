"""Tiny HTTP server supporting threading CGI.
"""
#
# Copyright (c) 2005-2014 shinGETsu Project.
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

import copy
import os
import re
import sys
import urllib.request, urllib.error, urllib.parse
import http.server
import http.server
import socketserver
from threading import RLock

from . import config
from . import admin_cgi, client_cgi, server_cgi, gateway_cgi, thread_cgi

cgimodule = {"admin.cgi": admin_cgi,
             "client.cgi": client_cgi,
             "server.cgi": server_cgi,
             "gateway.cgi": gateway_cgi,
             "thread.cgi": thread_cgi}


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


class HTTPRequestHandler(http.server.CGIHTTPRequestHandler):

    """Tiny HTTP Server.

    Exec CGI if script name ends with .cgi.
    The CGI script runs in same process.
    """
    root_index = "/"

    def parse_request(self):
        r = super().parse_request()
        if self.path == "/":
            self.path = self.root_index
        return r

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

    def run_cgi(self):
        """Execute a CGI script in this process.

        This code is from CGIHTTPServer.py module.
        """
        if config.max_connection < int(_counter):
            self.send_error(503, "Service Unavailable")
            return
        path = self.path
        dir, rest = self.cgi_info

        i = path.find('/', len(dir) + 1)
        while i >= 0:
            nextdir = path[:i]
            nextrest = path[i+1:]

            scriptdir = self.translate_path(nextdir)
            if os.path.isdir(scriptdir):
                dir, rest = nextdir, nextrest
                i = path.find('/', len(dir) + 1)
            else:
                break

        # find an explicit query string, if present.
        i = rest.rfind('?')
        if i >= 0:
            rest, query = rest[:i], rest[i+1:]
        else:
            query = ''
        # dissect the part after the directory name into a script name &
        # a possible additional path, to be stored in PATH_INFO.
        i = rest.find('/')
        if i >= 0:
            script, rest = rest[:i], rest[i:]
        else:
            script, rest = rest, ''
        scriptname = dir + '/' + script
        scriptfile = self.translate_path(scriptname)

        # Reference: http://hoohoo.ncsa.uiuc.edu/cgi/env.html
        # XXX Much of the following could be prepared ahead of time!
        env = dict(copy.deepcopy(os.environ))
        env['SERVER_SOFTWARE'] = self.version_string()
        env['SERVER_NAME'] = self.server.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PROTOCOL'] = self.protocol_version
        env['SERVER_PORT'] = str(self.server.server_port)
        env['REQUEST_METHOD'] = self.command
        uqrest = urllib.parse.unquote(rest)
        env['PATH_INFO'] = uqrest
        env['PATH_TRANSLATED'] = self.translate_path(uqrest)
        env['SCRIPT_NAME'] = scriptname
        if query:
            env['QUERY_STRING'] = query
        host = self.address_string()
        if host != self.client_address[0]:
            env['REMOTE_HOST'] = host
        env['REMOTE_ADDR'] = self.client_address[0]
        # XXX AUTH_TYPE
        # XXX REMOTE_USER
        # XXX REMOTE_IDENT
        if self.headers.get('content-type') is None:
            env['CONTENT_TYPE'] = self.headers.get_content_type()
        else:
            env['CONTENT_TYPE'] = self.headers['content-type']
        length = self.headers.get('content-length')
        if length:
            env['CONTENT_LENGTH'] = length
        referer = self.headers.get('referer')
        if referer:
            env['HTTP_REFERER'] = referer
        accept = []
        for line in self.headers.getallmatchingheaders('accept'):
            if line[:1] in "\t\n\r ":
                accept.append(line.strip())
            else:
                accept = accept + line[7:].split(',')
        env['HTTP_ACCEPT'] = ','.join(accept)
        ua = self.headers.get('user-agent')
        if ua:
            env['HTTP_USER_AGENT'] = ua
        co = filter(None, self.headers.get_all('cookie', []))
        cookie_str = ', '.join(co)
        if cookie_str:
            env['HTTP_COOKIE'] = cookie_str
        # XXX Other HTTP_* headers
        # Since we're setting the env in the parent, provide empty
        # values to override previously set values
        for k in ('QUERY_STRING', 'REMOTE_HOST', 'CONTENT_LENGTH',
                  'HTTP_USER_AGENT', 'HTTP_COOKIE', 'HTTP_REFERER'):
            env.setdefault(k, "")

        # HTTP_* headers require by SAKU
        env["HTTP_ACCEPT_LANGUAGE"] = \
            self.headers.get("Accept-Language", "")
        env["HTTP_ACCEPT_ENCODING"] = \
            self.headers.get("Accept-Encoding", "")
        env["HTTP_HOST"] = self.headers.get('host', '')
        env["HTTP_REFERER"] = self.headers.get("Referer", "")
        if 'X-Forwarded-For' in self.headers:
            env['HTTP_X_FORWARDED_FOR'] = self.headers['X-Forwarded-For']

        decoded_query = query.replace('+', ' ')

        # import CGI module
        try:
            cgiclass = cgimodule[script].CGI
        except KeyError:
            self.send_error(404, "No such CGI script (%s)" % repr(scriptname))
            return
        self.send_response(200, "Script output follows")
        if hasattr(self, 'flush_headers'):
            self.flush_headers()
        elif hasattr(self, '_headers_buffer'):
            self.wfile.write(b"".join(self._headers_buffer))
            self._headers_buffer = []

        # execute script in this process
        try:
            _counter.inclement()
            try:
                cgiobj = cgiclass(stdin=self.rfile,
                                  stdout=self.wfile,
                                  stderr=sys.stderr,
                                  environ=env)
                cgiobj.start()
            except SystemExit as sts:
                self.log_error("CGI script exit status %s", str(sts))
        finally:
            _counter.declement()


class HTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass
