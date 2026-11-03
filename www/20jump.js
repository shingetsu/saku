/**
 * Jump New Posts.
 * Copyright (C) 2006 shinGETsu Project.
 */

shingetsu.initialize(() => {
    let itemKey = null;
    const match = location.pathname.match(/^\/?thread.cgi\/([^\/]+)$/);
    if (match) {
        try {
            itemKey = `access_${decodeURIComponent(match[1])}`;
        } catch (e) {
            // Decoding failed
        }
    }

    const getAccess = () => {
        if (!itemKey) return 0;
        try {
            const val = localStorage.getItem(itemKey);
            return val !== null ? parseInt(val, 10) : 0;
        } catch (e) {
            return 0;
        }
    };

    const setAccess = (access) => {
        if (!itemKey) return;
        try {
            localStorage.setItem(itemKey, access);
        } catch (e) {
            // Storage might be full or restricted
        }
    };

    const jumpto = (id) => {
        if (!location.hash) {
            const target = document.getElementById(`r${id}`);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    };

    const setNewPost = (dt) => {
        if (!itemKey) return;
        const element = typeof dt === 'string' ? document.querySelector(dt) : dt;
        if (element) {
            element.classList.add('newpost');
        }
    };

    const newPosts = (access) => {
        const read = access || 0;
        let newid = '';
        let lastStamp = null;

        const stamps = document.querySelectorAll('dt span.stamp[data-stamp]');
        stamps.forEach((span) => {
            const stamp = Number(span.dataset.stamp);

            if (stamp > read) {
                const dt = span.closest('dt');
                if (dt) {
                    if (!newid && dt.id) {
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

        if (access && newid) {
            jumpto(newid);
        } else if (access && lastStamp) {
            const lastDt = lastStamp.closest('dt');
            if (lastDt && lastDt.id) {
                jumpto(lastDt.id.substring(1));
            }
        }
    };

    newPosts(getAccess());
});
