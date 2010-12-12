/* Popup.
 * Copyright (C) 2005-2010 shinGETsu Project.
 * This is made referring to Kindan-no Tubo.
 * $Id$
 */

shingetsu.plugins.Coordinate = function (e) {
    if (e) {
        this.x = e.pageX;
        this.y = e.pageY;
    } else {
        this.x = event.clientX;
        this.y = event.clientY;
    }
}

shingetsu.plugins.hidePopup = function () {
    var pop = document.getElementById("popup");
    if (pop) {
        pop.innerHTML = "";
        pop.style.padding = 0;
        pop.visibility = "hidden";
    }
    if (document.all) {
        var select = document.getElementsByTagName('select');
        for (var i=0; i<select.length; i++) {
            select[i].style.visibility = 'visible';
        }
    }
}

shingetsu.plugins.showPopup = function (coordinate, objects) {
    var pop = document.getElementById("popup");
    if (! pop) {
        return null;
    }
    pop.innerHTML = '';
    for (var i=0; i<objects.length; i++) {
        pop.appendChild(objects[i]);
    }
    if (document.all) {
        var nWidth  = pop.clientWidth;
        var nHeight = pop.clientHeight;
        var nPosX   = coordinate.x + 20;
        var nPosY   = coordinate.y - nHeight;
        var body = (document.compatMode=='CSS1Compat') ?
                        document.documentElement :
                        document.body;
        if (window.opera) {
            nPosY = coordinate.y - body.scrollTop;
        }
        if (nPosY < 0) {
            nPosY = 0;
        }
        pop.style.left = nPosX + body.scrollLeft;
        pop.style.top = nPosY + body.scrollTop;
        var select = document.getElementsByTagName('select');
        for (var i=0; i<select.length; i++) {
            select[i].style.visibility = 'hidden';
        }
    } else {
        var nWidth  = pop.scrollWidth;
        var nHeight = pop.scrollHeight;
        var nPosX = coordinate.x + 20;
        var nPosY = coordinate.y - nHeight;
        if (document.body.scrollTop && (nPosY < document.body.scrollTop)) {
            nPosY = document.body.scrollTop;
        } else if (window.pageYOffset && (nPosY < window.pageYOffset)) {
            nPosY = window.pageYOffset;
        } else if (nPosY < 0) {
            nPosY = 0;
        }
        pop.style.left = nPosX + "px";
        pop.style.top = nPosY + "px";
    }
    pop.style.paddingLeft = "1em";
    pop.style.paddingRight = "1em";
    pop.style.visibility = "visible";
    return pop;
}

shingetsu.addInitializer(function () {
    var div = document.createElement('div');
    div.id = 'popup';
    var body = document.getElementsByTagName('body')[0];
    body.appendChild(div);
    var pop = document.getElementById("popup");
    if (pop) {
        pop.style.position = "absolute";
        pop.style.left = "0px";
        pop.style.top = "0px";
        pop.visibility = "hidden";
    }
});
