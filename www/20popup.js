/* Popup.
 * Copyright (C) 2005 shinGETsu Project.
 */
(function () {
    function Coordinate(e, opt_y, opt_z) {
        Object.assign(this, {
            x: e,
            y: opt_y,
            z: opt_z
        });

        if (this.y === undefined) {
            if (e) {
                this.x = e.pageX;
                this.y = e.pageY;
            } else {
                this.x = window.event ? window.event.clientX : undefined;
                this.y = window.event ? window.event.clientY : undefined;
            }
        }
    }
    shingetsu.plugins.Coordinate = Coordinate;
})();


(function () {
    function Popup(opt_parameters) {
        Object.assign(this, {
            parentPopup: null,
            childPopups: [],
            container: null,
            content: null,
            coordinate: null
        }, opt_parameters);
        if (!this.container) {
            this.container = this.createContainer(this.content);
        } else if (typeof this.container === "string") {
            this.container = document.querySelector(this.container);
        }
        if (this.container && !document.body.contains(this.container)) {
            this.container.style.display = "none";
            document.body.appendChild(this.container);
        }
    }

    function createContainer(content) {
        const div = document.createElement('div');
        div.classList.add('popup');
        div.style.position = 'absolute';
        if (content) {
            if (content instanceof Node) {
                div.appendChild(content);
            } else if (typeof content === 'string') {
                div.innerHTML = content;
            }
        }
        return div;
    }

    function setContent(content) {
        this.content = content;
        while (this.container.firstChild) {
            this.container.removeChild(this.container.firstChild);
        }
        if (content) {
            if (content instanceof Node) {
                this.container.appendChild(content);
            } else if (typeof content === 'string') {
                this.container.innerHTML = content;
            }
        }
    }

    function appendChild(childPopup) {
        this.childPopups.push(childPopup);
    }

    function reposition(coordinate) {
        var width = this.container.offsetWidth;
        var height = this.container.offsetHeight;
        
        var scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        var x = Math.max(scrollLeft, coordinate.x + 20);
        var y = Math.max(scrollTop, coordinate.y - height);
        
        this.container.style.left = x + 'px';
        this.container.style.top = y + 'px';
        
        if (coordinate.z !== undefined) {
            this.container.style.zIndex = coordinate.z;
        }
    }

    function show(coordinate) {
        this.reposition(coordinate);
        const el = this.container;
        el.style.display = '';
        el.style.opacity = '1';
    }

    function hide(options) {
        options = Object.assign({
            duration: Popup.hidingDuration || 400
        }, options);

        const el = this.container;
        const duration = options.duration;

        el.style.transition = `opacity ${duration}ms ease`;
        el.style.opacity = '0';

        setTimeout(function() {
            el.style.display = 'none';
        }, duration);
    }

    function destroy() {
        while (this.childPopups.length) {
            var child = this.childPopups[this.childPopups.length - 1];
            child.destroy();
            this.childPopups.splice(this.childPopups.length - 1, 1);
        }   
        if (this.parentPopup) {
            var siblingPopups = this.parentPopup.childPopups;
            var i = siblingPopups.length;
            while (i--) {
                if (siblingPopups[i] == this) {
                    this.parentPopup.childPopups.splice(i, 1);
                    break;
                }
            }
            this.parentPopup = null;
        }
        if (this.container && this.container.remove) {
            this.container.remove();
        }
        this.container = null;
    }

    Popup.hidingDuration = 200;
    Popup.prototype = {
        constructor: Popup,
        createContainer: createContainer,
        setContent: setContent,
        appendChild: appendChild,
        reposition: reposition,
        show: show,
        hide: hide,
        destroy: destroy
    };
    shingetsu.plugins.Popup = Popup;
})();

(function () {
    var exclusivePopup;

    function showPopup(coordinate, objects) {
        if (exclusivePopup) {
            exclusivePopup.hide({
                complete: function () {
                    this.destroy();
                }.bind(exclusivePopup)
            });
        }
        
        var popup = new shingetsu.plugins.Popup({
            coordinate: coordinate,
            content: objects
        });
        
        popup.container.id = 'popup';
        
        exclusivePopup = popup;
        exclusivePopup.show(coordinate);

        var selects = document.querySelectorAll('select');
        selects.forEach(function (select) {
            select.style.display = 'none';
        });

        return exclusivePopup;
    }

    function hidePopup() {
        if (exclusivePopup) {
            exclusivePopup.hide({
                complete: function () {
                    this.destroy();
                }.bind(exclusivePopup)
            });
            exclusivePopup = null;
        }
        document.querySelectorAll('select').forEach(function(el) {
            el.style.display = '';
        });
    }

    shingetsu.plugins.showPopup = showPopup;
    shingetsu.plugins.hidePopup = hidePopup;
})();
