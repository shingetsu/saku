# -*- encoding: utf-8 -*-
"""2ch like post
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

import time
import cgi
import re

from shingetsu import title
from shingetsu import gateway
from shingetsu import cache
from shingetsu import spam
from shingetsu import updatequeue
from shingetsu import template
from shingetsu import config
from shingetsu import util

from . import dat
from . import utils
from . import keylib


class SpamError(RuntimeError):
    pass


def post_comment(env, thread_key, name, mail, body, passwd, tag=None):
    """Post article."""

    if config.server_name:
        dat_host = config.server_name
    else:
        host = env['HTTP_HOST']
        dat_host = re.sub(r':\d+', ':' + str(config.dat_port), host)
    p = re.compile(r'https?://' + dat_host + '/test/read.cgi/2ch(?:_[0-9A-Z]+)?/([0-9]+)/')
    for x in p.finditer(body):
        try:
            file = keylib.get_filekey(x.group(1))
            body = body.replace(x.group(0),'[[' + title.file_decode(file) + ']]')
        except keylib.DatkeyNotFound:
            pass

    stamp = int(time.time())
    recbody = {}
    if body != '': recbody['body'] = gateway.CGI.escape(None, body)
    if name != '': recbody['name'] = gateway.CGI.escape(None, name)
    if mail != '': recbody['mail'] = gateway.CGI.escape(None, mail)

    c = cache.Cache(thread_key)
    rec = cache.Record(datfile=c.datfile)
    id = rec.build(stamp, recbody, passwd=passwd)

    if spam.check(rec.recstr):
        raise SpamError()

    # utils.log('post %s/%d_%s' % (c.datfile, stamp, id))

    c.add_data(rec)
    c.sync_status()

    if tag:
        utils.save_tag(c, tag)


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
    mail = prop('mail')
    if mail.lower() == 'sage':
        mail = ''
    return [prop('subject'), prop('FROM'), mail, prop('MESSAGE'), prop('key')]

def post_comment_app(env, resp):
    # print('post', env)
    if env['REQUEST_METHOD'] != 'POST':
        resp("404 Not Found", [('Content-Type', 'text/plain')])
        return [b'404 Not Found']

    # utils.log('post_comment_app')
    subject, name, mail, body, datkey = _get_comment_data(env)

    info = {'host': util.get_http_remote_addr(env),
            'name': name,
            'mail': mail,
            'body': body}

    if body == '':
        return error_resp('本文がありません.', resp, **info)


    if subject:
        key = title.file_encode('thread', subject)
    else:
        key = keylib.get_filekey(datkey)


    has_auth = env.get('shingetsu.isadmin', False) or env.get('shingetsu.isfriend', False)

    referer = env.get('HTTP_REFERER', '')
    m = re.search(r'/2ch_([^/]+)/', referer)
    tag = None
    if m and has_auth:
        tag = title.file_decode('dummy_' + m.group(1))


    if cache.Cache(key).exists():
        pass
    elif has_auth:
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


    try:
        post_comment(env, key, name, mail, body, passwd, tag)
    except SpamError:
        return error_resp('スパムとみなされました', resp, **info)

    resp('200 OK', [('Content-Type', 'text/html; charset=Shift_JIS')])
    return [success_msg.encode('cp932', 'replace')]

