"""Saku Node and NodeList.
"""
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

import gzip
import ipaddress
import random
import re
import socket
import sys
import threading
import urllib.parse
import urllib.request
from io import BytesIO, StringIO

from . import config
from .tiedobj import *
from .conflist import *

__all__ = ['Node', 'RawNodeList', 'NodeList', 'SearchList', 'LookupTable',
           'init_node', 'node_allow', 'node_deny']

_init_node = None
_node_allow = None
_node_deny = None

def urlopen(url):
    req = urllib.request.Request(url)
    req.add_header('Accept-Encoding', 'gzip')
    req.add_header('User-Agent', config.version)
    return urllib.request.urlopen(req)

def init_node():
    global _init_node
    if _init_node is None:
        _init_node = ConfList(config.initnode_list)
    else:
        _init_node.update()
    if not _init_node:
        return config.init_node
    return list(_init_node)

def node_allow():
    global _node_allow
    if _node_allow is None:
        _node_allow = RegExpList(config.node_allow)
    else:
        _node_allow.update()
    return _node_allow

def node_deny():
    global _node_deny
    if _node_deny is None:
        _node_deny = RegExpList(config.node_deny)
    else:
        _node_deny.update()
    return _node_deny


class Broadcast(threading.Thread):
    def __init__(self, msg, cache):
        threading.Thread.__init__(self)
        self.msg = msg
        self.cache = cache

    def run(self):
        nodelist = NodeList()
        for node in self.cache.node:
            if (node in nodelist) or node.ping():
                node.talk(self.msg)
            else:
                self.cache.node.remove(node)
                self.cache.node.sync()
        for node in nodelist:
            if node not in self.cache.node:
                node.talk(self.msg)


class NodeError(Exception):
    pass


class SocketIO:
    '''Wrapper for SimpleGzipFile and URLopener.
    '''
    def __init__(self, fp, msg):
        self.fp = fp
        self.msg = msg

    def __iter__(self):
        try:
            for line in self.fp:
                yield str(line, 'utf-8', 'replace')
        except Exception as err:
            sys.stderr.write('%s: %s\n' % (self.msg, err))

# End of SocketIO


class Node:

    """One unit for P2P."""

    nodestr = ''
    host = ''
    _is_ipv6 = None

    def __init__(self, nodestr=None, host="", port="", path=""):
        if nodestr is not None:
            nodestr = nodestr.strip().replace('+', '/')
            parsed = urllib.parse.urlparse('//' + nodestr)
            host = parsed.hostname
            port = parsed.port
            path = parsed.path
        if not host or not port:
            raise NodeError('bad format')
        port = int(port)
        path = path.replace('+', '/')

        self.nodestr, self.host, self._is_ipv6 = Node._create_nodestr(host, port, path)

    @classmethod
    def _create_nodestr(cls, host, port, path):
        try:
            h = host.replace('[', '').replace(']', '')
            addr = ipaddress.ip_address(h)
        except ValueError:
            nodestr = '%s:%d%s' % (host, port, path)
            return nodestr, host, None
        if hasattr(addr, 'ipv4_mapped') and addr.ipv4_mapped:
            addr = addr.ipv4_mapped
        if addr.version == 6:
            nodestr = '[%s]:%d%s' % (addr.compressed, port, path)
            return nodestr, addr.compressed, True
        else:
            nodestr = '%s:%d%s' % (addr.compressed, port, path)
            return nodestr, addr.compressed, False

    def __str__(self):
        return self.nodestr

    def __gt__(self, y):
        return str(self) > str(y)

    def __lt__(self, y):
        return str(self) < str(y)

    def __eq__(self, y):
        return str(self) == str(y)

    def __ne__(self, y):
        return str(self) != str(y)

    def toxstring(self):
        """Return string, ``/'' is replaced with ``+''."""
        return self.nodestr.replace("/", "+")

    def is_ipv6(self):
        if self._is_ipv6 is not None:
            return self._is_ipv6
        try:
            info = socket.getaddrinfo(self.host, 80, proto=socket.IPPROTO_TCP)
        except socket.gaierror:
            self._is_ipv6 = False
            return False
        for i in info:
            try:
                addr = ipaddress.ip_address(i[4][0])
            except (IndexError, ValueError):
                continue
            if hasattr(addr, 'ipv4_mapped') and addr.ipv4_mapped:
                addr = addr.ipv4_mapped
            if addr.version == 6:
                self._is_ipv6 = True
                return True
        self._is_ipv6 = False
        return False

    def talk(self, message):
        """Connect other node."""
        if not message.startswith("/"):
            message = "/" + message
        if message.startswith("/get"):
            socket.setdefaulttimeout(config.get_timeout)
        else:
            socket.setdefaulttimeout(config.timeout)

        message = 'http://%s%s' % (self, message)
        try:
            sys.stderr.write('talk: %s\n' % message)
            res = urlopen(message)
        except Exception as err:
            sys.stderr.write('%s: %s\n' % (message, err))
            return StringIO('')

        if res.info().get("Content-Encoding", "") == "gzip":
            buffer = BytesIO(res.read())
            return SocketIO(gzip.GzipFile(fileobj=buffer), message)
        else:
            return SocketIO(res, message)

    def ping(self):
        try:
            res = self.talk('/ping')
            first = next(iter(res))
            return first.strip() == 'PONG'
        except StopIteration:
            sys.stderr.write('/ping %s: error\n' % self)
            return False

    def join(self):
        '''Connect.
        '''
        try:
            if node_allow().check(str(self)):
                pass
            elif node_deny().check(str(self)):
                return (False, None)
            welcome = False
            extnode = None
            port = config.port
            path = config.server.replace('/', '+')
            name = config.dnsname
            res = self.talk('/join/%s:%d%s' % (name, port, path))
            lines = iter(res)
            welcome = (next(lines).strip() == 'WELCOME')
            extnode = Node(next(lines))
            return (welcome, extnode)
        except StopIteration:
            return (welcome, extnode)

    def get_node(self):
        try:
            res = self.talk('/node')
            first = next(iter(res))
            return Node(first)
        except StopIteration:
            sys.stderr.write('/node %s: error\n' % self)
            return None

    def bye(self):
        """Unconnect."""
        try:
            port = config.port
            path = config.server.replace('/', '+')
            name = config.dnsname
            res = self.talk('/bye/%s:%d%s' % (name, port, path))
            first = next(iter(res))
            return first.strip() == 'BYEBYE'
        except StopIteration:
            sys.stderr.write('/bye %s: error\n' % self)
            return False

