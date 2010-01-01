#
# Makefile
# Copyright (C) 2005-2010 shinGETsu Project.
#
# $Id$
#

PREFIX = /usr/local

all:
	python setup.py build

install:
	python setup.py install --prefix=$(PREFIX)

exe:
	python setup-win.py py2exe

check:
	sh tests/runtests.sh

clean:
	rm -f saku tksaku
	rm -Rf build dist root
	rm -Rf cache log run
	find . -name "*.py[co]" -print0 | xargs -0 rm -f

distclean: clean
	find . \( -name "*~" -o -name "#*" -o -name ".#*" \) -print0 | \
	    xargs -0 rm -f
