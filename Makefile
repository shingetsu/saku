#
# Makefile
# Copyright (C) 2005-2012 shinGETsu Project.
#

PREFIX = /usr/local
PACKAGE_DIR = ..
PACKAGE = saku-git$(shell cat file/version.txt)

.PHONY: all install exe version check clean distclean package

all:
	python setup.py build

install:
	python setup.py install --prefix=$(PREFIX)

exe:
	python setup-win.py py2exe

version:
	env LANG=C git log -n 1| ./tool/git2ver.sh > file/version.txt

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

package: distclean version
	-rm -Rf $(PACKAGE_DIR)/$(PACKAGE).tar.gz $(PACKAGE_DIR)/$(PACKAGE)
	rsync -Ca . $(PACKAGE_DIR)/$(PACKAGE)
	-rm -Rf $(PACKAGE_DIR)/$(PACKAGE)/.git*
	tar -zcf $(PACKAGE_DIR)/$(PACKAGE).tar.gz -C $(PACKAGE_DIR) $(PACKAGE)
	-rm -Rf $(PACKAGE_DIR)/$(PACKAGE)
