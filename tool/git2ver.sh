#!/bin/sh
# git log format to version string
#
awk '/^Date:/ { print $2 " " $3 " " $4 " " $5  " " $7 " " $6}' |
xargs -0 date +'%Y%m%d-%H%M' --date
