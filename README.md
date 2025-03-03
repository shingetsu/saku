[![Lint and Test](https://github.com/shingetsu/saku/actions/workflows/workflow.yml/badge.svg)](https://github.com/shingetsu/saku/actions/workflows/workflow.yml)
[![License](https://img.shields.io/badge/License-BSD_2--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)

Saku - a clone of P2P anonymous BBS shinGETsu
=============================================

WebSite
-------
* https://shingetsu.info/

Saku stands for "Shingetsu Another Keen Utility".
Both the word "saku" and "shingetsu" mean the new moon in Japanese.

Agreement
---------
Agree following terms and join shinGETsu network.

* Descrive your license in your articles.
  Or they are open, public and/or free:
  anyone can use, modify and/or distribute them.
* Do not use the network for illegality.
* Do not use the network at the cost of othor peolpe.

Description
-----------
* Saku is a P2P anonymous BBS works on Python.
* We confirm that Saku works on CPython 3.11 on GNU/Linux.
* The features of shinGETsu are...
    * 2ch.net style interface
    * Wiki style hyperlink
    * IRC style cache
    * Uploader

Saku requires
-------------
* Python (ver.3.9 or later)
* pipenv if you install packages with pipenv
* Jinja2 (ver.3.1 or later)
* PIL or Pillow (Python Imaging Libraty) if you need
* Supervisor if you need

Usage Saku
----------
1. Install Python3.9 or lator.
2. Open port 8000/tcp.
    * IPv4 or IPv6 are needed to open.
    * Docker needs IPv4 or settings for IPv6.
3. Install libraries.
    * When use pipenv

        pip install pipenv
        pipenv install

    * When use Debian packages (pil is not required, to generate thumbnails)

        apt install python3-jinja2 python3-pil

    * When use Docker, do nothing.
4. When install saku to system
    * When install to /usr/local

        make
        sudo make install

    * when install to other place

        make
        make install PREFIX=/path/to/insall/dir

5. Set up config files when install saku to system.
    * Sample files are in /usr/local/share/doc/saku/sample.
    * saku.ini are loaded from following paths and the later settings have a priority.
        * /usr/local/etc/saku/saku.ini
        * /etc/saku/saku.ini
        * ~/.saku/saku.ini
    * Other config file paths are in saku.ini.
    * Create `shingetsu` user for auto start.
    * Allow write access for cache, log and run directories in saku.ini.
    * When use SysV Init, copy saku.init to /etc/init.d/saku.
    * When use Systemd, copy saku.service.sample to /etc/systemd/system/saku.service and run `systemctl daemon-reload`.
    * When use Supervisor, copy supervisor.sample to /etc/supervisor/conf.d/saku.conf and run `systemctl reload supervisor`.
6. Start saku
    * When use pipenv

        pipenv run python3 saku.py -v

    * When use Docker

        docker compose up

    * When install to system and need to run it directly

        /usr/local/bin/saku -v

    * When use Sysv Init

        /etc/init.d/saku start

    * When use Supervisor or any auto start, it starts automatically.
7. Open http://localhost:8000/

Acknowledge
-----------
* The design is made referring to Vojta and Winny.
* I learned how to handle file name from [YukiWiki](https://www.hyuki.com/yukiwiki/)
  written by Hiroshi Yuki.
* Module apollo.py is was made referring to apollo.c
  written by replaceable anonymous.
* Popup JavaScript was made referring to [Kindan-no Tubo](http://tubo.80.kg/) by Zero corp.
* XLST was made reffring to [Landscape](https://sonic64.com/2005-03-16.html).