# End of Node


class RawNodeList(list):

    """File includes list.

    One element par one line.
    """

    def __init__(self, filepath, caching=False):
        """Load list form file."""
        self.tiedlist = tiedlist(filepath, Node, caching)
        list.__init__(self, self.tiedlist.data)
        random.shuffle(self)

    def sync(self):
        self.tiedlist.sync()

    def random(self):
        return random.choice(self)

    def filterv4(self):
        return [i for i in self if not i.is_ipv6()]

    def filterv6(self):
        return [i for i in self if i.is_ipv6()]

    def append(self, node):
        if node_allow().check(str(node)):
            pass
        elif node_deny().check(str(node)):
            return
        if node not in self:
            list.append(self, node)
        self.tiedlist.append(node, False)

    def extend(self, nodes):
        for node in nodes:
            self.append(node)

    def remove(self, value):
        try:
            list.remove(self, value)
        except ValueError:
            pass
        try:
            self.tiedlist.remove(value)
        except ValueError:
            pass

# End of RawNodeList


class NodeList(RawNodeList):

    """Node list."""

    def __init__(self):
        RawNodeList.__init__(self, config.node, True)

    def myself(self):
        """Who am I."""
        port = config.port
        path = config.server
        dnsname = config.dnsname
        if dnsname != "":
            n = Node(host=dnsname, port=port, path=path)
            return n, n
        addr4 = {}
        addr6 = {}
        for n in self:
            try:
                res = n.talk('ping')
                lines = iter(res)
                buf = (next(lines), next(lines))
                if buf[0].strip() != 'PONG':
                    continue
                addr = buf[1].strip()
                if ':' in buf[1]:
                    addr6[addr] = addr6.get(addr, 0) + 1
                else:
                    addr4[addr] = addr4.get(addr, 0) + 1
            except Exception as err:
                sys.stderr.write('/ping %s: error: %s\n' % (n, err))
        node4 = None
        node6 = None
        if addr4:
            addr = sorted(addr4.keys(), key=addr4.get, reverse=True)[0]
            node4 = Node(host=addr, port=port, path=path)
        if addr6:
            addr = sorted(addr6.keys(), key=addr6.get)[0]
            node6 = Node(host=addr, port=port, path=path)
        return node4, node6

    def pingall(self):
        """Ping all nodes."""
        for n in self[0:]:
            if not n.ping():
                self.remove(n)

    def join(self, node):
        """Join network."""
        port = config.port
        count = 0
        flag = False
        while count < config.retry_join:
            count += 1
            (welcome, extnode) = node.join()
            if welcome and (extnode is None):
                self.append(node)
                return True
            elif welcome:
                self.append(node)
                node = extnode
                flag = True
            else:
                self.remove(node)
                return flag
        return flag

    def init(self):
        """Connect initial node."""
        port = config.port
        inodes = init_node()
        random.shuffle(inodes)
        for i in inodes:
            inode = Node(i)
            if inode.ping():
                self.join(inode)
                break
        myself4, myself6 = self.myself()
        if myself4 and (myself4 in self):
            self.remove(myself4)
        if myself6 and (myself6 in self):
            self.remove(myself6)
        if len(self) == 0:
            return

        done = {}
        for i in self[:]:
            if i != inode:
                self.join(i)
            done[str(i)] = 1

        while True:
            if not len(self):
                break
            n = random.choice(self)
            new = n.get_node()
            if (new is not None) and (str(new) not in done):
                self.join(new)
                done[str(new)] = 1
            done[str(n)] = done.get(str(n), 1) + 1
            if (done[str(n)] > config.retry) or (len(self) >= config.nodes):
                break

        if len(self) >= config.nodes:
            inode.bye()
            self.remove(inode)
        elif len(self) <= 1:
            sys.stderr.write("Warning: Few linked nodes.\n")
        while len(self.filterv4()) > config.nodes:
            n = random.choice(self.filterv4())
            n.bye()
            self.remove(n)
        while len(self.filterv6()) > config.nodes:
            n = random.choice(self.filterv6())
            n.bye()
            self.remove(n)

    def rejoin(self, searchlist):
        """Copy node from searchlist to nodelist."""
        do_join = False
        for n in searchlist:
            if n in self:
                pass
            elif len(self) >= config.nodes:
                break
            else:
                do_join = True
                flag = self.join(n)
                if (not flag) and (not n.ping()):
                    searchlist.remove(n)
        if do_join:
            searchlist.extend(self)
            self.sync()
            searchlist.sync()
        if len(self) <= 1:
            sys.stderr.write("Warning: Few linked nodes.\n")

    def tell_update(self, cache, stamp="", id="", node=None):
        """Tell update other nodes.

        If node is None, node is myself.
        """
        if node:
            tellstr = node.toxstring()
        elif config.dnsname:
            myself, _ = self.myself()
            tellstr = myself.toxstring()
        else:
            tellstr = ":" + str(config.port) + config.server.replace("/", "+")

        arg = "/".join(("", "update", cache.datfile, str(stamp), id, tellstr))

        broadcast = Broadcast(arg, cache)
        broadcast.start()

