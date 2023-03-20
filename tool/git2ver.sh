#!/bin/sh
# git log format to version string
#
case $(uname) in
Linux)
    git log -n 1 --pretty=format:"%ai" |
        env TZ=UTC xargs -0 date +'%Y%m%d-%H%M' --date
    ;;
Darwin|DragonFly|FreeBSD|NetBSD|OpenBSD)
    git log -n 1 --pretty=format:"%ai" |
        env TZ=UTC xargs -0 date -jf '%Y-%m-%d %H:%M:%S %z' +'%Y%m%d-%H%M'
    ;;
esac
