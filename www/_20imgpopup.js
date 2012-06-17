/* Popup Image Preview.
 * Copyright (C) 2005-2010 shinGETsu Project.
 * $Id$
 */

shingetsu.initialize(function () {
    function showPopupImage(coordinate, image, count) {
        if (count > 100) {
            return;
        } else if (image.complete) {
            image.width = image.width / image.height * 100;
            image.height = 100;
            var p = document.createElement('p');
            p.appendChild(image);
            shingetsu.plugins.showPopup(coordinate, [p]);
        } else {
            setTimeout(function(){
                        showPopupImage(coordinate, image, count+1);
                       }, 100);
        }
    }

    function popupImage(e, imguri) {
        var coordinate = new shingetsu.plugins.Coordinate(e);
        image = new Image();
        image.src = imguri;
        showPopupImage(coordinate, image, 0);
    }

    shingetsu.debugMode = true;
    $('a').each (function (i, anchor) {
        if (anchor.pathname.search(/[.](jpg|jpeg|gif|png|bmp)$/i) <= 0) {
            return;
        }
        var url = anchor.href;
        $(anchor).mouseover(function (e) { popupImage(e, url) })
                 .mouseout(function (e) { shingetsu.plugins.hidePopup() });
    });
});
