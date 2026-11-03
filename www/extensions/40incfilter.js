shingetsu.initialize(() => {
    const Position = {
        offset(elm) {
            const el = elm.nodeType ? elm : elm;
            let x = 0;
            let y = 0;
            let current = el;
            while (current) {
                x += current.offsetLeft || 0;
                y += current.offsetTop || 0;
                current = current.offsetParent;
            }
            return { x, y };
        },

        page(e) {
            if (e.pageX != null) {
                return { x: e.pageX, y: e.pageY };
            }
            const doc = document.documentElement || document.body;
            return {
                x: e.clientX + doc.scrollLeft,
                y: e.clientY + doc.scrollTop
            };
        }
    };

    /* --------------------------------------------- */

    class ElementResizer {
        constructor(elm) {
            this.elm = elm.length !== undefined ? elm[0] : elm;
            this._enable = false;
            this._cursor = false;

            this.elm.addEventListener('mousedown', (e) => this.start(e));
            this.elm.addEventListener('mousemove', (e) => this.pointer(e));
            document.body.addEventListener('mouseup', (e) => this.stop(e));
            document.body.addEventListener('mousemove', (e) => this.doResize(e));
        }

        pointer(e) {
            if (!this._cursor && this.resizePoint(e)) {
                this.elm.style.cursor = 'se-resize';
                this._cursor = true;
            } else if (this._cursor && !this.resizePoint(e)) {
                this.elm.style.cursor = 'default';
                this._cursor = false;
            }
        }

        start(e) {
            if (this.resizePoint(e)) {
                this._enable = true;
            }
        }

        stop() {
            this._enable = false;
        }

        resizePoint(e) {
            const offset = Position.offset(this.elm);
            const page = Position.page(e);

            offset.y += this.elm.offsetHeight;
            offset.x += this.elm.offsetWidth;

            if (offset.y - 32 < page.y && page.y < offset.y &&
                offset.x - 32 < page.x && page.x < offset.x - 8) {
                return true;
            }
            return false;
        }

        doResize(e) {
            if (!this._enable) return;
            const offset = Position.offset(this.elm);
            const page = Position.page(e);

            let width = page.x - offset.x + 24;
            let height = page.y - offset.y + 16;
            if (width < 50) width = 50;
            if (height < 50) height = 50;

            this.elm.style.height = height + 'px';
            this.elm.style.width = width + 'px';
        }
    }

    if (/\/thread\.cgi\/.*/.test(location.pathname)) {
        const textarea = document.querySelector('#postarticle textarea[name="body"]');
        if (textarea) {
            new ElementResizer(textarea);
        }
    }
});
