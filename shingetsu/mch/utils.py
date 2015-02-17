
'utils'

import sys

from shingetsu import title
from shingetsu import tag


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
                     ua=env.get('USER_AGENT', ''))
    log(msg)


def save_tag(cache, user_tag):
    cache.tags.update([user_tag])
    cache.tags.sync()
    user_tag_list = tag.UserTagList()
    user_tag_list.add([user_tag])
    user_tag_list.sync()

    print('usertags', user_tag_list)
    print('cache.tags', cache.tags)
