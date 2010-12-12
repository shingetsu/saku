/* Popup Res Anchor.
 * Copyright (C) 2005-2010 shinGETsu Project.
 * $Id$
 */

shingetsu.plugins.popupAnchor = function (e, aid) {
    var dt = document.getElementById("r" + aid);
    var dd = document.getElementById("b" + aid);
    if (! (dt && dd)) {
        return
    }
    dt = dt.innerHTML;
    var re = new RegExp("</?(input|a)[^<>]*>", "ig");
    dt = dt.replace(re, "");

    dd = dd.innerHTML;
    re = new RegExp("(<br[^<>]*>\\s*)*$", "i");
    dd = dd.replace(re, "");

    var coordinate = new shingetsu.plugins.Coordinate(e);
    var dl = document.createElement('dl');
    dl.innerHTML = '<dt>'+dt+'</dt><dd>'+dd+'</dd>';
    shingetsu.plugins.showPopup(coordinate, [dl]);
}

shingetsu.addInitializer(function () {
    function jump(aid) {
        location.hash = '#r' + aid;
        return false;
    }

    var popupAnchor = shingetsu.plugins.popupAnchor;
    var hidePopup = shingetsu.plugins.hidePopup;

    var anc = document.getElementsByTagName('a');
    for (var i=0; i<anc.length; i++) {
        if ((anc[i].className == 'innerlink') &&
            (anc[i].href.search(/([0-9a-f]{8})/) > 0)) {
            var id = RegExp.$1;
            if (anc[i].addEventListener) {
                anc[i].addEventListener(
                    'mouseover',
                    (function (_id) {
                        return function (event) {popupAnchor(event, _id);}
                    })(id),
                    false);
                anc[i].addEventListener('mouseout', hidePopup, false);
            } else if (anc[i].attachEvent) {
                anc[i].attachEvent(
                    'onmouseover',
                    (function (_id) {
                        return function () {popupAnchor(null, _id);}
                    })(id));
                anc[i].attachEvent('onmouseout', hidePopup);
            }
            if (document.getElementById('r' + id)) {
                anc[i].onclick =
                    (function (_id) {
                        return function () {jump(_id); return false; }
                    })(id);
            }
        }
    }
});
