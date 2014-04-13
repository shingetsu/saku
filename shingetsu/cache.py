"""Cache of Saku BBS.
"""
#
# Copyright (c) 2005-2014 shinGETsu Project.
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

import base64
import hashlib
import imghdr
import os
import random
import re
import shutil
import sys
from threading import RLock
from time import time

from shingetsu import apollo
from shingetsu import config
from shingetsu import spam
from shingetsu import title
from shingetsu.node import *
from shingetsu.tag import *
from shingetsu.tiedobj import *

try:
    import PIL.Image
except ImportError:
    PIL = None

__all__ = ['Record', 'Cache', 'CacheList', 'UpdateList', 'RecentList']

lock = RLock()


def md5digest(s):
    """Get MD5 hex digest.
    >>> md5digest('abc')
    '900150983cd24fb0d6963f7d28e17f72'
    >>> md5digest(b'abc')
    '900150983cd24fb0d6963f7d28e17f72'
    """
    if isinstance(s, str):
        s = s.encode('utf-8', 'replace')
    return hashlib.md5(s).hexdigest()

def fsdiff(f, s):
    '''Diff between file and string.

    Return same data or not.
    '''
    try:
        if os.path.isfile(f):
            buf = open(f, 'rb').read()
        else:
            buf = ''
    except (IOError, OSError) as e:
        sys.stderr.write('%s: %s\n' % (f, e))
        buf = ''
    if len(s) != len(buf):
        return False
    else:
        return s == buf
# End of sfdiff


