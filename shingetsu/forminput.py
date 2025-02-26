"""FieldStrage for CGI.
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

import re
import email
import urllib.parse

__all__ = ['File', 'Form', 'read']

class Form:
    def __init__(self):
        self.fields = {}
        self.files = {}
        self.is_error = False

    def getfirst(self, name, default=None):
        if name in self.fields and self.fields[name]:
            return self.fields[name][0]
        else:
            return default

    def getlist(self, name):
        if name in self.fields:
            return self.fields[name]
        else:
            return []

    def getfile(self, name):
        if name in self.files:
            return self.files[name]
        else:
            return None

class File:
    def __init__(self, filename, value):
        self.filename = filename
        self.value = value

def read(env, input, encoding='utf-8'):
    form = Form()
    read_get(form, env, encoding)
    if env['REQUEST_METHOD'] != 'POST':
        return form

    m = re.search(r'''multipart/form-data; boundary=["']?([^\s"';]+)''', env['CONTENT_TYPE'])
    if m:
        read_multipart(form, env, input, m.group(1), encoding)
    else:
        read_post(form, env, input, encoding)
    return form

def read_get(form, env, encoding):
    read_from_qsl(form, env.get('QUERY_STRING', ''), encoding)

def read_post(form, env, input, encoding):
    form_data = input.read(int(env['CONTENT_LENGTH']))
    read_from_qsl(form, form_data, encoding)

def read_from_qsl(form, data, encoding):
    if hasattr(urllib.parse, '_encode_result'):
        orig = urllib.parse._encode_result
        def tmp(obj, encoding=encoding, errors='strict'):
            return obj.encode(encoding, errors)
        urllib.parse._encode_result = tmp
    try:
        qs = urllib.parse.parse_qsl(data, encoding=encoding)
    except:
        form.is_error = True
        return form
    finally:
        if orig:
            urllib.parse._encode_result = orig

    for name, value in qs:
        name = decode(name, encoding)
        value = decode(value, encoding)
        if name in form.fields:
            form.fields[name].append(value)
        else:
            form.fields[name] = [value]

def read_multipart(form, env, input, boundary, encoding):
    form_data = input.read(int(env['CONTENT_LENGTH']))
    header = f'Content-Type: multipart/mixed; boundary="{boundary}"\n\n'
    msg = email.message_from_bytes(header.encode('utf-8') + form_data)
    for part in msg.walk():
        cd = 'Content-Disposition'
        if not str(part.get(cd)).startswith('form-data'):
            continue
        name = decode(part.get_param('name', header=cd), encoding)
        if name is None:
            continue
        if part.get_filename():
            file_name = part.get_filename()
            file_data = part.get_payload(decode=True)
            file_name = decode(file_name, encoding)
            form.files[name] = File(file_name, file_data)
        else:
            value = part.get_payload(decode=True)
            value = decode(value, encoding)
            if name in form.fields:
                form.fields[name].append(value)
            else:
                form.fields[name] = [value]
    return form

def decode(s, encoding):
    if isinstance(s, str):
        return s
    elif isinstance(s, bytes):
        return str(s, encoding, 'replace')
    else:
        return s
