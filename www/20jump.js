/*
 * Jump New Posts.
 * Copyright (C) 2006-2019 shinGETsu Project.
 */

shingetsu.initialize(function () {
    var itemKey = null;
    if (location.pathname.search(/^\/?thread.cgi\/([^\/]+)$/) === 0) {
        try {
            itemKey = 'access_' + decodeURI(RegExp.$1);
        } catch {
        }
    }

    function getAccess() {
        if (! itemKey) {
            return 0;
        }
        try {
            return parseInt(localStorage.getItem(itemKey));
        } catch {
            return 0;
        }
    }

    function setAccess() {
        if (! itemKey) {
            return;
        }
        var now = Math.floor(Date.now() / 1000);
        localStorage.setItem(itemKey, now.toString()); 
    }

    function jumpto(id) {
        var s = new String(window.location);
        if (s.search("#") < 0) {
            $("html,body").animate({
                scrollTop: $("#r" + id).offset().top
            }, {
                duration: 200
            });
        }
    }

    function setNewPost(dt) {
        if (itemKey) {
            $(dt).addClass("newpost");
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
        $("dt span.stamp[data-stamp]").each(function () {
            var stamp = $(this).attr('data-stamp');
            if (stamp > read) {
                var dt = $(this).closest("dt").get(0);
                if (!newid) {
                    newid = dt.id.substring(1);
                }
                setNewPost(dt);
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

    newPosts(getAccess());
    setAccess();
});
