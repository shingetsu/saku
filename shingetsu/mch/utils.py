'utils'

import sys

from shingetsu import title


def num_to_thread(n):
    """num to thread key.

    >>> num_to_thread(15)
    'thread_F'
    """
    try:
        n = int(n)
    except TypeError:
        return None
    return 'thread_' + ('%x' % n).upper()


def thread_to_num(f):
    """ thread key to num.

    >>> thread_to_num('thread_F')
    15
    """
    try:
        type, key = f.split('_', 1)
    except IndexError:
        return None

    return int(key, 16)


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
