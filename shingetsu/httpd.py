'''Tiny HTTP server running in another thread.
'''
#
# Copyright (c) 2005,2006 shinGETsu Project.
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
# $Id$
#

import os
import threading
import BaseHTTPServer
import SimpleHTTPServer

import config
import LightCGIHTTPServer

__version__ = "$Revision$"


class Httpd(threading.Thread):

    """Tiny HTTP server running in another thread."""

    daemon = None

    def __init__(self):
        threading.Thread.__init__(self)
        HandlerClass = LightCGIHTTPServer.HTTPRequestHandler

        ServerClass = LightCGIHTTPServer.HTTPServer
        server_address = ("", config.port)
        HandlerClass.server_version = config.version
        HandlerClass.root_index = config.root_index
        self.daemon = ServerClass(server_address, HandlerClass)

    def run(self):
        os.chdir(config.docroot)
        self.daemon.serve_forever()