class Record(dict):

    """One article of BBS.

    timestamp<>id<>foo:bar<>hoge:fuga<>...
    """

    recstr = ""     # record in string format
    datfile = ""    # cache file
    stamp = 0       # date when the record made
    id = ""         # md5sum
    idstr = ""      # stamp_id
    path = ""       # path for real file
    body_path = ''  # path for body (record without attach field)
    rm_path = ""    # path for removed marker
    flag_load = False
    flag_load_body = False

    def __init__(self, datfile="", idstr=""):
        dict.__init__(self)
        self.datfile = datfile
        self.idstr = idstr

        if idstr != "":
            buf = idstr.split("_")
            try:
                self.stamp = int(buf[0])
                self.id = buf[1]
            except (ValueError, IndexError):
                sys.stderr.write('%s: bad format\n' % idstr)
                pass
        self.setpath()

    def free(self):
        self.flag_load = False
        self.flag_load_body = False
        self.recstr = ''
        self.clear()

    def __str__(self):
        return self.recstr

    def __gt__(self, y):
        if self.stamp != y.stamp:
            return self.stamp > y.stamp
        else:
            return self.idstr > y.idstr

    def __lt__(self, y):
        if self.stamp != y.stamp:
            return self.stamp < y.stamp
        else:
            return self.idstr < y.idstr

    def __eq__(self, y):
        return self.idstr == y.idstr

    def __ne__(self, y):
        return self.idstr != y.idstr

    def setpath(self):
        if (self.idstr == "") or (self.datfile == ""):
            return
        self.dathash = title.file_hash(self.datfile)
        self.path = os.path.join(config.cache_dir,
                                 self.dathash,
                                 'record',
                                 self.idstr)
        self.body_path = os.path.join(config.cache_dir,
                                      self.dathash,
                                      'body',
                                      self.idstr)
        self.rm_path = os.path.join(config.cache_dir,
                                    self.dathash,
                                    'removed',
                                    self.idstr)

    def parse(self, recstr):
        """Parse cache record."""
        self.recstr = re.sub(r"[\r\n]*$", "", recstr)
        tmp = self.recstr.split("<>")
        try:
            self['stamp'] = tmp.pop(0)
            self['id'] = tmp.pop(0)
            self.idstr = self['stamp'] + '_' + self['id']
            self.stamp = int(self['stamp'])
            self.id = self['id']
        except (ValueError, KeyError, IndexError):
            sys.stderr.write(recstr + ': bad format\n')
            return False
        for i in tmp:
            buf = i.split(":", 1)
            if len(buf) >= 2:
                buf[1] = re.sub(r"<br>", "\n", buf[1])
                buf[1] = re.sub(r"<", "&lt;", buf[1])
                buf[1] = re.sub(r">", "&gt;", buf[1])
                buf[1] = re.sub(r"\n", "<br>", buf[1])
                if buf[0] == 'attach':
                    self[buf[0]] = buf[1]
                else:
                    self[buf[0]] = buf[1]
        if self.get('attach', '') != '1':
            self.flag_load = True
        self.flag_load_body = True
        self.setpath()
        return True

    def _load(self, filename):
        if self.path == '':
            sys.stderr.write('Null file name\n')
            return False
        try:
            if self.size() <= 0:
                self.remove()
                return False
            f = open(filename)
            parse_ok = self.parse(f.readline())
            f.close()
            return parse_ok
        except (IOError, OSError) as err:
            sys.stderr.write('IOError/OSError: %s\n' % err)
            self.free()
            return False

    def load(self):
        if not self.flag_load:
            return self._load(self.path)
        return True

    def load_body(self):
        if self.flag_load_body:
            return True
        elif os.path.isfile(self.body_path):
            return self._load(self.body_path)
        else:
            return self.load()

    def build(self, stamp, body, passwd=""):
        target = list(body.keys())
        bodyary = []
        for key in target:
            bodyary.append(key + ":" + body[key])
            self[key] = body[key]
        bodystr = "<>".join(bodyary)
        if passwd != "":
            (pubkey, prikey) = apollo.key_pair(passwd)
            md = md5digest(bodystr)
            sign = apollo.sign(md, pubkey, prikey)
            self["pubkey"] = pubkey
            self["sign"] = sign
            self["target"] = ",".join(target)

            bodystr += "<>pubkey:" + pubkey + \
                       "<>sign:" + sign + \
                       "<>target:" + ",".join(target)

        id = md5digest(bodystr)
        self.stamp = int(stamp)
        self.recstr = str(stamp) + "<>" + id + "<>" + bodystr
        self.idstr = str(stamp) + "_" + id
        self["stamp"] = str(stamp)
        self["id"] = id
        self.id = id
        self.setpath()
        return id

    def md5check(self):
        buf = str(self).split("<>", 2)
        if (len(buf) > 2):
            return md5digest(buf[2]) == self['id']
        else:
            return False

    def allthumbnail_path(self):
        if self.path == "":
            sys.stderr.write("Null file name\n")
            return None
        dir = "/".join((config.cache_dir, self.dathash, "attach"))
        thumbnail = []
        for i in os.listdir(dir):
            if i.startswith("s" + self.idstr):
                thumbnail.append("/".join((dir, i)))
        return thumbnail

    def attach_path(self, suffix=None, thumbnail_size=None):
        if self.path == "":
            sys.stderr.write("Null file name\n")
            return None
        dir = "/".join((config.cache_dir, self.dathash, "attach"))
        if suffix is not None:
            suffix = re.sub(r"[^-_.A-Za-z0-9]", "", suffix)
            if suffix == "":
                suffix = "txt"
            if thumbnail_size is not None:
                return dir + "/" + "s" + self.idstr + "." + thumbnail_size + "." + suffix
            else:
                return dir + "/" + self.idstr + "." + suffix
        for i in os.listdir(dir):
            if i.startswith(self.idstr):
                return dir + "/" + i
        return None

    def attach_size(self, path=None, suffix=None, thumbnail_size=None):
        if path is None:
            path = self.attach_path(suffix=suffix, thumbnail_size=thumbnail_size)
        if path is None:
            return 0
        else:
            return os.path.getsize(path)

    def _write_file(self, path, data):
        """Save data to file."""
        if path == "":
            sys.stderr.write("Null file name\n")
            return False
        try:
            f = open(path, "wb")
            if isinstance(data, str):
                data = data.encode('utf-8', 'replace')
            f.write(data)
            f.close()
            return True
        except IOError:
            sys.stderr.write(path + ": IOError\n")
            return False

    def make_thumbnail(self, suffix=None, thumbnail_size=config.thumbnail_size):
        if thumbnail_size is None:
            return
        if not PIL:
            return
        if suffix is None:
            suffix = self.get('suffix', 'jpg')
        attach_path = self.attach_path(suffix=suffix)
        thumbnail_path = self.attach_path(suffix=suffix, thumbnail_size=thumbnail_size)
        if os.path.isfile(thumbnail_path):
            return
        if not imghdr.what(attach_path):
            return
        size = thumbnail_size.split("x")
        if len(size) != 2:
            return
        size = (int(size[0]), int(size[1]))
        try:
            im = PIL.Image.open(attach_path)
            im.thumbnail(size, PIL.Image.ANTIALIAS)
            im.save(thumbnail_path)
        except (IOError, KeyError) as err:
            sys.stderr.write('PIL error: %s for %s\n' % (err, attach_path))
        return

    def sync(self, force=False):
        """Save files."""
        if self.removed():
            return
        elif (not force) and self.exists():
            pass
        else:
            self._write_file(self.path, str(self)+"\n")
        body = self.body_string()+'\n'
        if 'attach' in self:
            attach = base64.decodestring(self['attach'].encode('utf-8'))
            attach_path = self.attach_path(self.get('suffix', 'txt'))
            thumbnail_path = self.attach_path(self.get('suffix', 'jpg'),
                                thumbnail_size=config.thumbnail_size)
            if force or (not fsdiff(self.body_path, body)):
                self._write_file(self.body_path, body)
            if force or (not fsdiff(attach_path, attach)):
                self._write_file(attach_path, attach)
            if force or (not os.path.isfile(thumbnail_path)):
                self.make_thumbnail()
        if 'sign' in self:
            if force or (not fsdiff(self.body_path, body)):
                self._write_file(self.body_path, body)

    def body_string(self):
        """Remove attach field."""
        buf = [self["stamp"], self["id"]]
        for k in self:
            if k in ("stamp", "id"):
                pass
            elif k == "attach":
                buf.append("attach:1")
            elif k == "sign":
                pass
            elif k == "pubkey":
                if self.check_sign():
                    short_key = apollo.cut_key(self["pubkey"])
                    buf.append("pubkey:" + short_key)
            else:
                buf.append(k + ":" + self[k])
        return "<>".join(buf)

    def check_sign(self):
        """Check sigunature."""
        for k in ("pubkey", "sign", "target"):
            if k not in self:
                return False
        target = ""
        for t in self["target"].split(","):
            try:
                target += "<>" + t + ":" + self[t]
            except KeyError:
                return False
            except ValueError:
                return False
        target = target[2:]         # remove ^<>

        md = md5digest(target)
        if apollo.verify(md, self["sign"], self["pubkey"]):
            return True
        else:
            return False

    def exists(self):
        return os.path.isfile(self.path)

    def removed(self):
        return os.path.isfile(self.rm_path)

    def size(self):
        try:
            return os.path.getsize(self.path)
        except OSError as err:
            sys.stderr.write('OSError: %s\n' % err)
            return 0

    def remove(self):
        """Remove record.

        The record is removed from cache,
        but do not removed from file-system.
        """
        try:
            shutil.move(self.path, self.rm_path)
            for path in self.allthumbnail_path():
                if path and os.path.isfile(path):
                    os.remove(path)
            for path in (self.body_path, self.attach_path()):
                if path and os.path.isfile(path):
                    os.remove(path)
            self.free()
            return True
        except (IOError, OSError) as err:
            sys.stderr.write('IOError/OSError: %s\n' % err)
            self.free()
            return False

