#
# Makefile
# Copyright (C) 2005-2014 shinGETsu Project.
#

PREFIX = /usr/local
PACKAGE_DIR = ..
PACKAGE = saku-$(shell cat file/version.txt)

.PHONY: all install exe version check clean distclean package

all:
	python3 setup.py build

install:
	python3 setup.py install --prefix=$(PREFIX)

version:
	./tool/git2ver.sh > file/version.txt

check:
	sh tests/runtests.sh

clean:
	rm -f saku
	rm -f www/__merged.css www/__merged.js
	rm -Rf build dist root
	rm -Rf cache log run
	find . -name "*.py[co]" \! -path ".git/*" -print0 | xargs -0 -r rm -f

distclean: clean
	find . \( -name "*~" -o -name "#*" -o -name ".#*" \) \! -path ".git/*" \
	    -print0 | \
	    xargs -0 -r rm -fv

package: distclean version
	-rm -Rf $(PACKAGE_DIR)/$(PACKAGE).tar.gz $(PACKAGE_DIR)/$(PACKAGE)
	cp -a . $(PACKAGE_DIR)/$(PACKAGE)
	-rm -Rf $(PACKAGE_DIR)/$(PACKAGE)/.git*
	tar -zcf $(PACKAGE_DIR)/$(PACKAGE).tar.gz -C $(PACKAGE_DIR) $(PACKAGE)
	-rm -Rf $(PACKAGE_DIR)/$(PACKAGE)
