"""daemon.py - SAKU daemon module.
"""
#
# Copyright (c) 2005-2012 shinGETsu Project.
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

import os
import sys
from datetime import datetime

from . import config
from . import crond
from . import httpd
from . import mch
from .util import opentext


class Logger:

    """Save logs to /LOGDIR/%Y-%m-%d.
    """

    def __init__(self, logdir, additional=None):
        self.logdir = logdir
        self.logfile = ''
        self.output = None
        self.output2 = additional
        self.lastline = '\n'

    def write(self, msg):
        now = datetime.now()
        newlog = os.path.join(self.logdir, now.strftime('%Y-%m-%d'))
        if self.lastline.endswith('\n'):
            msg = '%s<>%s' % (now.strftime('%Y-%m-%d %H:%M:%S'), msg)
        self.lastline = msg

        if self.logfile == newlog:
            pass
        elif self.logfile == '':
            self.logfile = newlog
            self.output = opentext(self.logfile, 'a')
        else:
            self.output.close()
            self.logfile = newlog
            self.output = opentext(self.logfile, 'a')

        self.output.write(msg)
        self.output.flush()
        if self.output2:
            self.output2.write(msg)
            self.output2.flush()

    def flush(self):
        pass

    def close(self):
        pass

def setup():
    config.flags.append('light_cgi')
    config.abs_docroot = os.path.join(os.getcwd(), config.docroot)
    for i in [os.path.join(config.docroot, j) for j in \
                (config.run_dir, config.cache_dir)] + \
             [config.log_dir]:
        if not os.path.isdir(i):
            os.makedirs(i)

def set_logger(additional=None):
    logger = Logger(os.path.join(os.getcwd(), config.log_dir), additional)
    sys.stderr = logger
    sys.stdout = logger

def start_daemon():
    for lock in (config.lock, config.search_lock, config.admin_search):
        lock = os.path.join(config.docroot, lock)
        if os.path.exists(lock):
            try:
                os.remove(lock)
            except OSError:
                sys.stderr.write('OSError: removing %s\n' % lock)

    if hasattr(os, 'getpid'):
        try:
            pidfile = os.path.join(config.docroot, config.pid)
            open(pidfile, 'w').write('%d' % os.getpid())
        except (IOError, OSError) as err:
            sys.stderr.write('IOError/OSError: %s\n' % err)

    crondaemon = crond.Crond()
    crondaemon.setDaemon(True)
    crondaemon.start()

    if config.enable2ch:
        datdaemon = mch.Datd()
        datdaemon.setDaemon(True)
        datdaemon.start()

    httpdaemon = httpd.Httpd()
    httpdaemon.setDaemon(True)
    httpdaemon.start()

    return httpdaemon

def stop_daemon():
    pass