# End of Record


class RecordGetter:
    '''Iterator to get records with heads.
    '''
    def __init__(self, datfile, node, head):
        self.datfile = datfile
        self.node = node
        self.head = head

    def __iter__(self):
        for h in self.head:
            r = Record(datfile = self.datfile,
                       idstr = h.strip().replace('<>', '_'))
            if not (r.exists() or r.removed()):
                try:
                    res = self.node.talk('/get/%s/%d/%s' %
                                    (self.datfile, r.stamp, r.id))
                    first = re.sub(r'[\r\n]*$', '', next(iter(res)))
                    yield first
                except StopIteration as err:
                    sys.stderr.write('get %s: %s\n' % (self, err))

# End of RecordGetter


class Cache(dict):

    """Cache of BBS.

    Plain text (encode: UTF-8).
    One record par one line.
    """

    datfile = ""
    datpath = config.cache_dir
    stamp = 0       # when the cache is modified
    size = 0        # size of cache file
    count = 0       # records count
    loaded = False  # loaded records
    type = ""       # "thread"

    def __init__(self, datfile, sugtagtable=None, recentlist=None):
        dict.__init__(self)
        self.datfile = datfile
        self.dathash = title.file_hash(datfile)
        self.datpath += "/" + self.dathash
        self.removed = {}

        self.stamp = self._load_status('stamp')
        self.valid_stamp = self._load_status('validstamp')
        self.recent_stamp = self.stamp
        if recentlist is None:
            recentlist = RecentList()
        if self.datfile in recentlist.lookup:
            recent_stamp = recentlist.lookup[self.datfile].stamp
            if self.recent_stamp < recent_stamp:
                self.recent_stamp = recent_stamp
        self.size = self._load_status('size')
        self.count = self._load_status('count')
        self.node = RawNodeList(os.path.join(self.datpath, 'node.txt'))
        self.tags = TagList(self.datfile,
                            os.path.join(self.datpath, 'tag.txt'))
        if sugtagtable is None:
            sugtagtable = SuggestedTagTable()
        if self.datfile in sugtagtable:
            self.sugtags = sugtagtable[self.datfile]
        else:
            self.sugtags = SuggestedTagList(sugtagtable, self.datfile)

        for type in config.types:
            if self.datfile.startswith(type):
                self.type = type
                break

        self.save_record = config.save_record.get(self.type, 0)
        self.save_size = config.save_size.get(self.type, 1)
        self.get_range = config.get_range.get(self.type, 0)
        self.sync_range = config.sync_range.get(self.type, 0)
        self.save_removed = config.save_removed.get(self.type, 0)

        if self.sync_range == 0:
            self.save_removed = 0
        elif self.save_removed == 0:
            pass
        elif self.save_removed <= self.sync_range:
            self.save_removed = self.sync_range + 1

    def __str__(self):
        return self.datfile

    def __len__(self):
        return self.count

    def keys(self):
        self.load()
        k = list(dict.keys(self))
        k.sort()
        return k

    def __iter__(self):
        for idstr in list(self.keys()):
            yield self[idstr]

    def load(self):
        if (not self.loaded) and self.exists():
            self.loaded = True
            try:
                for k in os.listdir(self.datpath + "/record"):
                    self[k] = Record(datfile=self.datfile, idstr=k)
            except OSError:
                sys.stderr.write("%s/record: OSError\n" % self.datpath)

    def exists(self):
        return self.datpath and os.path.isdir(self.datpath)

    def has_record(self):
        removed = self.datpath + "/removed"
        return bool(self) or \
               (os.path.exists(removed) and
                bool(os.listdir(removed)))

    def _load_status(self, key):
        path = "%s/%s.stat" % (self.datpath, key)
        try:
            f = open(path)
            v = f.readline()
            f.close()
            return int(v.strip())
        except IOError:
            #sys.stderr.write(path + ": IOError\n")
            return 0
        except ValueError:
            sys.stderr.write(path + ": ValueError\n")
            return 0

    def _save_status(self, key, val):
        path = "%s/%s.stat" % (self.datpath, key)
        try:
            buf = str(val) + '\n'
            if not fsdiff(path, buf):
                try:
                    lock.acquire(True)
                    f = open(path, 'wb')
                    f.write(buf.encode('utf-8', 'replace'))
                    f.close()
                finally:
                    lock.release()
            return True
        except IOError:
            sys.stderr.write(path + ": IOError\n")
            return False

    def sync_status(self):
        self._save_status('stamp', self.stamp)
        self._save_status('validstamp', self.valid_stamp)
        self._save_status('size', self.size)
        self._save_status('count', self.count)
        if not os.path.exists(self.datpath + '/dat.stat'):
            self._save_status('dat', self.datfile)

    def standby_directories(self):
        for d in ('', '/attach', '/body', '/record', '/removed'):
            if not os.path.isdir(self.datpath + d):
                try:
                    os.makedirs(self.datpath + d)
                except (IOError, OSError):
                    sys.stderr.write(self.datfile + ": IOError/OSError\n")

    def check_data(self, res, stamp=None, id=None, begin=None, end=None):
        '''Check a data and add it cache.'''
        flag_got = False
        flag_spam = False
        count = 0
        for i in res:
            count += 1
            r = Record(datfile=self.datfile)
            parse_ok = r.parse(i)
            if parse_ok and \
               ((stamp is None) or (r['stamp'] == str(stamp))) and \
               ((not id) or (r['id'] == id)) and \
               ((begin is None) or (begin <= r.stamp)) and \
               ((end is None) or (r.stamp <= end)) and \
               r.md5check():
                flag_got = True
                if (len(i) > config.record_limit*1024) or spam.check(i):
                    sys.stderr.write(
                        'Warning: %s/%s: too large or spam record.\n' %
                        (self.datfile, r.idstr))
                    self.add_data(r, False)
                    r.remove()
                    flag_spam = True
                else:
                    self.add_data(r)
            else:
                if stamp is not None:
                    str_stamp = '/%s' % stamp
                elif 'stamp' in r:
                    str_stamp = '/%s' % r['stamp']
                else:
                    str_stamp = ''
                sys.stderr.write("Warning: %s%s: broken record.\n" %
                                 (self.datfile, str_stamp))
            r.free()
        return count, flag_got, flag_spam

    def get_data(self, stamp=0, id="", node=None):
        """Get appointed data."""
        res = node.talk("/get/" + self.datfile + "/" + str(stamp) + "/" + id)
        count, flag_got, flag_spam = self.check_data(res, stamp=stamp, id=id)
        if count:
            self.sync_status()
        else:
            sys.stderr.write("Warning: %s/%s: records not found.\n" %
                             (self.datfile, stamp))
        return flag_got, flag_spam

    def get_with_range(self, node=None):
        """Get data in range."""
        oldcount = len(self)
        now = int(time())
        if self.stamp > 0:
            begin = self.stamp
        else:
            begin = 0
        if self.sync_range > 0:
            begin2 = now - self.sync_range
        else:
            begin2 = 0
        if begin < 0:
            begin = 0
        elif begin2 < begin:
            begin = begin2

        if (begin <= 0) and (len(self) <= 0):
            if self.get_range > 0:
                begin = now - self.get_range
                if begin < 0:
                    begin = 0
            else:
                begin = 0
            res = node.talk('/get/%s/%d-' % (self.datfile, begin))
        else:
            head = node.talk('/head/%s/%d-' % (self.datfile, begin))
            res = RecordGetter(self.datfile, node, head)

        count, flag_got, flag_spam = self.check_data(res, begin=begin, end=now)
        if count:
            self.sync_status()
            if oldcount == 0:
                self.loaded = True
        return bool(count)

    def add_data(self, rec, really=True):
        """Add new data cache."""
        self.standby_directories()
        rec.sync()
        if really:
            self[rec.idstr] = rec
            self.size += len(str(rec)) + 1
            self.count += 1
        if really:
            if self.valid_stamp < rec.stamp:
                self.valid_stamp = rec.stamp
        if self.stamp < rec.stamp:
            self.stamp = rec.stamp

    def check_body(self):
        '''Remove body cache that is a field of removed record.'''
        try:
            dir = os.path.join(config.cache_dir, self.dathash, 'body')
            for idstr in os.listdir(dir):
                rec = Record(datfile=self.datfile, idstr=idstr)
                if not rec.exists():
                    try:
                        os.remove(os.path.join(dir, idstr))
                    except OSError as err:
                        sys.stderr.write("%s/%s: OSError: %s\n" %
                                         (dir, idstr, err))
        except (IOError, OSError) as err:
            sys.stderr.write('IOError/OSError: %s\n' % err)

    def check_attach(self):
        """Remove attach cache that is a field of removed record."""
        try:
            dir = os.path.join(config.cache_dir, self.dathash, 'attach')
            for f in os.listdir(dir):
                idstr = f
                i = f.find(".")
                if i >= 0:
                    idstr = f[:i]
                if idstr.startswith('s'):
                    idstr = idstr[1:]
                rec = Record(datfile=self.datfile, idstr=idstr)
                if not rec.exists():
                    try:
                        os.remove(dir + "/" + f)
                    except OSError as err:
                        sys.stderr.write('OSError: %s\n' % err)
        except (IOError, OSError) as err:
            sys.stderr.write('IOError/OSError: %s\n' % err)

    def remove(self):
        """Remove cache (a.k.a DATFILE).

        It is removed from disk.
        """
        try:
            shutil.rmtree(self.datpath)
            return True
        except (IOError, OSError) as err:
            sys.stderr.write('IOError/OSError: %s\n' % err)
            return False

    def remove_records(self, now, limit):
        '''Remove records which are older than limit.
        '''
        # Remove old records.
        ids = list(self.keys())
        if self.save_size < len(ids):
            ids = ids[:-self.save_size]
            if limit > 0:
                for r in ids:
                    rec = self[r]
                    if rec.stamp + limit < now:
                        rec.remove()

        # Remove redundant records.
        once = set()
        ids = list(self.keys())
        for r in ids:
            rec = self[r]
            if not rec.exists():
                pass
            elif rec.id in once:
                rec.remove()
            else:
                once.add(rec.id)

    def search(self, searchlist=None, myself=None):
        """Search node from network and get records."""
        self.standby_directories()
        if searchlist is None:
            searchlist = SearchList()
        if not myself:
            nodelist = NodeList()
            myself = nodelist.myself()
        lookuptable = LookupTable()
        node = searchlist.search(self,
                                 myself = myself,
                                 nodes = lookuptable.get(self.datfile, []))
        if node is not None:
            nodelist = NodeList()
            if node not in nodelist:
                nodelist.append(node)
                nodelist.sync()
            self.get_with_range(node)
            if node not in self.node:
                while len(self.node) >= config.share_nodes:
                    n = self.node.random()
                    self.node.remove(n)
                self.node.append(node)
                self.node.sync()
            return True
        else:
            self.sync_status()
            return False

