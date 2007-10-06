'''Saku Template Wrapper.
'''
#
# Copyright (c) 2007 shinGETsu Project.
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

import os.path
import sys

import Cheetah.Template

import config

__version__ = "$Revision$"
__all__ = ['Template']

class CachedTemplate:
    '''Cached Template

    cached[path] = Cheetah.Template.Template.compile(path)
    '''
    def __init__(self, directory):
        self.directory = directory
        self.template = {}
        self.mtime = {}

# End of CachedTemplate

cached = CachedTemplate(config.template_dir)


class Template:
    '''Wrapper for Cheetah.Template.Template.
    '''
    def __init__(self):
        self.defaults = {}
        self.loaded = {}

    def __getitem__(self, filename):
        path = os.path.join(cached.directory, filename+config.template_suffix)
        if os.path.isfile(path):
            mtime = os.path.getmtime(path)
            if (path not in cached.template) or \
               ((path not in self.loaded) and
                (cached.mtime.get(path, 0) < mtime)):
                cached.mtime[path] = mtime
                cached.template[path] = \
                    Cheetah.Template.Template.compile(file=path)
                self.loaded[path] = True
            return cached.template[path]
        else:
            sys.stderr.write('%s: file not exists.\n' % path)
            return None

    def set_defaults(self, nameSpace):
        self.defaults.update(nameSpace)

    def display(self, file, searchList=None):
        tmpl = self[file]
        if searchList is None:
            sl = [self.defaults]
        elif not isinstance(searchList, list):
            sl = [searchList, self.defaults]
        else:
            sl = searchList+[self.defaults]

        if tmpl is not None:
            return str(tmpl(searchList=sl))
        else:
            return ''

#End of Template
