#!/usr/bin/env python
# Copyright (C) 2005-2007 shinGETsu Project.
#
# $Id$
#

import os
import re
import sys
from distutils.core import setup
import py2exe

import shingetsu.config

def make_version():
    found = re.search(r"\(.*/([.\d]+)\)", shingetsu.config.version)
    if found:
        version = found.group(1)
    else:
        version = '0'
    return version

class DataFiles:
    files = {}
    done = {}

    def __init__(self, root):
        self.root = root

    def tolist(self):
        buf = []
        for dirname in self.files:
            buf.append((dirname, self.files[dirname]))
        return buf

    def append(self, dirname, srcfile, dstfile=None,
               change_code=False, binary=False):
        if not dstfile:
            dstfile = os.path.basename(srcfile)
        dirpath = os.path.join(self.root, dirname)
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)
        dstpath = os.path.join(dirpath, dstfile)
        if binary:
            buf = file(srcfile, 'rb').read()
            file(dstpath, 'wb').write(buf)
        else:
            buf = file(srcfile).read()
            #if change_code:
            #    buf = unicode(buf, 'euc-jp').encode('shift-jis')
            file(dstpath, 'w').write(buf)
        if dirname in self.files:
            self.files[dirname].append(dstpath)
        else:
            self.files[dirname] = [dstpath]
        self.done[srcfile.replace('/', os.sep)] = True

    def has(self, filepath):
        filepath = filepath.replace('/', os.sep)
        return filepath in self.done

    def append_dir(self, dirname, ignore_suffix=None):
        for filename in os.listdir(dirname):
            filepath = os.path.join(dirname, filename)
            if (ignore_suffix and filename.endswith(ignore_suffix)) or \
               self.has(filepath):
                pass
            elif os.path.isfile(filepath):
                self.append(dirname, filepath, filename)

# End of DataFiles

def make_data_files():
    if not os.path.isdir('root'):
        os.makedirs('root')
    data_files = DataFiles('root')
    data_files.append('', 'LICENSE', 'LICENSE.txt')
    data_files.append('', 'README', 'README.txt')
    data_files.append('', 'README.ja', 'README.ja.txt', True)

    license = os.path.join(sys.exec_prefix, 'LICENSE.txt')
    data_files.append('file', license, 'python-license.txt')
    data_files.append('file', 'Cheetah/LICENSE', 'cheetah-license.txt')
    data_files.append('file', 'file/changelog.ja', 'changelog.ja.txt', True)
    data_files.append('file', 'file/motd.txt', change_code=True)
    data_files.append_dir('file')

    data_files.append('www', 'www/favicon.ico', binary=True)
    data_files.append_dir('template')
    data_files.append_dir('www', ignore_suffix='.cgi')
    return data_files.tolist()

version = make_version()
data_files = make_data_files()

setup(name = 'saku',
      version = version,
      description = 'a clone of P2P anonymous BBS shinGETsu',
      author = 'Fuktommy',
      maintainer = 'Fuktommy',
      maintainer_email = 'fuktommy@shingetsu.info',
      url = 'http://shingetsu.info/',
      console = [
        {'script': 'saku.py',
         'icon_resources': [(1, 'www/favicon.ico')]}],
      windows = [
        {'script' : 'tksaku.pyw',
         'icon_resources': [(1, 'www/favicon.ico')]}],
      data_files = data_files,
      options = {'py2exe': {'packages': ['shingetsu', 'Cheetah']}},
)
