/**
 * Popup.
 * Copyright (C) 2005 shinGETsu Project.
 */

shingetsu.plugins.Coordinate = class {
    constructor(e, opt_y, opt_z) {
        this.x = e;
        this.y = opt_y;
        this.z = opt_z;

        if (this.y === undefined) {
            if (e && typeof e.pageX === 'number') {
                this.x = e.pageX;
                this.y = e.pageY;
            } else {
                // for old browsers
                const evt = window.event;
                this.x = evt ? evt.clientX : undefined;
                this.y = evt ? evt.clientY : undefined;
            }
        }
    }
};


shingetsu.plugins.Popup = class {
    static hidingDuration = 200;

    constructor(parameters = {}) {
        Object.assign(this, {
            parentPopup: null,
            childPopups: [],
            container: null,
            content: null,
            coordinate: null
        }, parameters);

        if (!this.container) {
            this.container = this.createContainer(this.content);
        } else if (typeof this.container === 'string') {
            this.container = document.querySelector(this.container);
        }

        if (this.container && this.container !== document.body && !document.body.contains(this.container)) {
            this.container.style.display = 'none';
            document.body.appendChild(this.container);
        }
    }

    createContainer(content) {
        const div = document.createElement('div');
        div.classList.add('popup');
        div.style.position = 'absolute';
        this._renderContent(div, content);
        return div;
    }

    _renderContent(container, content) {
        container.replaceChildren();
        if (content) {
            if (content instanceof Node) {
                container.appendChild(content);
            } else if (typeof content === 'string') {
                container.innerHTML = content;
            }
        }
    }

    setContent(content) {
        this.content = content;
        if (this.container && this.container !== document.body) {
            this._renderContent(this.container, content);
        }
    }

    appendChild(childPopup) {
        this.childPopups.push(childPopup);
    }

    reposition(coordinate) {
        if (!this.container || this.container === document.body || !coordinate) return;

        const scrollLeft = window.scrollX || document.documentElement.scrollLeft;
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const height = this.container.offsetHeight;

        const x = Math.max(scrollLeft, coordinate.x + 20);
        const y = Math.max(scrollTop, coordinate.y - height);

        this.container.style.left = `${x}px`;
        this.container.style.top = `${y}px`;

        if (coordinate.z !== undefined) {
            this.container.style.zIndex = coordinate.z;
        }
    }

    show(coordinate) {
        this.reposition(coordinate);
        const el = this.container;
        if (el && el !== document.body) {
            el.style.display = '';
            el.style.opacity = '1';
        }
    }

    hide(options = {}) {
        const config = {
            duration: this.constructor.hidingDuration,
            ...options
        };

        const el = this.container;
        if (!el || el === document.body) return;

        const duration = config.duration;
        el.style.transition = `opacity ${duration}ms ease`;
        el.style.opacity = '0';

        setTimeout(() => {
            if (el && el !== document.body) {
                el.style.display = 'none';
            }
            if (typeof config.complete === 'function') {
                config.complete.call(this);
            }
        }, duration);
    }

    destroy() {
        while (this.childPopups.length > 0) {
            const child = this.childPopups.pop();
            child.destroy();
        }

        if (this.parentPopup) {
            const index = this.parentPopup.childPopups.indexOf(this);
            if (index !== -1) {
                this.parentPopup.childPopups.splice(index, 1);
            }
            this.parentPopup = null;
        }

        if (this.container && this.container !== document.body) {
            this.container.remove();
            this.container = null;
        }
    }
};


(() => {
    let exclusivePopup = null;

    const showPopup = (coordinate, objects) => {
        if (exclusivePopup) {
            exclusivePopup.hide({
                complete: function () {
                    this.destroy();
                }
            });
        }

        const popup = new shingetsu.plugins.Popup({
            coordinate,
            content: objects
        });

        if (popup.container && popup.container !== document.body) {
            popup.container.id = 'popup';
        }

        exclusivePopup = popup;
        exclusivePopup.show(coordinate);

        document.querySelectorAll('select').forEach((select) => {
            select.style.display = 'none';
        });

        return exclusivePopup;
    };

    const hidePopup = () => {
        if (exclusivePopup) {
            exclusivePopup.hide({
                complete: function () {
                    this.destroy();
                }
            });
            exclusivePopup = null;
        }
        document.querySelectorAll('select').forEach((el) => {
            el.style.display = '';
        });
    };

    shingetsu.plugins.showPopup = showPopup;
    shingetsu.plugins.hidePopup = hidePopup;
})();
