import threading
import time

from shingetsu import cache
from shingetsu import config
from shingetsu import util

from . import utils


class _DatkeyTable:
    def __init__(self, file):
        self.file = file
        self.datkey2filekey = {}  # epoch stamp -> `Cache.datfile`
        self.filekey2datkey = {}  # `Cache.datfile` -> epoch stamp
        self.lock = threading.Lock()


    def load(self):
        try:
            with util.opentext(self.file, 'r') as f:
                for line in f:
                    try:
                        # format -> `12345<>thread_FFFF\n`
                        stamp, filekey = line.strip().split('<>', 1)
                        stamp = int(stamp)
                    except ValueError:
                        continue
                    self.set_entry(stamp, filekey)

        except IOError:
            pass


    def save(self):
        try:
            with util.opentext(self.file, 'w') as f:
                for stamp, filekey in self.datkey2filekey.items():
                    f.write(str(stamp) + '<>' + filekey + '\n')

        except IOError:
            utils.log('keylib._DatkeyTable.save fails')


    def set_entry(self, stamp, filekey):
        with self.lock:
            self.datkey2filekey[stamp] = filekey
            self.filekey2datkey[filekey] = stamp


    def set_from_cache(self, cache):
        if cache.datfile in self.filekey2datkey:
            return

        try:
            rec = cache[cache.keys()[0]]  # first record
            first_stamp = int(rec.stamp)
        except IndexError:
            first_stamp = cache.recent_stamp  # if don't have recent_stamp, it's 0
        if not first_stamp:
            first_stamp = int(time.time() - 24 * 60 * 60)

        # avoid duplication
        while first_stamp in self.datkey2filekey:
            first_stamp += 1

        self.set_entry(first_stamp, cache.datfile)


    def get_datkey(self, filekey):
        if filekey in self.filekey2datkey:
            return self.filekey2datkey[filekey]

        # because saku don't have this cache at start
        c = cache.Cache(filekey)
        c.load()
        self.set_from_cache(c)

        self.save()  # don't lose entry

        if filekey in self.filekey2datkey:
            return self.filekey2datkey[filekey]

        raise DatkeyNotFound(filekey + ' not found')


    def get_filekey(self, datkey):
        datkey = int(datkey)
        if datkey in self.datkey2filekey:
            return self.datkey2filekey[datkey]

        raise DatkeyNotFound('%d not found' % datkey)


class DatkeyNotFound(Exception):
    pass


_datkey_table = _DatkeyTable(config.run_dir + '/datkey.txt')


def get_datkey(filekey):
    return _datkey_table.get_datkey(filekey)


def get_filekey(datkey):
    return _datkey_table.get_filekey(datkey)


def load():
    _datkey_table.load()

    for c in cache.CacheList():
        c.load()
        _datkey_table.set_from_cache(c)

    # Because CacheList don't list all cache
    for rec in cache.RecentList():
        c = cache.Cache(rec.datfile)
        c.load()

        c.recent_stamp = rec.stamp  # if cache has no records, use recent_stamp
        _datkey_table.set_from_cache(c)

    save()

def save():
    _datkey_table.save()
