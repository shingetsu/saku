/**
 * Popup Res Anchor.
 * Copyright (C) 2005 shinGETsu Project.
 */

shingetsu.initialize(() => {
    class ResAnchor {
        static messages = {
            en: {
                loading: 'Loading...',
                notFound: 'Error or Not Found'
            },
            ja: {
                loading: '読み込み中です・・・',
                notFound: 'エラーが発生したか、見つかりません'
            }
        };

        static get message() {
            return ResAnchor.messages[shingetsu.uiLang] || ResAnchor.messages.en;
        }

        static cache = {};

        constructor(opt_parameters = {}) {
            this.parentResAnchor = null;
            this.childResAnchors = [];
            this.container = null;
            this.aid = null;
            this.url = null;
            this.furtherPopup = null;
            this.destroyTimer = null;

            Object.assign(this, opt_parameters);

            if (this.container) {
                this.container.addEventListener('mouseenter', (event) => {
                    this.cancelDescentDestroyTimer();
                    if (!this.furtherPopup) {
                        this.popup(new shingetsu.plugins.Coordinate(event));
                    } else if (this.furtherPopup.container) {
                        this.furtherPopup.container.style.display = '';
                        this.furtherPopup.container.style.opacity = '1';
                    }
                });

                this.container.addEventListener('mouseleave', () => {
                    this.scheduleDestroy();
                });
            }
        }

        scheduleDestroy() {
            this.cancelDestroyTimer();
            this.destroyTimer = setTimeout(() => {
                if (this.furtherPopup) {
                    this.furtherPopup.destroy();
                    this.furtherPopup = null;
                }
            }, shingetsu.plugins.Popup.hidingDuration);
        }

        popup(coordinate) {
            let parentPopup = null;
            if (this.parentResAnchor) {
                parentPopup = this.parentResAnchor.furtherPopup;
            }

            const furtherPopup = new shingetsu.plugins.Popup({
                parentPopup,
                coordinate
            });

            furtherPopup.container.addEventListener('mouseenter', () => {
                this.cancelDescentDestroyTimer();
                if (furtherPopup.container) {
                    furtherPopup.container.style.display = '';
                    furtherPopup.container.style.opacity = '1';
                }
            });

            furtherPopup.container.addEventListener('mouseleave', () => {
                this.scheduleDestroy();
            });

            if (parentPopup) {
                parentPopup.appendChild(furtherPopup);
            }
            this.furtherPopup = furtherPopup;
            furtherPopup.show(coordinate);
            this.loadContent();
        }

        loadContent() {
            let html = ResAnchor.cache[this.aid];
            if (!html) {
                const dt = document.getElementById(`r${this.aid}`);
                const dd = document.getElementById(`b${this.aid}`);
                if (dt && dd) {
                    html = `<dl><dt>${dt.innerHTML}</dt><dd>${dd.innerHTML}</dd></dl>`;
                    ResAnchor.cache[this.aid] = html;
                    this.setHtml(html);
                    this.parseContent();
                } else {
                    this.furtherPopup.setContent(`<div>${ResAnchor.message.loading}</div>`);

                    fetch(`${this.url}?ajax=true`)
                        .then((response) => {
                            if (!response.ok) {
                                throw new Error('Network response was not ok');
                            }
                            return response.text();
                        })
                        .then((textHtml) => {
                            ResAnchor.cache[this.aid] = textHtml;
                            this.setHtml(textHtml);
                            this.parseContent();
                        })
                        .catch((error) => {
                            console.error('Failed to load content:', error);
                        });
                }
            } else {
                this.setHtml(html);
                this.parseContent();
            }
        }

        setHtml(html) {
            const sanitizedHtml = html
                .replace(/<\/?input[^<>]*>/ig, '')
                .replace(/(<br[^<>]*>\s*)*$/, '');

            const finalHtml = sanitizedHtml.includes('<dt')
                ? sanitizedHtml
                : `<div>${ResAnchor.message.notFound}</div>`;

            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = finalHtml;

            if (tempDiv.firstElementChild) {
                tempDiv.firstElementChild.classList.add('panel', 'panel-default');
            }

            this.furtherPopup.setContent(tempDiv.firstElementChild || tempDiv);
        }

        parseContent(container = this.furtherPopup.container) {
            shingetsu.modifyRecords(container);
            this.childResAnchors = [];

            container.querySelectorAll('a').forEach((anchor) => {
                if (!anchor.classList.contains('innerlink') && !anchor.classList.contains('reclink')) {
                    return;
                }
                const match = anchor.href.match(/([0-9a-f]{8})/);
                if (!match) {
                    return;
                }
                const aid = match[1];
                const resAnchor = new ResAnchor({
                    parentResAnchor: this,
                    container: anchor,
                    aid,
                    url: anchor.href
                });
                this.childResAnchors.push(resAnchor);

                anchor.addEventListener('click', (e) => {
                    this.tryJump(e, aid);
                });
            });
        }

        cancelDestroyTimer() {
            clearTimeout(this.destroyTimer);
            this.destroyTimer = null;
            if (this.furtherPopup?.container && this.furtherPopup.container !== document.body) {
                this.furtherPopup.container.style.display = '';
                this.furtherPopup.container.style.opacity = '1';
            }
        }

        cancelDescentDestroyTimer() {
            this.cancelDestroyTimer();
            if (this.parentResAnchor) {
                this.parentResAnchor.cancelDescentDestroyTimer();
            }
        }

        tryJump(event, id) {
            const root = shingetsu.plugins.rootResAnchor?.furtherPopup;
            if (root?.childPopups) {
                while (root.childPopups.length > 0) {
                    const child = root.childPopups.pop();
                    child.destroy();
                }
            }

            const targetElement = document.getElementById(`r${id}`);
            if (!targetElement || event.button === 1) {
                return;
            }
            event.preventDefault();

            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });

            location.hash = `#r${id}`;
        }
    }

    const resAnchor = new ResAnchor();
    resAnchor.furtherPopup = new shingetsu.plugins.Popup({
        container: document.body
    });
    resAnchor.parseContent();
    shingetsu.plugins.rootResAnchor = resAnchor;
});
