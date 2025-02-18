朔 - P2P匿名掲示板「新月」のクローン
====================================

Authors
-------
* (main) Satoshi Fukutomi <fuktommy@shingetsu.info>
* sbwhitecap
* (apollo) replaceable anonymous.
* (2ch interface) kkka
* (thumbnail patch) A shinGETsu user.
* (imghdr patch) A shinGETsu user.
* (js extensions) shinGETsu users.
* (Pipfile, Dockefile, GitHub Actions) takano32

Contributers
------------
* (run_cgi) Python Software Foundation.
* (jQuery) The jQuery Foundation.
* (Twitter Bootstrap) Twitter.
* (jQuery Lazy) Daniel 'Eisbehr' Kern
* (Spoiler Alert) Joshua Hull, Jared Volpe, Dwayne Charrington

WebSite
-------
  https://shingetsu.info/

Sakuは Shingetsu Another Keen Utility の略です。
また、朔は新月を意味するやや古い表現です。

ネットワークの利用条件は motd.txt ファイルをご覧ください。

概要
----
* HTTPのGETメソッドのみを用いて記事を配信する
  peer to peer 電子掲示板システムです。
* 朔は Python 上で動きます。
  動作確認は主に GNU/Linux 上の CPython 3.2 で行っています。
    MacOS(9以前)では動かないと思います。
* 次のような特徴を備えた掲示板が利用できます。
    * 2ちゃんねる型掲示板のインタフェース
    * Wikiを参考にしたハイパーリンク
    * IRCを参考にしたキャッシュ
    * アップローダ

朔に必要なプログラム
--------------------
* Python (ver.3.9以降)
* pipenv パッケージをpipenvでインストールする場合
* Jinja2 (ver.3 以降)
* PIL または Pillow (Python Imaging Library) もし必要なら
* Supervisor もし必要なら

朔の使い方
----------
1. Python3.9以降をインストールする
2. モデム、ルータまたはファイアウォールを設定して8000/tcpをポート開放する。
   * 環境次第なのでここでは説明しきれません
   * IPv6対応環境では最初からポート開放されている場合があるようです
   * IPv4, IPv6 の少なくとも片方に外部から繋がるようにしてください
3. ライブラリをインストールする
    * 例: pipenvを使う場合

        pip install pipenv
        pipenv install

    * 例: Debianのパッケージを使う場合 (pilはサムネイル画像生成用で必須ではありません)

        apt install python3-jinja2 python3-pil

    * 例: Dockerを利用する場合は作業不要
4. 朔をシステムにインストールする(そうしたい人のみ)
    * 例: /usr/local にインストールする場合

        make install

    * 例: インストール先を指定する場合

        make install PREFIX=/path/to/insall/dir
5. 朔をシステムにインストールした場合は設定ファイルを配置する
    * 設定ファイルの雛型は /usr/local/share/doc/saku/sample にインストールされています
    * saku.ini は /usr/local/etc/saku/saku.ini, /etc/saku/saku.ini, ~/.saku/saku.ini の順に読み込まれ、後のものが優先されます
    * それ以外の設定ファイル(初期ノード一覧等)は saku.ini 内で指定します
    * 自動起動するときは shingetsu ユーザーを作成してください(起動スクリプトのデフォルトがこの名前です)。また設定ファイルをみて cache, log, run の3つのフォルダに書き込み権限をつけてください
    * 例: SysV Init 互換形式の方法で起動したい場合は saku.init を /etc/init.d/saku にコピーして自動起動するように設定する(ディストリビューションごとに異なっていた記憶)
    * 例: Systemdで起動したい場合は saku.service.sample を /etc/systemd/system/saku.service にコピーして systemctl daemon-reload を実行
    * 例: Supervisorで起動したい場合は supervisor.sample を /etc/supervisor/conf.d/saku.conf にコピーして systemctl reload supervisor を実行
6. 朔を起動する
    * 例: pipenvを使う場合

        pipenv run python3 saku.py -v

    * 例: Dockerを使う場合

        docker compose up

    * 例: システムにインストールしており直に実行したい場合

        /usr/local/bin/saku -v

    * 例: Sysv Init 形式の場合

        /etc/init.d/saku start

    * そのほか自動起動の設定(Supervisorなど)をしていれば自動で起動するでしょうし、停止や再起動の手順はそのシステムの方式に従ってください
7. http://localhost:8000/をブラウザで表示

2ch専用ブラウザから使う場合
---------------------------
1. file/saku.iniに

       [Gateway]
       enable_2ch: yes

   を追加してください。
2. sakuを起動してください。
3. http://localhost:8001/2ch/subject.txt を外部板として登録してください。
4. おたのしみください。

[2chインターフェイスについて詳細](./2ch-interface.README.md)

謝辞
----
* 設計についてVojtaとWinnyを参考にしました。
* ファイル名の扱いについてはHiroshi Yuki氏の[YukiWiki](https://www.hyuki.com/yukiwiki/)を参考にしました。
* 署名モジュール apollo.py は replaceable anonymous 氏のC言語版Apolloを基にしました。
* ポップアップのためのJavaScriptは  Zero corp. の[禁断の壷](http://tubo.80.kg/)を参考にしました。
* XLSTは[Landscape](https://sonic64.com/2005-03-16.html)を参考にしました。
