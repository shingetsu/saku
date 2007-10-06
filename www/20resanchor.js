/* Popup Res Anchor.
 * Copyright (C) 2005,2006 shinGETsu Project.
 * $Id$
 */

function popupAnchor(e, aid) {
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

    var coordinate = new Coordinate(e);
    var dl = document.createElement('dl');
    dl.innerHTML = '<dt>'+dt+'</dt><dd>'+dd+'</dd>';
    showPopup(coordinate, [dl]);
}

initFunc[initFunc.length] = function () {
    function jump(aid) {
        location.hash = '#r' + aid;
        return false;
    }

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
};
