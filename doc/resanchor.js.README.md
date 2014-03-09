20resanchor.js 説明.md
================================================================================

レス安価の上にマウスポインタを乗せたときに、安価先のレスの内容を
ポップアップするプラグインです。

このプラグインではポップアップに関わる処理を 20popup.js に任せています。
安価に関わる処理、例えば安価のパース、安価先の読み込みなどのみを行います。

安価のパースは初期化のタイミング (shingetsu.initialize) で行います。
ページ上のすべての a 要素に対して安価かどうかの判定を行い、
安価であればイベントリスナーを登録します。

安価先のレスの内容がページ上にある場合はそれをそのまま使い、
ない場合は AJAX でページを取得し、取得し終わったら表示します。
AJAX の結果は JavaScript の変数上にキャッシュされ、2回目以降はそれが使われます。

********************************************************************************

提供する API
--------------------------------------------------------------------------------

* ```function shingetsu.plugins.popupAnchor(DOMEvent event, string resId)```

  ```event``` が持っているイベントの発生位置に、```resID``` で表される
  レスの内容をポップアップします。

  #### このメソッドを参照するファイル

  - 20response.js
  - 20textarea.js

* ```function shingetsu.plugins.tryJump(DOMEvent event, string resId)```

  ```resId``` で表されるレスがページ内にあれば、ページの移動を行わずに
  その位置へスクロールします。

依存する API
--------------------------------------------------------------------------------

### 20popup.js

* ```function shingetsu.plugins.Coordinate(DOMEvent event)```
* ```function shingetsu.plugins.showPopup(Coordinate coordinate, Elements elements)```
* ```function shingetsu.plugins.hidePopup()```
