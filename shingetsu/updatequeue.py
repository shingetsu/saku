'''Update Manager.
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
from time import time
from random import choice
from compatible import RLock, Thread

import config
from cache import *
from node import *
from tiedobj import *

__version__ = '$Revision$'
__all__ = ['UpdateQueue']

lock = RLock()

class _UpdateQueue:
    '''Update Manager.

    self.queue is a tieddict like as
    self.queue[stamp<>id<>datfile] = [node1, node2, ...]
    '''
    def __init__(self):
        self.queue = tieddict(None)
        self.running = False

    def append(self, datfile, stamp, id, node):
        key = '%s<>%s<>%s' % (stamp, id, datfile)
        self.queue.append(key, node, False)

    def start(self):
        t = Thread(target=self.run)
        t.start()
 
    def run(self):
        try:
            lock.acquire(True)
            if self.running:
                return
            else:
                self.running = True
        finally:
            lock.release()
        try:
            for updateid in self.queue.keys():
                self.do_update(updateid)
        finally:
            try:
                lock.acquire(True)
                self.running = False
            finally:
                lock.release()

    def do_update(self, updateid):
        stamp, id, datfile = updateid.split('<>')
        rec = Record(datfile=datfile, idstr=stamp+'_'+id)
        for node in self.queue[updateid]:
            done = self.do_update_node(rec, node)
            if done:
                del self.queue[updateid]
                updatelist = UpdateList()
                updatelist.append(rec)
                updatelist.sync()
                recentlist = RecentList()
                recentlist.append(rec)
                recentlist.sync()
                return
            else:
                self.queue.remove(updateid, node)

    def do_update_node(self, rec, node):
        updatelist = UpdateList()
        if rec in updatelist:
            return True
        stamp = rec.stamp
        id = rec.id
        cache = Cache(rec.datfile)
        nodelist = NodeList()
        searchlist = SearchList()
        if not cache.exists():
            if len(searchlist) < config.search_depth:
                nodelist.tell_update(cache, stamp=stamp, id=id, node=node)
                return True
            else:
                return True
        elif node is None:
            pass
        elif len(cache) > 0:
            flag_got, flag_spam = cache.get_data(stamp=stamp, id=id, node=node)
        else:
            cache.get_with_range(node=node)
            flag_got = rec.exists()
            flag_spam = False

        if node is None:
            nodelist.tell_update(cache, stamp=stamp, id=id)
            return True
        elif flag_got:
            if not flag_spam:
                nodelist.tell_update(cache, stamp=stamp, id=id)
            if (node not in nodelist) and (len(nodelist) < config.nodes):
                nodelist.join(node)
                nodelist.sync()
            searchlist = SearchList()
            if node not in searchlist:
                searchlist.join(node)
                searchlist.sync()
            return True
        else:
            return False

# End of _UpdateQueue


def UpdateQueue():
    return _queue

_queue = _UpdateQueue()
