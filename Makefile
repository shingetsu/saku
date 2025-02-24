#
# Makefile
# Copyright (C) 2005 shinGETsu Project.
#

PREFIX = /usr/local
PACKAGE_DIR = ..
PACKAGE = saku-$(shell cat file/version.txt)

.PHONY: all install exe version check clean distclean package

all:

install:
	install -m 644 -D -t $(PREFIX)/lib/saku/shingetsu shingetsu/*.py
	install -m 644 -D -t $(PREFIX)/lib/saku/shingetsu/mch shingetsu/mch/*.py
	install -m 644 -D -t $(PREFIX)/share/saku/file file/*.txt
	install -m 644 -D -t $(PREFIX)/share/saku/template template/*.txt
	install -m 644 -D -t $(PREFIX)/share/saku/www www/*.css www/*.js
	install -m 644 -D -t $(PREFIX)/share/saku/www www/*.ico www/*.png www/*.xsl
	install -m 644 -D -t $(PREFIX)/share/saku/www/bootstrap/css www/bootstrap/css/*
	install -m 644 -D -t $(PREFIX)/share/saku/www/bootstrap/fonts www/bootstrap/fonts/*
	install -m 644 -D -t $(PREFIX)/share/saku/www/bootstrap/js www/bootstrap/js/*
	install -m 644 -D -t $(PREFIX)/share/saku/www/contrib www/contrib/*
	install -m 644 -D -t $(PREFIX)/share/saku/www/jquery www/jquery/*.js
	install -m 644 -D -t $(PREFIX)/share/saku/www/jquery/spoiler www/jquery/spoiler/*
	install -m 644 -D -t $(PREFIX)/share/doc/saku README*
	install -m 644 -D -t $(PREFIX)/share/doc/saku doc/README*
	install -m 644 -D -t $(PREFIX)/share/doc/saku/sample file/*node*.txt
	install -m 644 -D -t $(PREFIX)/share/doc/saku/sample file/spam.txt
	install -m 644 -D -t $(PREFIX)/share/doc/saku/sample doc/*.sample

	install -m 755 -d $(PREFIX)/bin
	install -m 755 -T doc/saku.sh $(PREFIX)/bin/saku
	install -m 755 -T saku.py $(PREFIX)/lib/saku/saku
	install -m 755 -T tool/mkrss.py $(PREFIX)/lib/saku/mkrss
	install -m 755 -T tool/mkarchive.py $(PREFIX)/lib/saku/mkarchive
	install -m 644 -T doc/sample.ini $(PREFIX)/share/doc/saku/sample/saku.ini

	rm -f $(PREFIX)/share/saku/www/__merged.css
	rm -f $(PREFIX)/share/saku/www/__merged.js
	cat www/*.css > $(PREFIX)/share/saku/www/__merged.css
	cat www/*.js > $(PREFIX)/share/saku/www/__merged.js

version:
	./tool/git2ver.sh > file/version.txt
	@cat file/version.txt

check:
	sh tests/runtests.sh

clean:
	rm -f saku
	rm -f www/__merged.css www/__merged.js
	rm -Rf build dist root
	rm -Rf cache log run
	find . -name "*.py[co]" \! -path ".git/*" -print0 | xargs -0 -r rm -f
	-find . -type d -name "__pycache__" -print0 | xargs -0 -r rmdir

distclean: clean
	rm -f Pipfile.lock
	find . \( -name "*~" -o -name "#*" -o -name ".#*" \) \! -path ".git/*" \
	    -print0 | \
	    xargs -0 -r rm -fv

package: distclean version
	-rm -Rf $(PACKAGE_DIR)/$(PACKAGE).tar.gz $(PACKAGE_DIR)/$(PACKAGE)
	rsync -a --exclude=".git*" . $(PACKAGE_DIR)/$(PACKAGE)
	tar -zcf $(PACKAGE_DIR)/$(PACKAGE).tar.gz -C $(PACKAGE_DIR) $(PACKAGE)
	-rm -Rf $(PACKAGE_DIR)/$(PACKAGE)
