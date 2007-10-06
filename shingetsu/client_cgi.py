'''Client CGI methods.
'''
#
# Copyright (c) 2005-2007 shinGETsu Project.
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

import re
import sys
import os.path
from time import time

import config
import basecgi
from cache import *
from node import *
from tag import UserTagList
from updatequeue import UpdateQueue

__version__ = "$Revision$"


class Status(dict):

    """Time stamp for client process.

    format:
        ping
        init
        sync
    """

    statusfile = config.client_log

    def __init__(self):
        dict.__init__(self)
        self.update({"ping": 0, "init": 0, "sync": 0})
        try:
            if os.path.isfile(self.statusfile):
                f = file(self.statusfile)
                for k in ("ping", "init", "sync"):
                    self[k] = int(f.readline())
                f.close()
        except IOError:
            sys.stderr.write(self.statusfile + ": IOError\n")
        except ValueError:
            sys.stderr.write("Wrong format\n")

    def sync(self):
        try:
            f = file(self.statusfile, "wb")
            for k in ("ping", "init", "sync"):
                f.write(str(self[k]) + "\n")
            f.close()
        except IOError:
            sys.stderr.write(self.statusfile + ": IOError\n")

    def check(self, key):
        """Task is done."""
        self[key] = str(int(time()))

# End of Status


class CGI(basecgi.CGI):

    """Class for /client.cgi."""

    def run(self):    
        self.stdout.write('Content-Type: text/plain\r\n')
        if (not re.search(config.admin, self.environ["REMOTE_ADDR"])) and \
           (not self.environ["REMOTE_ADDR"].startswith('127')):
            self.stdout.write("You are not the administrator.\n")
            self.stdout.close()
            return
        self.stdout.close()
        status = Status()
        self.timelimit = int(time()) + config.client_timeout

        if int(time()) - status["ping"] >= config.ping_cycle:
            self.do_ping()
            status = Status()
            self.do_update()

        nodelist = NodeList()
        if len(nodelist) == 0:
            self.do_init()
            nodelist = NodeList()
            if nodelist:
                self.do_sync()
            status = Status()

        if int(time()) - status["init"] >= config.init_cycle * len(nodelist):
            self.do_init()
            status = Status()
        elif len(nodelist) < config.nodes:
            self.do_rejoin()
            status = Status()

        if int(time()) - status["sync"] >= config.sync_cycle:
            self.do_sync()

    def check(self, key):
        status = Status()
        status.check(key)
        status.sync()

    def do_ping(self):
        self.check("ping")
        nodelist = NodeList()
        nodelist.pingall()
        nodelist.sync()
        self.stderr.write("shingetsu.node.NodeList.pingall() finished\n")

    def do_update(self):
        queue = UpdateQueue()
        queue.start()
        self.stderr.write("shingetsu.updatequeue.UpdateQueue.run() started\n")

    def do_init(self):
        self.check("init")
        nodelist = NodeList()
        nodelist.init()
        nodelist.sync()
        searchlist = SearchList()
        searchlist.extend(nodelist)
        searchlist.sync()
        self.stderr.write("shingetsu.node.NodeList.init() finished\n")

    def do_rejoin(self):
        nodelist = NodeList()
        searchlist = SearchList()
        nodelist.rejoin(searchlist)
        self.stderr.write("shingetsu.node.NodeList.rejoin() finished\n")

    def do_sync(self):
        self.check("sync")
        nodelist = NodeList()
        for n in nodelist[:]:
            nodelist.join(n)
        nodelist.sync()
        self.stderr.write("shingetsu.node.NodeList.join() finished\n")

        cachelist = CacheList()
        cachelist.clean_records()
        self.stderr.write("shingetsu.cache.CacheList.clean_records()" +
                          " finished\n")

        cachelist.remove_removed()
        self.stderr.write("shingetsu.cache.CacheList.remove_removed()" +
                          " finished\n")

        user_tag_list = UserTagList()
        user_tag_list.update_all()
        self.stderr.write("shingetsu.tag.UserTagList.update_all()" +
                          " finished\n")

        recentlist = RecentList()
        recentlist.getall()
        self.stderr.write("shingetsu.cache.RecentList.getall() finished\n")

        cachelist.getall(timelimit=self.timelimit)
        self.stderr.write("shingetsu.cache.CacheList.getall() finished\n")
