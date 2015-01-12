# coding: utf-8
'2ch like post'


import base64
import time
import cgi
import re

from shingetsu import title
from shingetsu import gateway
from shingetsu import cache
from shingetsu import updatequeue
from shingetsu import template

from . import dat
from . import utils
from . import keylib



def post_comment(thread_key, name, mail, body, passwd):
    """Post article."""

    stamp = int(time.time())
    body = {'body': gateway.CGI.escape(None, body),
            'name': gateway.CGI.escape(None, name),
            'mail': gateway.CGI.escape(None, mail)}

    c = cache.Cache(thread_key)
    rec = cache.Record(datfile=c.datfile)
    id = rec.build(stamp, body, passwd=passwd)

    # utils.log('post %s/%d_%s' % (c.datfile, stamp, id))

    c.add_data(rec)
    c.sync_status()

    queue = updatequeue.UpdateQueue()
    queue.append(c.datfile, stamp, id, None)
    queue.start()


def error_resp(msg, start_response, host, name, mail, body):
    info = {'message': msg, 'host': host, 'name': name, 'mail': mail, 'body': body}
    msg = (template.Template()
        .display('2ch_error', info)
        .encode('cp932', 'replace'))
    start_response('200 OK', [('Content-Type', 'text/html; charset=Shift_JIS')])
    return [msg]

success_msg = '''<html lang="ja"><head><meta http-equiv="Content-Type" content="text/html"><title>書きこみました。</title></head>
<body>書きこみが終わりました。<br><br></body></html>'''


def _get_comment_data(env):
    fs = cgi.FieldStorage(environ=env, fp=env['wsgi.input'],
                          encoding='cp932')
    prop = lambda s: fs[s].value if s in fs else ''
    return [prop('subject'), prop('FROM'), prop('mail'), prop('MESSAGE'), prop('key')]

def post_comment_app(env, resp):
    # utils.log('post_comment_app')
    subject, name, mail, body, datkey = _get_comment_data(env)

    info = {'host': env.get('REMOTE_ADDR', ''),
            'name': name,
            'mail': mail,
            'body': body}

    if body == '':
        return error_resp('本文がありません.', resp, **info)

    if subject:
        key = title.file_encode('thread', subject)
    else:
        key = keylib.get_filekey(datkey)

    if cache.Cache(key).exists():
        pass
    elif env.get('shingetsu.isadmin', False):
        pass
    elif env.get('shingetsu.isfriend', False):
        pass
    elif subject:
        return error_resp('掲示版を作る権限がありません', resp, **info)
    else:
        return error_resp('掲示版がありません', resp, **info)

    if (not subject and not key):
        return error_resp('フォームが変です.', resp, **info)



    table = dat.ResTable(cache.Cache(key))
    def replace(match):
        no = int(match.group(1))
        return '>>' + table[no]
    # replace number anchor to id anchor
    body = re.sub(r'>>([1-9][0-9]*)', replace, body)  # before escape '>>'

    if name.find('#') < 0:
        passwd = ''
    else:
        name, passwd = name.split('#', 1)

    if (passwd and not env['shingetsu.isadmin']):
        return error_resp('自ノード以外で署名機能は使えません', resp, **info)

    post_comment(key, name, mail, body, passwd)
    resp('200 OK', [('Content-Type', 'text/html; charset=Shift_JIS')])
    return [success_msg.encode('cp932', 'replace')]

