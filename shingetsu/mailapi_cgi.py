'''Mail Parser.
'''
#
# Copyright (c) 2007 shinGETsu Project.
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
# $Id$
#
import os
import re
import sys
import base64
import email.Parser
from time import time

import config
import gateway
import spam
from cache import *
from node import *
from tmpaddr import TmpAddress
from updatequeue import UpdateQueue

__version__ = '$Revision$'


class CGI(gateway.CGI):
    '''Mail Parser.
    '''

    def run(self):
        self.stdout.write('Content-Type: text/plain\r\n')
        if (not re.search(config.admin, self.environ["REMOTE_ADDR"])) and \
           (not self.environ["REMOTE_ADDR"].startswith('127')):
            self.stdout.write("You are not the administrator.\n")
            self.stdout.close()
            return
        elif self.environ.get('REQUEST_METHOD', '') != 'POST':
            return
        self.read_mail()

    def read_mail(self):
        '''Read mail style post from stdin.
        '''
        try:
            length = int(self.environ['CONTENT_LENGTH'])
        except (ValueError, KeyError):
            return
        msg = email.Parser.Parser().parsestr(self.stdin.read(length))
        body = ''
        attach = ''
        suffix = 'txt'
        datfile = msg.get('subject', '')
        addr = msg.get('to', '')
        tmpaddr = TmpAddress()
        if not tmpaddr.check(addr):
            return
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            filename = part.get_filename()
            charset = part.get_content_charset()
            if not charset:
                charset = 'utf-8'
            if filename and (not attach):
                found = re.search(r'\.([^./]+)$', filename)
                if found:
                    suffix = found.group(1)
                if part.get('Content-Transfer-Encoding', '') == 'base64':
                    attach = part.get_payload(decode=False)
                else:
                    attach = part.get_payload(decode=True)
                    attach = base64.encodestring(attach)
                attach = attach.replace('\n', '')
            elif (not filename) and (not body):
                body = part.get_payload(decode=True).decode(charset, 'replace')
        if re.search(r'thread_[0-9A-F]+', datfile) and \
           (body or attach):
            self.do_post_from_mail(datfile,
                                   body.encode('utf-8', 'replace'),
                                   attach,
                                   suffix)
 
    def do_post_from_mail(self, datfile, bodystr, attach, suffix):
        """Post article."""
        suffix = re.sub(r"[^0-9A-Za-z]", "", suffix)
        stamp = int(time())

        body = {'body': self.escape(bodystr)}
        if attach:
            body['attach'] = attach
            body['suffix'] = suffix
        if not body:
            return None

        cache = Cache(datfile)
        rec = Record(datfile=cache.datfile)
        id = rec.build(stamp, body)

        if len(rec.recstr) > config.record_limit*1024:
            return None
        elif spam.check(rec.recstr):
            return None

        if cache.exists():
            cache.add_data(rec)
            cache.sync_status()
        else:
            return None

        queue = UpdateQueue()
        queue.append(cache.datfile, stamp, id, None)
        queue.start()

        return True

# End of CGI
