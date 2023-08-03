Saku - a clone of P2P anonymous BBS shinGETsu
=============================================

Authors
-------
* (main) Satoshi Fukutomi <fuktommy@shingetsu.info>
* sbwhitecap
* (apollo) replaceable anonymous.
* (2ch interface) kkka
* (thumbnail patch) A shinGETsu user.
* (imghdr patch) A shinGETsu user.
* (js extensions) shinGETsu users.
* (markdown extension) WhiteCat6142

Contributors
------------
* (run_cgi) Python Software Foundation.
* (jQuery) The jQuery Foundation.
* (Twitter Bootstrap) Twitter.
* (jQuery Lazy) Daniel 'Eisbehr' Kern
* (Spoiler Alert) Joshua Hull, Jared Volpe, Dwayne Charrington
* (marked) Christopher Jeffrey

WebSite
-------
* https://www.shingetsu.info/

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
* We confirm that Saku works on CPython 3.4 on GNU/Linux.
    Saku may not work on MacOS(ver.9 or before).
* The features of shinGETsu are...
    * 2ch.net style interface
    * Wiki style hyperlink
    * IRC style cache
    * Uploader

Saku requires
-------------
* Python (ver.3.4.2 or later)
* pipenv if you install packages with pipenv
* Jinja2 (ver.2.7.3 or later) if you install Saku
* PIL or Pillow (Python Imaging Libraty) if you need
* Supervisor if you need

Usage Saku with Docker Compose
------------------------------

Data will be persistence with `./data` directory

1. Open port 8000/tcp.
2. Edit `docker/saku.ini`.
3. Start with

        % docker compose up

4. Browse http://localhost:8000/.
5. Stop with ^C.

Usage Saku without install
--------------------------
1. Open port 8000/tcp.
2. Edit file/saku.ini.
3. Start with

        % pipenv install
        % pipenv run python3 ./saku.py -v

4. Browse http://localhost:8000/.
5. Stop with ^C.

Usage Saku with install
-----------------------
1. Install [Jinja2](http://jinja.pocoo.org/).
2. Open port 8000/tcp.
3. Compile and install.

        # make install

   You can use PREFIX option for make, and use setup.py directly.
   If your system do not read modules in /usr/bin/local, do

        # ln -s /usr/local/lib/python3.2/site-packages/shingetsu \
                /usr/lib/python3.2/site-packages

4. Configration files are installed into /usr/local/share/doc/saku/sample.
   You shoud install them:

        # cp init.sample /usr/local/etc/init.d/saku
        # cp saku.ini /usr/local/etc/saku/saku.ini
        
   and so on.
   If you use Supervisor, install supervisor.sample instead of init.sample.
   The paths of config files are set in saku.ini,
   they are in /usr/local/etc/saku by defaults.
   saku.ini are loaded from following paths and the later settings have a priority.

        * /usr/local/etc/saku/saku.ini
        * /etc/saku/saku.ini
        * ~/.saku/saku.ini

5. Setup user and directories refering config files.
6. Start with

        # /usr/local/etc/init.d/saku start

7. Browse http://localhost:8000/.
8. Stop with

        # /usr/local/etc/init.d/saku stop

9. Run /usr/local/bin/saku for user application.

How to Insatall Required Packages on Debian GNU/Linux 8.3
---------------------------------------------------------
1. do

        $ sudo aptitude install python3 python3-jinja2 python3-pil

Acknowledge
-----------
* The design is made referring to Vojta and Winny.
* I learned how to handle file name from [YukiWiki](http://www.hyuki.com/yukiwiki/)
  written by Hiroshi Yuki.
* Module apollo.py is was made referring to apollo.c
  written by replaceable anonymous.
* Popup JavaScript was made referring to [Kindan-no Tubo](http://tubo.80.kg/) by Zero corp.
* XLST was made reffring to [Landscape](http://sonic64.com/2005-03-16.html).
