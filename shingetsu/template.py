'''Saku Template Wrapper.
'''
#
# Copyright (c) 2007,2014 shinGETsu Project.
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

import os.path
import sys

import jinja2

import config

__all__ = ['Template']


class CachedTemplate(jinja2.BytecodeCache):
    def __init__(self):
        self.template = {}

    def load_bytecode(self, bucket):
        if bucket.key in self.template:
            bucket.bytecode_from_string(self.template[bucket.key])

    def dump_bytecode(self, bucket):
        self.template[bucket.key] = bucket.bytecode_to_string()

# End of CachedTemplate


class Template:
    def __init__(self):
        self.defaults = {}
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(config.template_dir),
            bytecode_cache=CachedTemplate()
        )

    def __getitem__(self, filename):
        basename = filename + config.template_suffix
        path = os.path.join(config.template_dir, basename)
        if not os.path.isfile(path):
            sys.stderr.write('%s: file not exists.\n' % path)
            return None
        return self.env.get_template(basename)

    def set_defaults(self, nameSpace):
        self.defaults.update(nameSpace)

    def display(self, file, searchList=None):
        tmpl = self[file]
        if searchList is None:
            sl = self.defaults
        elif not isinstance(searchList, list):
            sl = self.defaults.copy()
            sl.update(searchList)
        else:
            sl = self.defaults.copy()
            for eachsl in searchList:
                sl.update(eachsl)

        if tmpl is not None:
            return tmpl.render(sl)
        else:
            return ''

# End of Template
