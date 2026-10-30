/*
 * Jump New Posts.
 * Copyright (C) 2006 shinGETsu Project.
 */

shingetsu.initialize(function () {
    let itemKey = null;
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
        if (!window.location.href.includes("#")) {
            const target = document.getElementById("r" + id);
            if (target) {
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        }
    }

    function setNewPost(dt) {
        if (itemKey) {
            const element = typeof dt === 'string' ? document.querySelector(dt) : dt;

            if (element) {
                element.classList.add("newpost");
            }
        }
    }

    function newPosts(access) {
        const read = access ? access : 0;
        let newid = "";
        let lastStamp = null;

        const stamps = document.querySelectorAll("dt span.stamp[data-stamp]");
        stamps.forEach(function (span) {
            const stamp = Number(span.dataset.stamp);

            if (stamp > read) {
                const dt = span.closest("dt");
                if (dt) {
                    if (!newid) {
                        newid = dt.id.substring(1);
                    }
                    setNewPost(dt);
                }
            }
            lastStamp = span;
        });

        if (lastStamp) {
            setAccess(Number(lastStamp.dataset.stamp) + 1);
        }

        if (!access) {
            // nop
        } else if (newid) {
            jumpto(newid);
        } else if (lastStamp) {
            const lastDt = lastStamp.closest("dt");
            if (lastDt && lastDt.id) {
                jumpto(lastDt.id.substring(1));
            }
        }
    }

    newPosts(getAccess());
});
