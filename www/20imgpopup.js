/* Popup Image Preview.
 * Copyright (C) 2005,2006 shinGETsu Project.
 * $Id$
 */

initFunc[initFunc.length] = function () {
    function showPopupImage(coordinate, image, count) {
        if (count > 100) {
            return;
        } else if (image.complete) {
            image.width = image.width / image.height * 100;
            image.height = 100;
            var p = document.createElement('p');
            p.appendChild(image);
            showPopup(coordinate, [p]);
        } else {
            setTimeout(function(){
                        showPopupImage(coordinate, image, count+1);
                       }, 100);
        }
    }

    function popupImage(e, imguri) {
        var coordinate = new Coordinate(e);
        image = new Image();
        image.src = imguri;
        showPopupImage(coordinate, image, 0);
    }

    var anc = document.getElementsByTagName('a');
    for (var i=0; i<anc.length; i++) {
        if (anc[i].pathname.search(/[.](jpg|jpeg|gif|png|bmp)$/i) > 0) {
            if (anc[i].addEventListener) {
                anc[i].addEventListener(
                    'mouseover',
                    (function (_uri) {
                        return function (e) {popupImage(e, _uri);}
                    })(anc[i].href),
                    false);
                anc[i].addEventListener('mouseout', hidePopup, false);
            } else if (anc[i].attachEvent) {
                anc[i].attachEvent(
                    'onmouseover',
                    (function (_uri) {
                        return function () {popupImage(null, _uri);}
                    })(anc[i].href));
                anc[i].attachEvent('onmouseout', hidePopup);
            }
        }
    }
};
