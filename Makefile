#
# Makefile
# Copyright (C) 2005 shinGETsu Project.
#

PREFIX = /usr/local

packdir = ..
package = saku-$(shell python3 -c 'import shingetsu.config; \
    print(shingetsu.config.saku_version)')

.PHONY: all install uninstall version check clean distclean package

all: version

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
	install -m 644 -D -t $(PREFIX)/share/doc/saku README* LICENSE doc/AUTHORS*
	install -m 644 -D -t $(PREFIX)/share/doc/saku doc/README* doc/changelog*
	install -m 644 -D -t $(PREFIX)/share/doc/saku/contrib doc/contrib/*
	install -m 644 -D -t $(PREFIX)/share/doc/saku/readme doc/readme/*
	install -m 644 -D -t $(PREFIX)/share/doc/saku/sample doc/sample/*

	install -m 755 -d $(PREFIX)/bin
	install -m 755 -T tool/saku.sh $(PREFIX)/bin/saku
	install -m 755 -T saku.py $(PREFIX)/lib/saku/saku
	install -m 755 -T tool/mkrss.py $(PREFIX)/lib/saku/mkrss
	install -m 755 -T tool/mkarchive.py $(PREFIX)/lib/saku/mkarchive

	rm -f $(PREFIX)/share/saku/www/__merged.css
	rm -f $(PREFIX)/share/saku/www/__merged.js
	cat www/*.css > $(PREFIX)/share/saku/www/__merged.css
	cat www/*.js > $(PREFIX)/share/saku/www/__merged.js

uninstall:
	rm -Rf $(PREFIX)/bin/saku
	rm -Rf $(PREFIX)/lib/saku
	rm -Rf $(PREFIX)/share/saku
	rm -Rf $(PREFIX)/share/doc/saku

version:
	python3 tool/git2ver.py
	@test -f file/version.txt && cat file/version.txt || true

check:
	python3 -B -m unittest -v tests/test_*.py

clean:
	rm -f www/__merged.css www/__merged.js
	rm -Rf cache log run
	rm -Rf data
	find . -name "*.py[co]" \! -path ".git/*" -print0 | xargs -0 -r rm -f
	-find . -type d -name "__pycache__" -print0 | xargs -0 -r rmdir

distclean: clean
	rm -f Pipfile.lock
	rm -f file/version.txt
	find . \( -name "*~" -o -name "#*" -o -name ".#*" \) \! -path ".git/*" \
	    -print0 | \
	    xargs -0 -r rm -fv

package: distclean
	rm -f $(packdir)/$(package).tar.gz
	rm -Rf $(packdir)/$(package)
	rsync -a --exclude=".git*" . $(packdir)/$(package)
	tar -zcf $(packdir)/$(package).tar.gz -C $(packdir) $(package)
	rm -Rf $(packdir)/$(package)
