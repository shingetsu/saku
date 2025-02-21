'''Cron daemon running in another thread for client.cgi.
'''
#
# Copyright (c) 2005 shinGETsu Project.
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

import gc
import os.path
import re
import sys
import time
from threading import Thread

from . import config
from . import tiedobj
from .cache import *
from .node import *
from .tag import UserTagList
from .updatequeue import UpdateQueue
from .util import opentext


_myself4 = None
_myself6 = None


class Crond(Thread):
    gc_counter = {}

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        time.sleep(5)
        gc.set_debug(gc.DEBUG_UNCOLLECTABLE)
        while True:
            self.clear_cache()
            #self.gc_debug()
            Client().start()
            time.sleep(config.client_cycle)

    def clear_cache(self):
        try:
            re.purge()
            tiedobj.reset()
        except Exception as err:
            sys.stderr.write('Crond.clear_cache(): %s\n' % err)

    def gc_debug(self):
        collect = gc.collect()
        counter = {}
        objects = gc.get_objects()
        for i in objects:
            t = str(type(i))
            counter[t] = counter.get(t, 0) + 1
        tmp = {}
        for k in list(counter.keys()):
            if self.gc_counter.get(k, 0) != counter[k]:
                tmp[k] = counter[k] - self.gc_counter.get(k, 0)
                self.gc_counter[k] = counter[k]
        print('GC', len(objects), len(gc.garbage), collect, tmp)

# End of Crond


class Status(dict):

    """Time stamp for client process.

    format:
        ping
        init
        sync
    """

    statusfile = config.client_log
    use_client_log = config.use_client_log
    
    @classmethod
    def get_instance(cls):
        if config.use_client_log:
            return cls()
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        dict.__init__(self)
        self.update({"ping": 0, "init": 0, "sync": 0})
        if self.use_client_log:
            try:
                if os.path.isfile(self.statusfile):
                    f = open(self.statusfile)
                    for k in ("ping", "init", "sync"):
                        self[k] = int(f.readline())
                    f.close()
            except IOError:
                sys.stderr.write(self.statusfile + ": IOError\n")
            except ValueError:
                sys.stderr.write("Wrong format\n")

    def sync(self):
        if self.use_client_log:
            try:
                f = opentext(self.statusfile, 'w')
                for k in ("ping", "init", "sync"):
                    f.write(str(self[k]) + '\n')
                f.close()
            except IOError:
                sys.stderr.write(self.statusfile + ": IOError\n")
        else:
            time.sleep(1)

    def check(self, key):
        """Task is done."""
        self[key] = int(time.time())

# End of Status


class Client(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        status = Status.get_instance()
        self.timelimit = int(time.time()) + config.client_timeout

        if int(time.time()) - status["ping"] >= config.ping_cycle:
            self.do_ping()
            status = Status.get_instance()
            self.do_update()

        global _myself4, _myself6
        nodelist = NodeList()
        myself4, myself6 = nodelist.myself()
        print("myself: %s, %s" % (myself4, myself6))
        if not _myself4 and not _myself6:
            _myself4 = myself4
            _myself6 = myself6

        if len(nodelist) == 0:
            self.do_init()
            nodelist = NodeList()
            if nodelist:
                self.do_sync()
            status = Status.get_instance()
        elif myself4 != _myself4 or myself6 != _myself6:
            print("changed myself: %s -> %s, %s -> %s" % (_myself4, myself4, _myself6, myself6))
            _myself4 = myself4
            _myself6 = myself6
            self.do_init()
            nodelist = NodeList()
            status = Status.get_instance()
        elif (int(time.time()) - status["init"]
            >= config.init_cycle * len(nodelist)):
            self.do_init()
            status = Status.get_instance()
        elif len(nodelist) < config.nodes:
            self.do_rejoin()
            status = Status.get_instance()

        if int(time.time()) - status["sync"] >= config.sync_cycle:
            self.do_sync()

    def check(self, key):
        status = Status.get_instance()
        status.check(key)
        status.sync()

    def do_ping(self):
        self.check("ping")
        nodelist = NodeList()
        nodelist.pingall()
        nodelist.sync()
        sys.stderr.write("shingetsu.node.NodeList.pingall() finished\n")

    def do_update(self):
        queue = UpdateQueue()
        queue.start()
        sys.stderr.write("shingetsu.updatequeue.UpdateQueue.run() started\n")

    def do_init(self):
        self.check("init")
        nodelist = NodeList()
        nodelist.init()
        nodelist.sync()
        searchlist = SearchList()
        nodelist.clean(searchlist)
        searchlist.extend(nodelist)
        searchlist.sync()
        sys.stderr.write("shingetsu.node.NodeList.init() finished\n")

    def do_rejoin(self):
        nodelist = NodeList()
        searchlist = SearchList()
        nodelist.rejoin(searchlist)
        nodelist.clean(searchlist)
        sys.stderr.write("shingetsu.node.NodeList.rejoin() finished\n")

    def do_sync(self):
        self.check("sync")
        nodelist = NodeList()
        for n in nodelist[:]:
            nodelist.join(n)
        nodelist.sync()
        sys.stderr.write("shingetsu.node.NodeList.join() finished\n")

        cachelist = CacheList()
        cachelist.rehash()
        sys.stderr.write("shingetsu.cache.CacheList.rehash() finished\n")

        cachelist.clean_records()
        sys.stderr.write("shingetsu.cache.CacheList.clean_records()" +
                          " finished\n")

        cachelist.remove_removed()
        sys.stderr.write("shingetsu.cache.CacheList.remove_removed()" +
                          " finished\n")

        user_tag_list = UserTagList()
        user_tag_list.update_all()
        sys.stderr.write("shingetsu.tag.UserTagList.update_all()" +
                          " finished\n")

        recentlist = RecentList()
        recentlist.getall()
        sys.stderr.write("shingetsu.cache.RecentList.getall() finished\n")

        cachelist.getall(timelimit=self.timelimit)
        sys.stderr.write("shingetsu.cache.CacheList.getall() finished\n")

# End of Client
