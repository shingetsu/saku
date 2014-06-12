'2ch like dat interface'

from wsgiref import simple_server
import threading
import re
import datetime
from wsgiref.headers import Headers
from email import utils as eutils
import threading
import collections
import socketserver


from shingetsu import cache
from shingetsu import title
from shingetsu import config
from shingetsu import gateway

from . import post
from . import middleware
from . import dat
from . import utils
from . import keylib


board_re= re.compile(r'/([^/]+)/$')
thread_re = re.compile(r'/([^/]+)/dat/([^.]+)\.dat')
subject_re = re.compile(r'/([^/]+)/subject.txt')
post_comment_re = re.compile(r'/test/bbs.cgi')


#@middleware.simple_range
@middleware.last_modified
@middleware.gzipped
def dat_app(env, resp):
    # utils.log('dat_app')
    addr = env.get('REMOTE_ADDR', '')
    env['shingetsu.isadmin'] = bool(config.re_admin.match(addr))
    env['shingetsu.isfriend'] = bool(config.re_friend.match(addr))
    env['shingetsu.isvisitor'] = bool(config.re_visitor.match(addr))
    isopen = (env['shingetsu.isadmin'] or env['shingetsu.isfriend']
              or env['shingetsu.isvisitor'])

    utils.log_request(env)
    path = env.get('PATH_INFO', '')
    if not isopen:
        resp('403 Forbidden', [('Content-Type', 'text/plain')])
        return [b'403 Forbidden']

    try:
        if board_re.match(path):
            return board_app(env, resp)

        if subject_re.match(path):
            return subject_app(env, resp)

        if thread_re.match(path):
            return thread_app(env, resp)

        if post_comment_re.match(path) and env['REQUEST_METHOD'] == 'POST':
            return post.post_comment_app(env, resp)

    except keylib.DatkeyNotFound:
        pass
    resp("404 Not Found", [('Content-Type', 'text/plain')])
    return [b'404 Not Found']



def check_get_cache(env):
    if not (env['shingetsu.isfriend'] or env['shingetsu.isadmin']):
        return False
    agent = env.get("HTTP_USER_AGENT", "")
    if re.search(config.robot, agent):
        return False
    return True


_lock = threading.Lock()
_update_counter = collections.defaultdict(int)
_UPDATE_COUNT = 4  # once every _UPDATE_COUNT times
def _count_is_update(thread_key):
    with _lock:
        try:
            _update_counter[thread_key] += 1
            return _update_counter[thread_key] == _UPDATE_COUNT
        finally:
            _update_counter[thread_key] %= _UPDATE_COUNT


def board_app(env, resp):
    path = env['PATH_INFO']
    m = board_re.match(path)
    board = m.group(1)
    message = gateway.search_message(env.get('HTTP_ACCEPT_LANGUAGE', 'ja'))

    headers = Headers([('Content-Type', 'text/html; charset=Shift_JIS')])
    resp("200 OK", headers.items())

    html = [
        '<!DOCTYPE html>',
        '<html><head>',
        '<meta http-equiv="content-type" content="text/html; charset=Shift_JIS">',
        '<title>%s - %s</title>' % (message['logo'], message['description']),
        '<meta name="description" content="%s - %s">' % (message['logo'], message['description']),
        '</head><body>',
        '<h1>%s - %s</h1>' % (message['logo'], message['description']),
        '</body></html>',
    ]
    return ((c + '\n').encode('sjis', 'ignore') for c in html)


def thread_app(env, resp):
    path = env['PATH_INFO']
    # utils.log('thread_app', path)
    m = thread_re.match(path)
    board, datkey = m.group(1), m.group(2)

    key = keylib.get_filekey(datkey)
    data = cache.Cache(key)
    data.load()
    if check_get_cache(env):
        if _count_is_update(key):
            data.search()  # update thread

    if not data.exists():
        resp('404 Not Found', [('Content-Type', 'text/plain; charset=Shift_JIS')])
        return [b'404 Not Found']

    thread = dat.make_dat(data, env, board)

    headers = Headers([('Content-Type', 'text/plain; charset=Shift_JIS')])
    last_m = eutils.formatdate(data.stamp)
    headers['Last-Modified'] = last_m
    resp("200 OK", headers.items())

    return (c.encode('sjis', 'ignore') for c in thread)



def subject_app(env, resp):
    # utils.log('subject_app')
    path = env['PATH_INFO']
    board = subject_re.match(path).group(1)

    cachelist = cache.CacheList()
    subjects = []
    last_stamp = 0
    for c in cachelist:
        c.load()
        if len(c) == 0:
            continue

        if last_stamp < c.stamp:
            last_stamp = c.stamp

        subjects.append('{key}.dat<>{title} ({num})\n'.format(
            key=keylib.get_datkey(c.datfile),
            title=title.file_decode(c.datfile),
            num=len(c)))

    resp('200 OK', [('Content-Type', 'text/plain; charset=Shift_JIS'),
                    ('Last-Modified', eutils.formatdate(last_stamp))])
    return (s.encode('sjis', 'ignore') for s in subjects)


class Datd(threading.Thread):
    def __init__(self, *args, **kwds):
        super(Datd, self).__init__(*args, **kwds)
        self._port = config.dat_port

    def run(self):
        utils.log('start 2ch interface')
        keylib.load(config.cache_dir)
        try:
            import waitress
        except ImportError:
            utils.log('use wsgiref')
            class Server(socketserver.ThreadingMixIn,
                         simple_server.WSGIServer):
                pass
            _server = simple_server.make_server('', self._port, dat_app,
                                                server_class=Server)
            _server.serve_forever()
        else:
            utils.log('use waitress')
            waitress.serve(dat_app, host='', port=self._port)
