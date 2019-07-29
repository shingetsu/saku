/*
 * Jump New Posts.
 * Copyright (C) 2006-2019 shinGETsu Project.
 */

shingetsu.initialize(function () {
    var itemKey = null;
    if (location.pathname.search(/^\/?thread.cgi\/([^\/]+)$/) === 0) {
        try {
            itemKey = 'access_' + decodeURI(RegExp.$1);
        } catch (e) {
        }
    }

    function getAccess() {
        if (! itemKey) {
            return 0;
        }
        try {
            return parseInt(localStorage.getItem(itemKey));
        } catch (e) {
            return 0;
        }
    }

    function setAccess(access) {
        if (! itemKey) {
            return;
        }
        localStorage.setItem(itemKey, access);
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
            var stamp = $(this).data('stamp');
            if (stamp > read) {
                var dt = $(this).closest("dt").get(0);
                if (!newid) {
                    newid = dt.id.substring(1);
                }
                setNewPost(dt);
            }
            lastStamp = this;
        });
        if (lastStamp) {
            setAccess($(lastStamp).data('stamp') + 1);
        }
        if (! access) {
        } else if (newid) {
            jumpto(newid);
        } else {
            jumpto($(lastStamp).closest("dt").get(0).id.substring(1));
        }
    }

    newPosts(getAccess());
});
