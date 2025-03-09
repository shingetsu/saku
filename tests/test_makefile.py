"""Test Makefile.
"""
#
# Copyright (c) 2025 shinGETsu Project.
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

import os
import shutil
import subprocess
import unittest

import shingetsu.config as config


class MakefileTest(unittest.TestCase):
    def setUp(self):
        self.clean_tmp_dir()
        os.makedirs(self.get_tmp_dir())

    def tearDown(self):
        self.clean_tmp_dir()

    @classmethod
    def clean_tmp_dir(cls):
        d = cls.get_tmp_dir()
        if os.path.exists(d):
            shutil.rmtree(d)

    @classmethod
    def get_tmp_dir(cls):
        return os.path.abspath(os.path.dirname(__file__) + '/../run/test')

    def test_make_install_with_git_dir(self):
        if not os.path.isdir(os.path.dirname(__file__) + '/../.git'):
            self.skipTest('not a git repository')
        src = self.get_tmp_dir() + '/src'
        dest = self.get_tmp_dir() + '/dest'
        ignore = shutil.ignore_patterns('cache', 'log', 'run', 'version.txt')
        shutil.copytree('.', src, ignore=ignore)
        subprocess.run(['make'], cwd=src, stdout=subprocess.PIPE)
        subprocess.run(['make', 'install', 'PREFIX='+dest], cwd=src,
                       stdout=subprocess.PIPE)
        self.assertTrue(os.path.isfile(dest + '/share/saku/file/initnode.txt'))
        self.assertTrue(os.path.isfile(dest + '/share/saku/file/version.txt'))

        subprocess.run(['make', 'uninstall', 'PREFIX='+dest], cwd=src,
                       stdout=subprocess.PIPE)
        for dirpath, _, filenames in os.walk(dest):
            if filenames:
                self.fail('directory is not empty: %s' % dirpath)

    def test_make_install_without_git_dir(self):
        src = self.get_tmp_dir() + '/src'
        dest = self.get_tmp_dir() + '/dest'
        ignore = shutil.ignore_patterns('.git', 'cache', 'log', 'run')
        shutil.copytree('.', src, ignore=ignore)
        with open(src + '/file/version.txt', 'w') as f:
            print('dummy', file=f)
        subprocess.run(['make'], cwd=src, stdout=subprocess.PIPE)
        subprocess.run(['make', 'install', 'PREFIX='+dest], cwd=src,
                       stdout=subprocess.PIPE)
        self.assertTrue(os.path.isfile(dest + '/share/saku/file/initnode.txt'))
        self.assertFalse(os.path.isfile(dest + '/share/saku/file/version.txt'))

        subprocess.run(['make', 'uninstall', 'PREFIX='+dest], cwd=src,
                       stdout=subprocess.PIPE)
        for dirpath, _, filenames in os.walk(dest):
            if filenames:
                self.fail('directory is not empty: %s' % dirpath)

    def test_make_package(self):
        tmp = self.get_tmp_dir()
        src = self.get_tmp_dir() + '/src'
        ignore = shutil.ignore_patterns('.git', 'cache', 'log', 'run')
        shutil.copytree('.', src, ignore=ignore)
        with open(src + '/file/version.txt', 'w') as f:
            print('dummy', file=f)
        subprocess.run(['make', 'package'], cwd=src, stdout=subprocess.PIPE)
        pkg = 'saku-' + config.saku_version
        subprocess.run(['tar', 'xf', pkg+'.tar.gz'], cwd=tmp, stdout=subprocess.PIPE)
        self.assertTrue(os.path.isfile(os.path.join(tmp, pkg, 'file/initnode.txt')))
        self.assertFalse(os.path.isfile(os.path.join(tmp, pkg, 'file/version.txt')))