# End of Cache


class CacheList(list):

    """All cache."""

    def __init__(self):
        list.__init__(self)
        self.load()

    def load(self):
        sugtagtable = SuggestedTagTable()
        recentlist = RecentList()
        del self[:]
        for i in os.listdir(config.cache_dir):
            if config.cache_hash_method == 'asis':
                c = Cache(i, sugtagtable, recentlist)
                self.append(c)
                continue
            try:
                f = open(config.cache_dir + "/" + i + "/dat.stat")
                dat_stat = f.readlines()[0].strip()
                f.close()
                c = Cache(dat_stat, sugtagtable, recentlist)
                self.append(c)
                f.close()
            except IOError:
                c = Cache(i, sugtagtable, recentlist)
                self.append(c)

    def rehash(self):
        """Rename file path hash if it is old.
        """
        to_reload = False
        for i in os.listdir(config.cache_dir):
            try:
                dat_stat_file = os.path.join(config.cache_dir, i, 'dat.stat')
                if os.path.isfile(dat_stat_file):
                    f = open(dat_stat_file)
                    dat_stat = f.readlines()[0].strip()
                    f.close()
                else:
                    dat_stat = i
                    f = open(dat_stat_file, 'wb')
                    f.write(i + '\n')
                    f.close()
                hash = title.file_hash(dat_stat)
                if i == hash:
                    continue
                sys.stderr.write('rehash %s to %s\n' % (i, hash))
                shutil.move(os.path.join(config.cache_dir, i),
                            os.path.join(config.cache_dir, hash))
                to_reload = True
            except (IOError, OSError, IndexError) as err:
                sys.stderr.write('rehash error %s for %s\n' % (err, i))
        if to_reload:
            self.load()

    def getall(self, timelimit=0):
        """Search nodes and update my cache."""
        random.shuffle(self)
        nodelist = NodeList()
        myself = nodelist.myself()
        searchlist = SearchList()
        for cache in self:
            if int(time()) > timelimit:
                sys.stderr.write("client timeout\n")
                return
            elif not cache.exists():
                pass
            else:
                cache.search(searchlist=searchlist, myself=myself)
                cache.size = 0
                cache.count = 0
                cache.valid_stamp = 0
                for rec in cache:
                    if not rec.exists():
                        continue
                    load_ok = rec.load()
                    if load_ok:
                        if cache.stamp < rec.stamp:
                            cache.stamp = rec.stamp
                        if cache.valid_stamp < rec.stamp:
                            cache.valid_stamp = rec.stamp
                        cache.size += len(str(rec))
                        cache.count += 1
                        rec.sync()
                        rec.free()
                    else:
                        rec.remove()
                cache.check_body()
                cache.check_attach()
                cache.sync_status()

    def search(self, query):
        result = []
        for cache in self:
            for rec in cache:
                try:
                    rec.load_body()
                    if query.search(str(rec)):
                        result.append(cache)
                        rec.free()
                        break
                except (IOError, OSError, UnicodeDecodeError):
                    pass
                rec.free()
        return result

    def clean_records(self):
        """Clean old records."""
        now = int(time())
        for cache in self:
            cache.remove_records(now, cache.save_record)

    def remove_removed(self):
        """Remove removed record from disk."""
        now = int(time())
        for cache in self:
            for r in os.listdir(cache.datpath + "/removed"):
                rec = Record(datfile=cache.datfile, idstr=r)
                if (cache.save_removed > 0) and \
                   (rec.stamp + cache.save_removed < now) and \
                   (rec.stamp < cache.stamp):
                    try:
                        os.remove(cache.datpath + "/removed/" + r)
                    except OSError as xxx_todo_changeme:
                        (errno, errorstr) = xxx_todo_changeme.args
                        sys.stderr.write("OSError: %s: %s\n" %
                                         (cache.datpath + "/removed/" + r,
                                          errorstr))

