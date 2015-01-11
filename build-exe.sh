#!/bin/bash

cxfreeze saku.py --include-path=. --target-dir=dist | tee build-exe.log
cp -r doc/ file/ template/ tool/ www/ dist/

cat >dist/file/saku.ini <<END
#
# Sample saku.ini to run saku in distributed directory.
# Copyright (c) 2005-2011 shinGETsu Project.
# $Id$
#

[Network]
port: 8000

[Gateway]
enable_2ch: yes
visitor: ^127

#admin: ^127|^192\.168
END