'make dat'

import re
import datetime

from shingetsu import config
from shingetsu import title
from shingetsu import cache as cachelib

from . import utils

weekday = {0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日',}

def _datestr_2ch(epoch_str):
    d = datetime.datetime.fromtimestamp(int(epoch_str))
    s = d.strftime('%Y/%m/%d({}) %H:%M:%S.00')
    return s.format(weekday[d.weekday()])



def make_dat(cache, env, board):
    dat = []
    table = ResTable(cache)

    for i, k in enumerate(cache.keys()):
        rec = cache[k]
        rec.load()


        name = rec.get('name')
        if not name:
            name = '名無しさん'
        if rec.get('pubkey'):  # 2ch trip
            name += '◆' + rec.get('pubkey')[:10]  # 10 is 2ch trip length

        comment = '{name}<>{mail}<>{date} ID:{id}<>{body}<>'.format(
                name=name,
                mail=rec.get('mail', ''),
                date=_datestr_2ch(rec.get('stamp', 0)),
                id=rec.get('id', '')[:8],  # 8 is saku's id length
                body=_make_body(rec, env, board, table)
        )
        if i == 0:  # dat title
            comment += title.file_decode(cache.datfile)
        comment += '\n'
        dat.append(comment)

    return dat



class ResTable(dict):
    't[res_id] -> res_number & t[res_number] -> res_id'
    'res_number is 1 origin'
    def __init__(self, cache):
        cache.load()
        for i, k in enumerate(list(cache.keys()), 1):
            rec = cache[k]
            rec.load()
            self[i] = rec.id[:8]
            self[rec.id[:8]] = i

    def __getitem__(self, key):
        return self.get(key, key)

def _make_body(rec, env, board, table):
    if config.server_name:
        dat_host = saku_host = config.server_name
    else:
        host = env['HTTP_HOST']
        dat_host = re.sub(r':\d+', ':' + str(config.dat_port), host)
        saku_host = re.sub(r':\d+', ':' + str(config.port), host)

    body = _make_attach_link(rec, saku_host)
    body = _make_res_anchor(body, table)
    body = _make_bracket_link(body, dat_host, board, table)
    return body


def _make_attach_link(rec, saku_host):
    if 'attach' not in rec:
        return rec.get('body', '')


    # saku's thread.cgi deal with attach file.
    url = 'http://{}/thread.cgi/{}/{}/{}.{}'.format(
        saku_host, rec.datfile, rec.id,
        rec.stamp, rec.get('suffix', 'txt'))
    body = rec.get('body', '') + '<br><br>[Attached]<br>' + url
    return body


def _make_res_anchor(body, table):
    def replace(match):
        id = match.group(1)
        no = str(table[id])
        return '&gt;&gt;' + no  # '>>' is escape to '&gt;&gt;'

    return re.sub(r'&gt;&gt;([0-9a-f]{8})', replace, body)


def _make_bracket_link(body, dat_host, board, table):

    def replace(match):
        link = match.group(1)
        # saku's link format
        for r in (r"^(?P<title>[^/]+)$",
                  r"^/(?P<type>[a-z]+)/(?P<title>[^/]+)$",
                  r"^(?P<title>[^/]+)/(?P<id>[0-9a-f]{8})$",
                  r"^/(?P<type>[a-z]+)/(?P<title>[^/]+)/(?P<id>[0-9a-f]{8})$"):
            m = re.match(r, link)
            if m:
                d = m.groupdict()
                _title = d['title']
                type = d.get('type', None)
                id = d.get('id', None)
                break
        else:
            return match.group(0)

        if not type:
            type = 'thread'
        file = title.file_encode(type, _title)
        datkey = utils.thread_to_num(file)
        if id is None:
            # same `board` is required for the dedicated browser to work properly
            url = 'http://{}/{}/dat/{}.dat'.format(dat_host, board, datkey)
            return '[[{title}({url})]]'.format(title=_title, url=url)
        else:
            # anchor to specific comment
            cache = cachelib.Cache(file)
            table = ResTable(cache)
            no = table[id]
            # this format url expect that dedicated browser get res number
            url = 'http://{}/test/read.cgi/{}/{}/{}'.format(dat_host, board, datkey, no)
            return '[[{title}(&gt;&gt;{no} {url})]]'.format(title=_title, no=no, url=url)

    return re.sub(r'\[\[([^<>]+?)\]\]', replace, body)



