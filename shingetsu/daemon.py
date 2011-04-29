'''daemon.py - SAKU daemon module.
'''
#
# Copyright (c) 2005,2006 shinGETsu Project.
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
import sys
import time

import config
import httpd
import crond
from upnp import findrouter

try:
    import miniupnpc
except ImportError:
    miniupnpc = None
    sys.stdout.write('system does not have MiniUPnPc.\n');

__version__ = "$Revision$"

router = None

class Logger:

    """Save logs to /LOGDIR/%Y-%m-%d."""

    def __init__(self, logdir, additional=None):
        self.logdir = logdir
        self.logfile = ""
        self.output = None
        self.output2 = additional

    def write(self, msg):
        newlog = self.logdir + "/" + \
                 time.strftime("%Y-%m-%d", time.localtime())
        if self.logfile == newlog:
            pass
        elif self.logfile == "":
            self.logfile = newlog
            self.output = file(self.logfile, "a")
        else:
            self.output.close()
            self.logfile = newlog
            self.output = file(self.logfile, "a")
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
    config.flags.append("light_cgi")
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
                sys.stderr.write("OSError: removing %s\n" % lock)

    if hasattr(os, 'getpid'):
        try:
            pidfile = os.path.join(config.docroot, config.pid)
            file(pidfile, 'w').write('%d' % os.getpid())
        except (IOError, OSError), err:
            sys.stderr.write('IOError/OSError: %s\n' % err)

    global router
    global mupnpc
    if config.use_upnp:
        if not miniupnpc:
            sys.stderr.write("finding router\n")
            router = findrouter(config.upnp_timeout)
            if router:
                sys.stderr.write("found router: %s\n" % router)
            else:
                sys.stderr.write("Error: faild to find router\n")
        else:
            mupnpc = miniupnpc.UPnP()
            mupnpc.discoverdelay = config.upnp_timeout
            sys.stderr.write("finding router with MiniUPnPc\n")
            try:
                rcout = mupnpc.discover()
            except Exception, e:
                mupnpc = None
            if rcout >= 1:
                try:
                    raddr = mupnpc.selectigd()
                except Exception, e:
                    raddr = None
                    mupnpc = None
                if raddr:
                    sys.stderr.write("sending router openport %d: %s\n" % (config.port, raddr))
                    try:
                        opr = mupnpc.addportmapping(config.port, 'TCP', mupnpc.lanaddr, config.port, 'shinGETsu saku', '')
                    except Exception, e:
                        opr = None
                        mupnpc = None
                    if opr:
                        sys.stderr.write("openport succeed: %s\n" % raddr)
                    else:
                        sys.stderr.write("Error: openport failed\n")
                else:
                    sys.stderr.write("Error: faild to find router\n")
            else:
                sys.stderr.write("Error: faild to find router\n")

    crondaemon = crond.Crond(router)
    crondaemon.setDaemon(True)
    crondaemon.start()

    httpdaemon = httpd.Httpd()
    httpdaemon.setDaemon(True)
    httpdaemon.start()

    return httpdaemon

def stop_daemon():
    if not miniupnpc:
        if router:
            sys.stderr.write("sending router closeport %d: %s\n" %
                             (config.port, router))
            flag = router.closeport(config.port, "TCP")
            if flag:
                sys.stderr.write("closeport succeed: %s\n" % router)
            else:
                sys.stderr.write("Error: closeport failed: %s\n" % router)
    else:
        if mupnpc:
            sys.stderr.write("sending router closeport %d\n" % config.port)
            mupnpc.deleteportmapping(config.port, 'TCP')
            sys.stderr.write("closeport succeed: %s\n" % mupnpc.selectigd())
