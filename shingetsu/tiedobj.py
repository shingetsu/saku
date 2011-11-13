'''Tied List and Dictionaly.
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
from compatible import RLock

import config

__version__ = '$Revision$'
__all__ = ['tiedlist', 'tieddict']

lock = RLock()

_cache = {}


def reset():
    try:
        lock.acquire(True)
        global _cache
        _cache = {}
    finally:
        lock.release()


class ListFile:
    '''File includes list.

    One element par one line.
    '''

    def __init__(self, path, elemclass=None, caching=False):
        '''Constructor.

        None for path do not tie file.
        '''
        self.data = []
        self.path = path
        self.elemclass = elemclass
        self.caching = caching
        if path is None:
            caching = False
            self.caching = False
        try:
            if (self.path is not None) and os.path.isfile(self.path):
                for line in file(self.path):
                    if self.elemclass is not None:
                        try:
                            obj = self.elemclass(line.strip())
                            if obj is not None:
                                self.data.append(obj)
                        except Exception, err:
                            sys.stderr.write('ListFile: %s\n' % err)
                    else:
                        self.data.append(line.strip())
        except (IOError, OSError), err:
            sys.stderr.write('%s: %s\n' % (self.path, err))
        if caching and (self.path not in _cache) \
                   and os.path.isfile(self.path):
            _cache[self.path] = self

    def __iter__(self):
        return iter(self.data)

    def __getslice__(self, i, j):
        return self.data[i:j]

    def append(self, data, allow_duplication=True):
        try:
            lock.acquire(True)
            if allow_duplication or (data not in self):
                self.data.append(data)
        finally:
            lock.release()

    def remove(self, data):
        try:
            lock.acquire(True)
            try:
                self.data.remove(data)
            except ValueError:
                pass
        finally:
            lock.release()

    def sync(self):
        try:
            lock.acquire(True)
            if self.caching:
                _cache[self.path] = self
            elif self.path in _cache:
                del _cache[self.path]
            f = file(self.path, 'wb')
            for elem in self.data:
                f.write('%s\n' % elem)
            f.close()
        finally:
            lock.release()

# End of ListFile


class DictFile:
    '''File includes dictionary.

    data: sugtags[filename] = [1, 2, ...]
    file format: filename<>1 2 ...
    '''

    def __init__(self, path, elemclass=None, caching=False, listclass=None):
        self.data = {}
        self.path = path
        self.caching = caching
        try:
            if (self.path is not None) and os.path.isfile(self.path):
                for line in file(self.path):
                    try:
                        key, str_values = line.strip().split('<>', 1)
                        if listclass is not None:
                            self.data[key] = listclass()
                        else:
                            self.data[key] = []
                        for elem in str_values.strip().split():
                            if elemclass is not None:
                                try:
                                    obj = elemclass(elem)
                                    if obj is not None:
                                        self.data[key].append(obj)
                                except Exception, err:
                                    sys.stderr.write('DictFile: %s\n' % err)
                            else:
                                self.data[key].append(line.strip())
                    except ValueError, err:
                        sys.stderr.write('%s: %s\n' % (self.path, err))
        except (IOError, OSError), err:
            sys.stderr.write('%s: %s\n' % (self.path, err))

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default):
        return self.data.get(key, default)

    def keys(self):
        return self.data.keys()

    def __setitem__(self, key, data):
        try:
            lock.acquire(True)
            self.data[key] = data
        finally:
            lock.release()

    def __delitem__(self, key):
        try:
            lock.acquire(True)
            try:
                del self.data[key]
            except KeyError:
                pass
        finally:
            lock.release()

    def append(self, key, data, allow_duplication=True):
        try:
            lock.acquire(True)
            if key in self.data:
                if allow_duplication or (data not in self.data[key]):
                    self.data[key].append(data)
            else:
                self.data[key] = [data]
        finally:
            lock.release()

    def remove(self, key, data):
        try:
            lock.acquire(True)
            try:
                if key in self.data:
                    self.data[key].remove(data)
            except (ValueError, KeyError):
                pass
            try:
                if not self.data[key]:
                    del self.data[key]
            except KeyError:
                pass
        finally:
            lock.release()

    def sync(self):
        try:
            lock.acquire(True)
            if self.caching:
                _cache[self.path] = self
            elif self.path in _cache:
                del _cache[self.path]
            f = file(self.path, 'wb')
            for key in self.data:
                f.write('%s<>%s\n' %
                        (key, ' '.join([str(i) for i in self.data[key]])))
            f.close()
        finally:
            lock.release()

# End of DictFile


def tiedlist(path, elemclass=None, caching=False):
    if path in _cache:
        return _cache[path]
    else:
        try:
            lock.acquire(True)
            if path in _cache:
                return _cache[path]
            else:
                return ListFile(path, elemclass, caching)
        finally:
            lock.release()

def tieddict(path, elemclass=None, caching=False, listclass=None):
    if path in _cache:
        return _cache[path]
    else:
        try:
            lock.acquire(True)
            if path in _cache:
                return _cache[path]
            else:
                return DictFile(path, elemclass, caching, listclass)
        finally:
            lock.release()