# End of CacheList


class VirtualRecord(Record):
    '''Record like object for UpdateList.
    '''
    def __str__(self):
        line = "<>".join((str(self.stamp), self.id, self.datfile))
        return line

    def __eq__(self, r):
        return (self.stamp == r.stamp) and \
               (self.id == r.id) and \
               (self.datfile == r.datfile)

# End of VirtualRecord


class UpdateList:

    """Save update information.

    Get update if the system does not have the update.
    """

    def __init__(self,
                 update_file = config.update,
                 update_range = config.update_range):
        self.update_file = update_file
        self.update_range = update_range
        self.lookup = {}
        self.tiedlist = tiedlist(self.update_file,
                                 self.make_record,
                                 True)

    def __iter__(self):
        return iter(self.tiedlist)

    def __getitem__(self, i):
        return self.tiedlist[i]

    def append(self, rec):
        rec = VirtualRecord(datfile=rec.datfile, idstr=rec.idstr)
        self.tiedlist.append(rec, False)

    def remove(self, rec):
        self.tiedlist.remove(rec)

    def make_record(self, line):
        buf = re.sub(r'[\r\n]*$', '', line).split('<>')
        if (len(buf) > 2) and buf[0] and buf[1] and buf[2]:
            idstr = buf[0] + '_' + buf[1]
            vr = VirtualRecord(datfile=buf[2], idstr=idstr)
            vr.parse(line)
            return vr
        return None

    def add_lookup(self, rec):
        if rec.datfile in self.lookup:
            if self.lookup[rec.datfile].stamp < rec.stamp:
                self.lookup[rec.datfile] = rec
        else:
            self.lookup[rec.datfile] = rec

    def sync(self):
        """Save update list."""
        now = int(time())
        for r in self.tiedlist[:]:
            if (self.update_range != 0) and \
               (r.stamp + self.update_range < now):
                self.tiedlist.remove(r)
        self.tiedlist.sync()

