朔 - P2P匿名掲示板「新月」のクローン
====================================

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
* (Cheetah) The Cheetah Development Team:
  Tavis Rudd, Mike Orr, Ian Bicking, Chuck Esterbrook.
* (jQuery) The jQuery Foundation.
* (Twitter Bootstrap) Twitter.
* (HTML5 Shiv) @afarkas @jdalton @jon_neal @rem
* (Spoiler Alert) Joshua Hull, Jared Volpe, Dwayne Charrington

WebSite
-------
  http://www.shingetsu.info/

Sakuは Shingetsu Another Keen Utility の略です。
また、朔は新月を意味するやや古い表現です。

ネットワークの利用条件は motd.txt ファイルをご覧ください。

概要
----
* HTTPのGETメソッドのみを用いて記事を配信する
  peer to peer 電子掲示板システムです。
* 朔は Python 上で動きます。
  動作確認は主に GNU/Linux 上の CPython 2.6 と
    Windows 7 上の CPython 2.7 で行っています。
    MacOS(9以前)では動かないと思います。
* 次のような特徴を備えた掲示板が利用できます。
    * 2ちゃんねる型掲示板のインタフェース
    * Wikiを参考にしたハイパーリンク
    * IRCを参考にしたキャッシュ
    * アップローダ

朔に必要なプログラム
--------------------
* Python (ver.2.5以降)
* Cheetah (ver.2.0rc7 以降) 朔をインストールする場合
* PIL (Python Imaging Library) もし必要なら
* MiniUPnPc もし必要なら

朔をインストールせずに使う場合
------------------------------
1. ポート 8000/tcp を開けてください。
2. file/saku.ini ファイルでポート番号などを設定できます。
   詳しくは doc/sample.ini をご覧ください。
3. 次のコマンドで起動します。

        % python ./saku.py -v

4. その後 http://localhost:8000/ を表示してください。
5. 止めるときは ^C (Ctrl+C)を押下してください。

朔をインストールする場合
------------------------
1. [Cheetah](http://www.cheetahtemplate.org/) をインストールします。
2. ポート 8000/tcp が開いていることを確認します。
3. 次のコマンドを実行します。

        # make install

4. デフォルトでは /usr/local 以下にインストールされます
   PREFIXオプションでインストールする場所を変更することができます。
   setup.pyを直接利用することもできます。
   環境によっては /usr/bin/local 以下のPythonモジュールは読み込みません。
   その場合は次のようにしてリンクを張ってください。

        # ln -s /usr/local/lib/python2.5/site-packages/shingetsu \
                /usr/lib/python2.5/site-packages

5. 設定ファイルは /usr/local/share/doc/saku/sample にインストールされます。
   これを必要に応じて、次のようにインストールしてください。

        # cp saku.init /usr/local/etc/init.d/saku
        # cp sample.ini /usr/local/etc/saku/saku.ini

6. ほとんどの設定ファイルは saku.ini でパスを指定するようになっており、
   デフォルトでは /usr/local/etc/saku に配置するような設定になっています。
   saku.ini は次の順で読み込まれ、後で設定したものが優先されます。

        * /usr/local/etc/saku/saku.ini
        * /etc/saku/saku.ini
        * ~/.saku/saku.ini

7. 設定ファイルと連動するようにユーザとディレクトリを準備してください。
8. 次のコマンドで起動します。

        # /usr/local/etc/init.d/saku start

9. その後 http://localhost:8000/ を表示してください。
10. 次のコマンドで終了します。

        # /usr/local/etc/init.d/saku stop

11. /usr/local/bin/saku でも起動できます。
    この場合はユーザアプリケーションとしての動作です。

謝辞
----
* 設計についてVojtaとWinnyを参考にしました。
* ファイル名の扱いについてはHiroshi Yuki氏の[YukiWiki](http://www.hyuki.com/yukiwiki/)を参考にしました。
* 署名モジュール apollo.py は replaceable anonymous 氏のC言語版Apolloを基にしました。
* ポップアップのためのJavaScriptは  Zero corp. の[禁断の壷](http://tubo.80.kg/)を参考にしました。
* XLSTは[Landscape](http://sonic64.com/2005-03-16.html)を参考にしました。
