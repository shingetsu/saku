/* -*- coding: utf-8 -*-
 * Popup Res Anchor.
 * Copyright (C) 2005 shinGETsu Project.
 */

shingetsu.initialize(function () {

    function ResAnchor(opt_parameters) {
        Object.assign(this, {
            parentResAnchor: null,
            childResAnchors: [],
            container: null,
            aid: null,
            url: null,
            furtherPopup: null,
            destroyTimer: null
        }, opt_parameters);

        if (this.container) {
            this.container.addEventListener('mouseenter', (event) => {
                this.cancelDescentDestroyTimer();
                if (!this.furtherPopup) {
                    this.popup(
                        new shingetsu.plugins.Coordinate(event));
                }
            });

            this.container.addEventListener('mouseleave', () => {
                this.cancelDestroyTimer();
                this.destroyTimer = setTimeout(() => {
                    if (this.furtherPopup) {
                        this.furtherPopup.destroy();
                        this.furtherPopup = null;
                    }
                }, shingetsu.plugins.Popup.hidingDuration);

                if (this.furtherPopup) {
                    this.furtherPopup.hide();
                }
            });
        }
    }

    function popup(coordinate) {
        const url = this.container.href;
        let parentPopup;
        if (this.parentResAnchor) {
            parentPopup = this.parentResAnchor.furtherPopup;
        }
        const furtherPopup = new shingetsu.plugins.Popup({
            parentPopup: parentPopup,
            coordinate: coordinate
        });

        furtherPopup.container.addEventListener("mouseenter", () => {
            this.cancelDescentDestroyTimer();
        });

        furtherPopup.container.addEventListener("mouseleave", () => {
            this.cancelDestroyTimer();
            this.destroyTimer = setTimeout(() => {
                furtherPopup.destroy();
                this.furtherPopup = null;
            }, shingetsu.plugins.Popup.hidingDuration);

            this.furtherPopup.hide();
            this.refireDescentMouseleave();
        });

        if (parentPopup) {
            parentPopup.appendChild(furtherPopup);
        }
        this.furtherPopup = furtherPopup;
        furtherPopup.show(coordinate);
        this.loadContent();
    }

    function loadContent() {
        let html = this.cache[this.aid];
        if (!html) {
            const dt = document.getElementById('r' + this.aid);
            const dd = document.getElementById('b' + this.aid);
            if (dt && dd) {
                html = "<dl><dt>" + dt.innerHTML + "</dt><dd>"
                    + dd.innerHTML + "</dd></dl>";
                this.cache[this.aid] = html;
                this.setHtml(html);
                this.parseContent();
            } else {
                this.furtherPopup.setContent('<div>'
                    + ResAnchor.message.loading + '</div>');

                fetch(this.url + '?ajax=true')
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.text();
                    })
                    .then(html => {
                        this.cache[this.aid] = html;
                        this.setHtml(html);
                        this.parseContent();
                    })
                    .catch(error => {
                        console.error('Failed to load content:', error);
                    });
            }
        } else {
            this.setHtml(html);
            this.parseContent();
        }
    }

    function setHtml(html) {
        html = html.replace(new RegExp('</?(input)[^<>]*>', 'ig'), '')
                   .replace(new RegExp('(<br[^<>]*>\\s*)*$', 'i'), '');
        if (html.search(/<dt/) < 0) {
            html = '<div>' + ResAnchor.message.notFound + '</div>';
        }

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;

        if (tempDiv.firstElementChild) {
            tempDiv.firstElementChild.classList.add('panel', 'panel-default');
        }

        this.furtherPopup.setContent(tempDiv.firstElementChild || tempDiv);
    }

    function parseContent(container) {
        if (!container) {
            container = this.furtherPopup.container;
        }
        shingetsu.modifyRecords(container);

        this.childResAnchors = [];

        container.querySelectorAll('a').forEach(anchor => {
            if (!anchor.classList.contains("innerlink")
                && !anchor.classList.contains("reclink")) {
                return;
            }
            if (anchor.href.search(/([0-9a-f]{8})/) <= 0) {
                return;
            }
            const aid = RegExp.$1;
            const resAnchor = new ResAnchor({
                parentResAnchor: this,
                container: anchor,
                aid: aid,
                url: anchor.href
            });
            this.childResAnchors.push(resAnchor);

            anchor.addEventListener('click', (e) => {
                this.tryJump(e, aid);
            });
        });
    }

    function cancelDestroyTimer() {
        clearTimeout(this.destroyTimer);
        if (this.furtherPopup) {
            const container = this.furtherPopup.container;
            if (container) {
                container.style.display = '';
            }
        }
    }

    function cancelDescentDestroyTimer() {
        this.cancelDestroyTimer();
        if (this.parentResAnchor) {
            this.parentResAnchor.cancelDescentDestroyTimer();
        }
    }

    function refireMouseleave() {
        if (this.container) {
            this.container.dispatchEvent(new Event('mouseleave', { bubbles: true }));
        }
    }

    function refireDescentMouseleave() {
        this.refireMouseleave();
        if (this.parentResAnchor) {
            this.parentResAnchor.refireMouseleave();
        }
    }

    function tryJump(event, id) {
        const root = shingetsu.plugins.rootResAnchor.furtherPopup;
        let i = root.childPopups.length;
        while (i--) {
            root.childPopups[i].destroy();
            root.childPopups.splice(i, 1);
        }
        const targetElement = document.getElementById('r' + id);
        if (!targetElement) {
            return;
        }
        if (event.button === 1) {
            return;
        }
        event.preventDefault();

        const targetTop = targetElement.getBoundingClientRect().top + window.pageYOffset;
        window.scrollTo({
            top: targetTop,
            behavior: 'smooth'
        });

        location.hash = '#r' + id;
    }

    const message = {
        'en': {
            loading: 'Loading...',
            notFound: 'Error or Not Found'
        },
        'ja': {
            loading: '読み込み中です・・・',
            notFound: 'エラーが発生したか、見つかりません'
        }
    };
    Object.assign(ResAnchor, {
        message: message[shingetsu.uiLang] || message['en']
    });
    ResAnchor.prototype = {
        constructor: ResAnchor,
        cache: {},
        popup: popup,
        loadContent: loadContent,
        setHtml: setHtml,
        parseContent: parseContent,
        cancelDestroyTimer: cancelDestroyTimer,
        cancelDescentDestroyTimer: cancelDescentDestroyTimer,
        refireMouseleave: refireMouseleave,
        refireDescentMouseleave: refireDescentMouseleave,
        tryJump: tryJump
    };

    const resAnchor = new ResAnchor();
    resAnchor.furtherPopup = new shingetsu.plugins.Popup({
        container: document.body
    });
    resAnchor.parseContent();
    shingetsu.plugins.rootResAnchor = resAnchor;
});
