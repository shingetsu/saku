/* Jump New Posts.
 * Copyright (C) 2006,2010 shinGETsu Project.
 * $Id$
 */

shingetsu.addInitializer(function () {
    var lastpage = location.pathname.search(/^\/?thread.cgi\/[^\/]+$/) == 0;

    function removeCookie() {
        var day = new Date();
        var access = day.getTime();
        day.setTime(access - 7*24*60*60*1000);
        document.cookie = 'tmpaccess=0; ' +
                          'path=/; ' +
                          'expires=' + day.toGMTString();
    }

    function readCookie() {
        if (document.cookie.search(/tmpaccess=([0-9]*)/) >= 0) {
            return RegExp.$1;
        } else {
            return null;
        }
    }

    function jumpto(id) {
        var s = new String(window.location);
        if (s.search("#") < 0) {
            window.location.hash = "r" + id;
        }
    }

    function setNewPost(dt) {
        if (lastpage) {
            var a = dt.getElementsByTagName('a')[0];
            a.style.fontWeight = 'bold';
        }
    }

    function newPosts(access) {
        if (access) {
            var read = access
        } else {
            var read = 0;
        }
        var dt = document.getElementsByTagName('dt');
        var newid = '';
        for (var i=0; i<dt.length; i++) {
            var span = dt[i].getElementsByTagName('span');
            for (var j=0; j<span.length; j++) {
                if ((span[j].className == 'stamp') &&
                    (span[j].id.search(/s([0-9]*)$/) == 0)) {
                    var stamp = RegExp.$1;
                    if (stamp > read) {
                        if (! newid) {
                            newid = dt[i].id.substring(1);
                        }
                        setNewPost(dt[i]);
                    }
                }
            }
        }
        if (! access) {
        } else if (newid) {
            jumpto(newid);
        } else {
            jumpto(dt[dt.length-1].id.substring(1));
        }
    }

    var access = readCookie();
    newPosts(access);
    removeCookie();
});
