
'utils'

import sys
import re

from shingetsu import title
from shingetsu import tag
from shingetsu import util


def log(s, *args, **kwds):
    sys.stderr.write(s.format(*args, **kwds) + '\n')


def log_request(env):  # same as saku's log format
    fmt = '{host}<>{proxy}<>{method} {path} {protocol}<>{referer}<>{ua}'
    msg = fmt.format(host=env['REMOTE_ADDR'],
                     proxy=env.get('HTTP_X_FORWARDED_FOR', 'direct'),
                     method=env['REQUEST_METHOD'],
                     path=env['PATH_INFO'],
                     protocol=env['SERVER_PROTOCOL'],
                     referer=env.get('REFERER', ''),
                     ua=env.get('HTTP_USER_AGENT', ''))
    log(msg)


def save_tag(cache, user_tag):
    cache.tags.update([user_tag])
    cache.tags.sync()
    user_tag_list = tag.UserTagList()
    user_tag_list.add([user_tag])
    user_tag_list.sync()

def get_board(url):
    m = re.search(r'/2ch_([^/]+)/', url)
    if not m:
        return ''

    board = title.file_decode('dummy_' + m.group(1))
    return board

def sanitize(text):
    return text.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;').replace('"', '&quot;')
