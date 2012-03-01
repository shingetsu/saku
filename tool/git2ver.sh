#!/bin/sh
# git log format to version string
#
env LANG=C git log -n 1 |
    awk '/^Date:/ { print $2 " " $3 " " $4 " " $5  " " $7 " " $6}' |
    env TZ=UTC xargs -0 date +'%Y%m%d-%H%M' --date
