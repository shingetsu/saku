#!/usr/bin/env python3
# Copyright (C) 2005-2014 shinGETsu Project.
#

import re
import os
from stat import S_IRUSR, S_IWUSR, S_IXUSR, S_IXGRP, S_IRGRP, S_IROTH, S_IXOTH
from glob import glob
from shutil import copy, copytree
from distutils.core import setup

import shingetsu.config
from shingetsu.util import opentext

conf_dir = "root/etc/saku"
init_dir = "root/etc/init.d"
lib_dir = "root/lib/saku"
data_dir = "root/share/saku"
file_dir = "root/share/saku/file"
template_dir = "root/share/saku/template"
www_dir = "root/share/saku/www"
doc_dir = "root/share/doc/saku/"
sample_dir = "root/share/doc/saku/sample/"

mode = S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH
execmode = mode | S_IXUSR | S_IXGRP | S_IXOTH

def globcopy(src, dst):
    for i in glob(src):
        copy(i, dst)

def globcat(src, dst):
    f = opentext(dst, 'w')
    files = glob(src)
    files.sort()
    for i in files:
        f.write(opentext(i).read())
    f.close()

def setup_script_files():
    copy("saku.py", "saku")

def setup_data_files():
    for i in (lib_dir, data_dir, file_dir, template_dir,
              www_dir, doc_dir, sample_dir):
        if not os.path.isdir(i):
            os.makedirs(i)

    globcopy("file/*.txt", file_dir)
    globcopy("template/*.txt", template_dir)
    globcopy("www/*.css", www_dir)
    globcopy("www/*.ico", www_dir)
    globcopy("www/*.gif", www_dir)
    globcopy("www/*.js", www_dir)
    globcopy("www/*.xsl", www_dir)
    globcat("www/*.css", os.path.join(www_dir, '__merged.css'))
    globcat("www/*.js", os.path.join(www_dir, '__merged.js'))
    copytree("www/bootstrap", os.path.join(www_dir, 'bootstrap'))
    copytree("www/jquery", os.path.join(www_dir, 'jquery'))

    globcopy("README*", doc_dir)
    globcopy("doc/README*", doc_dir)

    globcopy("file/*node*.txt", sample_dir)
    globcopy("file/spam.txt", sample_dir)
    globcopy("doc/*.sample", sample_dir)
    copy('doc/sample.ini', os.path.join(sample_dir, 'saku.ini'))

    #copy("doc/sample.ini", os.path.join(conf_dir, "saku.ini"))
    #copy("file/spam.txt", os.path.join(conf_dir, "spam.txt"))
    #copy("file/initnode.txt", os.path.join(conf_dir, "initnode.txt"))
    #copy("doc/init.sample", os.path.join(init_dir, "saku"))
    copy("tool/mkrss.py", os.path.join(lib_dir, "mkrss"))
    copy("tool/mkarchive.py", os.path.join(lib_dir, "mkarchive"))


def make_data_files():
    data_files = []
    for r, d, f in os.walk("root"):
        data = []
        for i in f:
            i = os.path.join(r, i)
            os.chmod(i, mode)
            data.append(i)
        data_files.append((r[len("root")+1:], data))
    #os.chmod(os.path.join(init_dir, "saku"), execmode)
    os.chmod(os.path.join(lib_dir, "mkrss"), execmode)
    os.chmod(os.path.join(lib_dir, "mkarchive"), execmode)

    return data_files

def make_version():
    found = re.search(r"\(.*/(.+)\)", shingetsu.config.version)
    if found:
        version = found.group(1)
    else:
        version = shingetsu.config.version
    return version

setup_script_files()
setup_data_files()
data_files = make_data_files()
version = make_version()

setup(name = "saku",
      version = version,
      description = "a clone of P2P anonymous BBS shinGETsu",
      author = "Fuktommy",
      maintainer = "Fuktommy",
      maintainer_email = "fuktommy@shingetsu.info",
      url = "http://www.shingetsu.info/",
      license = '2-clause BSD license',
      platforms = 'any',
      long_description =
            'A clone of P2P anonymous BBS shinGETsu written by Python.'
            ' This includes libraries, daemon, and Apache config files.',
      scripts = ['saku'],
      packages = ['shingetsu', 'shingetsu.mch'],
      data_files = data_files)
