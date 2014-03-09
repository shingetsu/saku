/* Popup.
 * Copyright (C) 2005-2012 shinGETsu Project.
 */
(function () {
    function Coordinate(e, opt_y, opt_z) {
        $.extend(this, {
            x: e,
            y: opt_y,
            z: opt_z
        });

        if (this.y === undefined) {
            if (e) {
                this.x = e.pageX;
                this.y = e.pageY;
            } else {
                this.x = event.clientX;
                this.y = event.clientY;
            }
        }
    }
    shingetsu.plugins.Coordinate = Coordinate;
})();

(function () {
    function Popup(opt_parameters) {
        $.extend(this, {
            parentPopup: null,
            childPopups: [],
            container: null,
            content: null,
            coordinate: null
        }, opt_parameters);

        if (!this.container) {
            this.container = this.createContainer(this.content);
        } else {
            this.container = $(this.container);
        }
        if ($(document).has(this.container).length === 0) {
            this.container.hide().appendTo(document.body);
        }
    }
    function createContainer(content) {
        return $('<div>')
            .addClass('popup')
            .css('position', 'absolute')
            .append(content);
    }
    function setContent(content) {
        this.content = content;
        this.container.empty().append(content);
    }
    function appendChild(childPopup) {
        this.childPopups.push(childPopup);
    }
    function reposition(coordinate) {
        var width = this.container.width();
        var height = this.container.height();
        var x = Math.max($(document).scrollLeft(), coordinate.x + 20);
        var y = Math.max($(document).scrollTop(), coordinate.y - height);
        this.container
            .css('left', x)
            .css('top', y);
        if (coordinate.z !== undefined) {
            this.container.css('zIndex', coordinate.z);
        }
    }
    function show(coordinate) {
        this.reposition(coordinate);
        this.container.show();
    }
    function hide() {
        this.container.fadeOut({
            duration: 200
        });
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
        this.container.remove();
        this.container = null;
    }
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
            exclusivePopup.hide();
        }
        var popup = new shingetsu.plugins.Popup({
            coordinate: coordinate,
            content: objects
        });
        popup.container.prop('id', 'popup');
        exclusivePopup = popup;
        exclusivePopup.show(coordinate);

        $('select').hide();
        
        return exclusivePopup;
    }
    function hidePopup() {
        if (exclusivePopup) {
            exclusivePopup.hide();
            exclusivePopup = null;
        }

        $('select').show();
    }

    shingetsu.plugins.showPopup = showPopup;
    shingetsu.plugins.hidePopup = hidePopup;
})();
