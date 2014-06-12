
'utils'

import sys

from shingetsu import title


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
