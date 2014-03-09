/* Popup Res Anchor.
 * Copyright (C) 2005-2012 shinGETsu Project.
 */

shingetsu.initialize(function () {

    function ResAnchor(opt_parameters) {
        $.extend(this, {
            parentResAnchor: null,
            childResAnchors: [],
            container: null,
            aid: null,
            url: null,
            furtherPopup: null,
            hidingTimer: null
        }, opt_parameters);

        if (this.container) {
            this.container
                .on('mouseenter', $.proxy(function (event) {
                    this.cancelDescentHidingTimer();
                    if (!this.furtherPopup) {
                        this.popup(
                            new shingetsu.plugins.Coordinate(event));
                    }
                }, this))
                .on('mouseleave', $.proxy(function () {
                    this.cancelHidingTimer();
                    this.hidingTimer = setTimeout($.proxy(function () {
                        if (this.furtherPopup) {
                            this.furtherPopup.destroy();
                            this.furtherPopup = null;
                        }
                    }, this), 200);
                    this.furtherPopup.hide();
                }, this));
        }
    }
    function popup(coordinate) {
        var that = this;
        var url = $(this.container).prop('href');
        var parentPopup;
        if (this.parentResAnchor) {
            parentPopup = this.parentResAnchor.furtherPopup;
        }
        var furtherPopup = new shingetsu.plugins.Popup({
            parentPopup: parentPopup,
            coordinate: coordinate
        });
        furtherPopup.container
            .on("mouseenter", function () {
                that.cancelDescentHidingTimer();
            })
            // =====================================
            .on("mouseleave", $.proxy(function () {
                that.cancelHidingTimer();
                that.hidingTimer
                = setTimeout($.proxy(function () {
                    this.destroy();
                    that.furtherPopup = null;
                }, this), 200);
                that.furtherPopup.hide();
                that.refireDescentMouseleave();
            }, furtherPopup));
        if (parentPopup) {
            parentPopup.appendChild(furtherPopup);
        }
        this.furtherPopup = furtherPopup;
        furtherPopup.show(coordinate);
        this.loadContent();
    }
    function loadContent() {
        var html = this.cache[this.aid];
        if (!html) {
            var dt = $('#r' + this.aid);
            var dd = $('#b' + this.aid);
            if (dt.length && dd.length) {
                html = "<dl><dt>" + dt.html() + "</dt><dd>"
                    + dd.html() + "</dd></dl>";
                this.cache[this.aid] = html;
                this.setHtml(html);
                this.parseContent();
            } else {
                this.furtherPopup.setContent('<div>Loading...</div>');
                $.ajax({
                    url: this.url + '?ajax=true',
                    dataType: 'html',
                    success: $.proxy(function (html) {
                        this.cache[this.aid] = html;
                        this.setHtml(html);
                        this.parseContent();
                    }, this)
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
            html = '<div>Error or Not Found</div>';
        }
        this.furtherPopup.setContent(
            $(html).addClass('panel panel-default'));
    }
    function parseContent() {
        var that = this;
        this.childResAnchors = [];
        $(this.furtherPopup.container).find("a").each(function () {
            if (!$(this).hasClass("innerlink")
                && !$(this).hasClass("reclink")) {
                return;
            }
            if (this.href.search(/([0-9a-f]{8})/) <= 0) {
                return;
            }
            var aid = RegExp.$1;
            var resAnchor = new ResAnchor({
                parentResAnchor: that,
                container: $(this),
                aid: aid,
                url: $(this).prop("href")
            });
            that.childResAnchors.push(resAnchor);

            $(this).click(function (e) {
                that.tryJump(e, id);
            });
        });
    }
    function cancelHidingTimer() {
        clearTimeout(this.hidingTimer);
        if (this.furtherPopup) {
            $(this.furtherPopup.container).stop(true, true).show();
        }
    }
    function cancelDescentHidingTimer() {
        this.cancelHidingTimer();
        if (this.parentResAnchor) {
            this.parentResAnchor.cancelDescentHidingTimer();
        }
    }
    function refireMouseleave() {
        if (this.container) {
            this.container.trigger('mouseleave');
        }
    }
    function refireDescentMouseleave() {
        this.refireMouseleave();
        if (this.parentResAnchor) {
            this.parentResAnchor.refireMouseleave();
        }
    }
    function tryJump(event, id) {
        shingetsu.plugins.hidePopup();
        if (!document.getElementById('r' + id)) {
            return;
        }
        if (event.originalEvent.button === 1) {
            return;
        }
        event.preventDefault();
        $('body').animate({scrollTop: $('#r' + id).offset().top}, 'fast'); 
        location.hash = '#r' + id;
    }

    ResAnchor.prototype = {
        constructor: ResAnchor,
        cache: {},
        popup: popup,
        loadContent: loadContent,
        setHtml: setHtml,
        parseContent: parseContent,
        cancelHidingTimer: cancelHidingTimer,
        cancelDescentHidingTimer: cancelDescentHidingTimer,
        refireMouseleave: refireMouseleave,
        refireDescentMouseleave: refireDescentMouseleave,
        tryJump: tryJump
    };

    shingetsu.plugins.ResAnchor = ResAnchor;

    var resAnchor = new ResAnchor();
    resAnchor.furtherPopup = new shingetsu.plugins.Popup({
        container: document.body
    });
    resAnchor.parseContent();
    shingetsu.plugins.rootResAnchor = resAnchor;
});
