#!/usr/bin/python3
#
'''shinGETsu clone.
'''
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

import sys
import time
import argparse

import shingetsu.daemon as daemon


def main():
    parser = argparse.ArgumentParser()
    log_group = parser.add_mutually_exclusive_group()
    default_verbose = hasattr(sys, 'winver')
    log_group.add_argument(
        '-v', '--verbose', default=default_verbose, action='store_true',
        dest='print_log', help='print logs')
    log_group.add_argument(
        '--silent', action='store_false', dest='print_log',
        help='suppress logs')
    args = parser.parse_args()

    try:
        daemon.setup()
        if args.print_log:
            daemon.set_logger(additional=sys.stdout)
        else:
            daemon.set_logger()
        try:
            daemon.start_daemon()
            while True:
                time.sleep(60*60)
        finally:
            daemon.stop_daemon()
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    main()
