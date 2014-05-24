/*
 * Jump New Posts.
 * Copyright (C) 2006-2012 shinGETsu Project.
 */

shingetsu.initialize(function () {
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
            $("html").animate({
                scrollTop: $("#r" + id).offset().top
            }, {
                duration: 200
            });
        }
    }

    function setNewPost(dt) {
        if (lastpage) {
            var a = dt.getElementsByTagName('a')[0];
            a.style.fontWeight = 'bold';
            $(a).addClass("newpost");
        }
    }

    function newPosts(access) {
        if (access) {
            var read = access
        } else {
            var read = 0;
        }
        var newid = "";
        var lastStamp = null;
        $("dt span.stamp").each(function () {
            if (this.id.search(/s([0-9]*)$/) == 0) {
                var stamp = RegExp.$1;
                if (stamp > read) {
                    var dt = $(this).closest("dt").get(0);
                    if (!newid) {
                        newid = dt.id.substring(1);
                    }
                    setNewPost(dt);
                }
            }
            lastStamp = this;
        });
        if (! access) {
        } else if (newid) {
            jumpto(newid);
        } else {
            jumpto($(lastStamp).closest("dt").get(0).id.substring(1));
        }
    }

    var access = readCookie();
    newPosts(access);
    removeCookie();
});
