#!/bin/bash
set -eux
chown saku:saku /saku-data
su saku -c "/saku/.local/bin/pipenv run python ./saku.py -v"