# End of UpdateList


class RecentList(UpdateList):
    '''Recent updated files list.

    Provide file names and tags for node manager.
    '''

    def __init__(self):
        UpdateList.__init__(self, config.recent, config.recent_range)

    def getall(self):
        """Search nodes and update my recent list."""
        searchlist = SearchList()
        lookuptable = LookupTable()
        lookuptable.clear()
        sugtagtable = SuggestedTagTable()
        if config.recent_range:
            begin = int(time()) - config.recent_range
        else:
            begin = 0
        count = 0
        for node in searchlist:
            tag_update = False
            res = node.talk("/recent/%d-" % begin)
            for line in res:
                r = self.make_record(line)
                if r is not None:
                    self.append(r)
                    cache = Cache(r.datfile, sugtagtable=sugtagtable)
                    tags = r.get('tag', '').strip().split()
                    random.shuffle(tags)
                    del tags[config.tag_size:]
                    if tags:
                        cache.sugtags.add(tags)
                        cache.sugtags.sync()
                        lookuptable.add(r.datfile, node)
            count += 1
            if count > config.search_depth:
                break
        self.sync()
        lookuptable.sync()
        sugtagtable.prune(self)
        sugtagtable.sync()

    def uniq(self):
        '''Save one line par one file.'''
        date = {}
        for r in self[:]:
            if r.datfile not in date:
                date[r.datfile] = r
            elif date[r.datfile] < r:
                self.remove(date[r.datfile])
                date[r.datfile] = r
            else:
                self.remove(r)

    def sync(self):
        '''Save list.'''
        self.uniq()
        UpdateList.sync(self)

# End of RecentList


def _test(*args, **kwargs):
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test()
