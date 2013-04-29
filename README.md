Saku - a clone of P2P anonymous BBS shinGETsu
=============================================

Authors
-------
* (main) Satoshi Fukutomi <fuktommy@shingetsu.info>
* sbwhitecap
* (apollo) replaceable anonymous.
* (compatible) A shinGETsu user.
* (thumbnail patch) A shinGETsu user.
* (imghdr patch) A shinGETsu user.
* (moonlight) A shinGETsu user.
* (js extensions) shinGETsu users.

Contributers
------------
* (run_cgi) Python Software Foundation.
* (SimpleGzipFile) Python Software Foundation.
* (popup.js) Zero corp.
* (Cheetah) The Cheetah Development Team:
  Tavis Rudd, Mike Orr, Ian Bicking, Chuck Esterbrook.
* (jQuery) The jQuery Foundation.
* (Twitter Bootstrap) Twitter.
* (HTML5 Shiv) @afarkas @jdalton @jon_neal @rem
* (Spoiler Alert) Joshua Hull, Jared Volpe, Dwayne Charrington

WebSite
-------
* http://www.shingetsu.info/

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
* We confirm that Saku works on CPython 2.6 on GNU/Linux and
    CPython 2.7 on Windows 7.
    Saku may not work on MacOS(ver.9 or before).
* The features of shinGETsu are...
    * 2ch.net style interface
    * Wiki style hyperlink
    * IRC style cache
    * Uploader

Saku requires
-------------
* Python (ver.2.4 or later)
* Cheetah (ver.2.0rc7 or later) if you install Saku
* PIL (Python Imaging Libraty) if you need
* MiniUPnPc if you need

Usage Saku without install
--------------------------
1. Open port 8000/tcp.
2. Edit file/saku.ini.
3. Start with
        % python ./saku.py -v
4. Browse http://localhost:8000/.
5. Stop with ^C.

Usage Saku with install
-----------------------
1. Install [Cheetah](http://www.cheetahtemplate.org/).
2. Open port 8000/tcp.
3. Compile and install.

        # make install
   You can use PREFIX option for make, and use setup.py directly.
   If your system do not read modules in /usr/bin/local, do

        # ln -s /usr/local/lib/python2.5/site-packages/shingetsu \
                /usr/lib/python2.5/site-packages

4. Configration files are installed into /usr/local/share/doc/saku/sample.
   You shoud install them:

        # cp saku.init /usr/local/etc/init.d/saku
        # cp sample.ini /usr/local/etc/saku/saku.ini
        
   and so on.
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

Acknowledge
-----------
* The design is made referring to Vojta and Winny.
* I learned how to handle file name from [YukiWiki](http://www.hyuki.com/yukiwiki/)
  written by Hiroshi Yuki.
* Module apollo.py is was made referring to apollo.c
  written by replaceable anonymous.
* Popup JavaScript was made referring to [Kindan-no Tubo](http://tubo.80.kg/) by Zero corp.
* XLST was made reffring to [Landscape](http://sonic64.com/2005-03-16.html).
