"""tiny middleware
"""
#
# Copyright (c) 2014 shinGETsu Project.
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

import gzip
import re
from email import utils as eutils
from wsgiref.headers import Headers


# use as decorator.
def gzipped(app):
    def newapp(environ, start_response):
        resp = {}
        def capture(s, h):
            resp['status'] = s
            resp['headers'] = h

        body = app(environ, capture)
        status = resp['status']
        headers = Headers(resp['headers'])

        already = 'Content-Encoding' in headers
        accepted = 'gzip' in environ.get('HTTP_ACCEPT_ENCODING', '')
        if not accepted or already:
            # no compress
            start_response(status, list(headers.items()))
            return body

        content = gzip.compress(b''.join(body))
        if hasattr(body, 'close'):
            body.close()
        headers['Content-Encoding'] = 'gzip'
        start_response(status, list(headers.items()))
        return [content]

    return newapp


def last_modified(app):
    def newapp(environ, start_response):
        resp = {}
        def capture(s, h):
            resp['status'] = s
            resp['headers'] = h

        raw = app(environ, capture)
        status = resp['status']
        headers = Headers(resp['headers'])

        if (not 'Last-Modified' in headers
            or not environ.get('HTTP_IF_MODIFIED_SINCE')):
            start_response(status, list(headers.items()))
            return raw

        last_m = eutils.parsedate(headers['Last-Modified'])
        since_m = eutils.parsedate(environ['HTTP_IF_MODIFIED_SINCE'])
        if since_m < last_m:
            start_response(status, list(headers.items()))
            return raw
        else:
            start_response('304 Not Modified', list(headers.items()))
            if hasattr(raw, 'close'):
                raw.close()
            return [b'']

    return newapp


def simple_range(app):
    def newapp(environ, start_response):
        resp = {}
        def capture(s, h):
            resp['status'] = s
            resp['headers'] = h

        raw = app(environ, capture)
        status = resp['status']
        headers = Headers(resp['headers'])

        headers.setdefault('Accept-Range', 'bytes')
        range = environ.get('HTTP_RANGE')

        if (range is None
            or ',' in range  # not deal with multi-part range
            or not status.startswith('2')):  # not success status
            start_response(status, list(headers.items()))
            return raw

        def error_416():
            start_response('416 Requested Range Not Satisfiable',
                           list(headers.items()))
            if hasattr(raw, 'close'):
                raw.close()
            return [b'']

        m = re.match(r'bytes=([0-9]+)?-([0-9]+)?', range)
        if not m or (not m.group(1) and not m.group(2)):
            return error_416()

        content = b''.join(raw)
        begin = int(m.group(1)) if m.group(1) else None
        end = int(m.group(2)) if m.group(2) else None

        # because 0 is False
        has_begin = begin is not None
        has_end = end is not None

        if (has_begin and has_end) and end < begin:
            return error_416()
        if has_end and len(content) <= end:
            return error_416()
        if has_begin and len(content) <= begin :
            return error_416()

        if has_begin and has_end:
            # bytes=begin-end
            c_range = 'bytes {}-{}/{}'.format(begin, end, len(content))
            body = content[begin:end+1]

        elif has_begin:
            # bytes=begin-
            c_range = 'bytes {}-{}/{}'.format(begin, len(content)-1,
                                              len(content))
            body = content[begin:]

        else:
            # bytes=-end
            c_range = 'bytes {}-{}/{}'.format(len(content)-end,
                                              len(content)-1, len(content))
            body = content[len(content)-end:]

        headers['Content-Range'] = c_range
        start_response('206 Partial Content', list(headers.items()))
        if hasattr(raw, 'close'):
            raw.close()
        return [body]

    return newapp


def head(app):
    def newapp(environ, start_response):
        resp = {}
        def capture(s, h):
            resp['status'] = s
            resp['headers'] = h

        body = app(environ, capture)
        status = resp['status']

        if environ['REQUEST_METHOD'].upper() != 'HEAD':
            start_response(status, resp['headers'])
            return body

        headers = Headers(resp['headers'])
        headers['Content-Length'] = str(sum([len(b) for b in body]))
        start_response(status, list(headers.items()))
        return []

    return newapp
