"""git log format to version file
"""
#
# Copyright (c) 2012 shinGETsu Project.
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
import datetime
import os
import subprocess
import sys

def main():
    version_file = 'file/version.txt'
    os.chdir(os.path.dirname(__file__) + '/..')
    if os.path.exists(version_file):
        os.remove(version_file)
    if not os.path.isdir('.git'):
        print('not a git repository')
        return

    ret = subprocess.run(['git', 'log', '-n', '1', '--pretty=format:%aI'],
                         stdout=subprocess.PIPE, encoding='utf-8')
    s = ret.stdout.strip().replace('Z', '+00:00')
    dt = datetime.datetime.fromisoformat(s)
    v = dt.astimezone(datetime.timezone.utc).strftime('%Y%m%d-%H%M')

    with open(version_file, 'w') as f:
        print(v, file=f)

if __name__ == '__main__':
    main()
