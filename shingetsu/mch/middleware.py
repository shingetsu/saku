'tiny middleware'

from email import utils as eutils
import gzip
from wsgiref.headers import Headers
import re


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
