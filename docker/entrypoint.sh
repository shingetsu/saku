#!/bin/bash
set -eux
chown saku:saku /saku-data
su saku -c "pipenv run python ./saku.py -v"