# End of NodeList


class SearchList(RawNodeList):

    """List of existing nodes."""

    def __init__(self):
        RawNodeList.__init__(self, config.search, True)

    def join(self, node):
        '''Add node.
        '''
        if node not in self:
            self.append(node)

    def search(self, cache=None, myself4=None, myself6=None, nodes=None):
        """Search node which has the file."""
        nodelist = NodeList()
        random.shuffle(self)
        count = 0
        if nodes:
            random.shuffle(nodes)
            target = nodes
            for i in self:
                if i not in nodes:
                    target.append(i)
        else:
            target = self
        for n in target:
            if myself4 and (n == myself4):
                continue
            elif myself6 and (n == myself6):
                continue
            elif (not node_allow().check(str(n))) and \
                 node_deny().check(str(n)):
                continue
            count += 1
            lookuptable = LookupTable()
            res = n.talk('/have/' + cache.datfile)
            try:
                first = next(iter(res)).strip()
            except StopIteration:
                first = ''
            if first == 'YES':
                self.sync()
                lookuptable.add(cache.datfile, n)
                lookuptable.sync()
                return n
            elif first == 'NO':
                pass
            elif not n.ping():
                self.remove(n)
                cache.node.remove(n)
            if n in lookuptable.get(cache.datfile, []):
                lookuptable.remove(cache.datfile, n)
            if count > config.search_depth:
                break
        self.sync()
        if count <= 1:
            sys.stderr.write("Warning: Search nodes are null.\n")
        return None

# End of SearchList


class LookupTable:
    '''Filename to Node Mapping Table.

    data: lookuptable[filename] = [node1, node2, ...]
    '''

    def __init__(self):
        self.tosave = False
        self.tieddict = tieddict(config.lookup, Node, True)

    def sync(self, force=True):
        if self.tosave or force:
            self.tieddict.sync()

    def add(self, datfile, node):
        self.tieddict.append(datfile, node, False)
        self.tosave = True

    def remove(self, datfile, node):
        self.tieddict.remove(datfile, node)
        self.tosave = True

    def clear(self):
        for key in list(self.tieddict.keys()):
            del self.tieddict[key]

    def get(self, key, default=None):
        return self.tieddict.get(key, default)

# End of LookupTable
