#!/bin/sh
# git log format to version string
#
git log -n 1 --pretty=format:"%ai" |
    env TZ=UTC xargs -0 date +'%Y%m%d-%H%M' --date
