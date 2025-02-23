"""2ch like dat interface
"""
#
# Copyright (c) 2014-2024 shinGETsu Project.
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

from wsgiref import simple_server
import threading
import re
from wsgiref.headers import Headers
from email import utils as eutils
import collections
import socket
import socketserver

from shingetsu import cache
from shingetsu import title
from shingetsu import config
from shingetsu import gateway
from shingetsu import tag


from . import post
from . import middleware
from . import dat
from . import utils
from . import keylib


board_re= re.compile(r'/([^/]+)/$')
thread_re = re.compile(r'/([^/]+)/dat/([^.]+)\.dat')
subject_re = re.compile(r'/([^/]+)/subject\.txt')
post_comment_re = re.compile(r'/test/bbs\.cgi')
head_re = re.compile(r'/([^/]+)/head\.txt$')

@middleware.simple_range
@middleware.last_modified
@middleware.gzipped
def dat_app(env, resp):
    # utils.log('dat_app')
    addr = env.get('REMOTE_ADDR', '')
    m = re.search(r'^::ffff:([\d.]+)$', addr)
    if m:
        addr = m.group(1)
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

    routes = [
        (board_re, board_app),
        (subject_re, subject_app),
        (thread_re, thread_app),
        (post_comment_re, post.post_comment_app),
        (head_re, head_app)
    ]
    try:
        for (route, app) in routes:
            m = route.match(path)
            if m:
                env['mch.path_match'] = m
                return app(env, resp)

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

    board = utils.sanitize(utils.get_board(path))

    if board:
        fmt = '{logo} - {board} - {desc}'
    else:
        fmt = '{logo} - {desc}'

    text = fmt.format(logo=message['logo'], desc=message['description'], board=board)

    html = '''
        <!DOCTYPE html>
        <html><head>
        <meta http-equiv="content-type" content="text/html; charset=Shift_JIS">
        <title>{text}</title>
        <meta name="description" content="{text}">
        </head><body>
        <h1>{text}</h1>
        </body></html>
    '''.format(text=text)
    return [html.encode('cp932', 'replace')]


def thread_app(env, resp):
    path = env['PATH_INFO']
    # utils.log('thread_app', path)
    m = thread_re.match(path)
    board, datkey = m.group(1), m.group(2)

    key = keylib.get_filekey(datkey)
    data = cache.Cache(key)
    data.load()

    if check_get_cache(env):
        if not data.exists() or len(data) == 0:
            # when first access, load data from network
            data.search()

        elif _count_is_update(key):
            # update thread
            # limit `data.search` calling. it's slow!
            threading.Thread(target=data.search, daemon=True).start()

    if not data.exists():
        resp('404 Not Found', [('Content-Type', 'text/plain; charset=Shift_JIS')])
        return [b'404 Not Found']

    thread = dat.make_dat(data, env, board)

    headers = Headers([('Content-Type', 'text/plain; charset=Shift_JIS')])
    last_m = eutils.formatdate(data.stamp)
    headers['Last-Modified'] = last_m
    resp("200 OK", headers.items())

    return (c.encode('cp932', 'replace') for c in thread)



def make_subject_cachelist(board):
    """Make RecentList&CacheList"""
    recentlist = cache.RecentList()
    cachelist = cache.CacheList()

    seen = set(c.datfile for c in cachelist)
    result = cachelist
    for rec in recentlist:
        if rec.datfile not in seen:
            seen.add(rec.datfile)

            c = cache.Cache(rec.datfile)
            c.recent_stamp = rec.stamp
            result.append(c)

    result = [c for c in result if c.type == 'thread']

    # same as order recent page
    result.sort(key=lambda c: c.recent_stamp, reverse=True)
    if board is not None:
        sugtags = tag.SuggestedTagTable()
        result = [c for c in result if has_tag(c, board, sugtags)]
    return result

def subject_app(env, resp):
    # utils.log('subject_app')
    path = env['PATH_INFO']
    # board is `title.file_encode`ed
    # example: 2ch_E99B91E8AB87(雑談)
    board = env['mch.path_match'].group(1)

    m = re.match(r'2ch_(\S+)', board)
    if not (board.startswith('2ch') or m):
        resp("404 Not Found", [('Content-Type', 'text/plain')])
        return [b'404 Not Found']

    board_encoded = m and title.str_decode(m.group(1))

    if board_encoded:
        # such as '雑談', 'ニュース', etc...
        board_name = title.file_decode('dummy_' + board_encoded)
    else:
        board_name = None

    subjects, last_stamp = make_subject(env, board_name)
    resp('200 OK', [('Content-Type', 'text/plain; charset=Shift_JIS'),
                    ('Last-Modified', eutils.formatdate(last_stamp))])
    return (s.encode('cp932', 'replace') for s in subjects)



def make_subject(env, board):
    load_from_net = check_get_cache(env)

    subjects = []
    cachelist = make_subject_cachelist(board)
    last_stamp = 0
    for c in cachelist:
        if not load_from_net and len(c) == 0:
            # Because you don't have a permission of getting data from network,
            # don't need to look a thread that don't have records.
            continue

        if last_stamp < c.stamp:
            last_stamp = c.stamp

        try:
            key = keylib.get_datkey(c.datfile)
        except keylib.DatkeyNotFound:
            continue

        title_str = title.file_decode(c.datfile)
        if title_str is not None:
            title_str = title_str.replace('\n', '')
        subjects.append('{key}.dat<>{title} ({num})\n'.format(
            key=key,
            title=title_str,
            num=len(c)))
    return subjects, last_stamp



def has_tag(c, board, sugtags):
    tags = c.tags
    if c.datfile in sugtags:
        tags += sugtags[c.datfile]
    return board in (str(t) for t in tags)


def head_app(env, resp):
    resp('200 OK', [('Content-Type', 'text/plain; charset=Shift_JIS')])
    body = []
    with open(config.motd, encoding='utf-8', errors='replace') as f:
        for line in f:
            body.append(line.rstrip('\n') + '<br>\n')
    return [''.join(body).encode('cp932', 'replace')]


class Datd(threading.Thread):
    def __init__(self, *args, **kwds):
        super(Datd, self).__init__(*args, **kwds)
        self._addr = config.bind_addr
        self._port = config.dat_port

    def run(self):
        utils.log('start 2ch interface')
        keylib.load()
        try:
            import waitress
        except ImportError:
            utils.log('use wsgiref')
            class Server(socketserver.ThreadingMixIn,
                         simple_server.WSGIServer):
                address_family = socket.AF_INET6
            _server = simple_server.make_server(self._addr, self._port, dat_app,
                                                server_class=Server)
            _server.serve_forever()
        else:
            utils.log('use waitress')
            waitress.serve(dat_app, host=self._addr, port=self._port)
