/* Popup Res Anchor.
 * Copyright (C) 2005-2013 shinGETsu Project.
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
            destroyTimer: null
        }, opt_parameters);

        if (this.container) {
            this.container
                .on('mouseenter', $.proxy(function (event) {
                    this.cancelDescentDestroyTimer();
                    if (!this.furtherPopup) {
                        this.popup(
                            new shingetsu.plugins.Coordinate(event));
                    }
                }, this))
                .on('mouseleave', $.proxy(function () {
                    this.cancelDestroyTimer();
                    this.destroyTimer = setTimeout($.proxy(function () {
                        if (this.furtherPopup) {
                            this.furtherPopup.destroy();
                            this.furtherPopup = null;
                        }
                    }, this), shingetsu.plugins.Popup.hidingDuration);
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
                that.cancelDescentDestroyTimer();
            })
            .on("mouseleave", $.proxy(function () {
                that.cancelDestroyTimer();
                that.destroyTimer
                = setTimeout($.proxy(function () {
                    this.destroy();
                    that.furtherPopup = null;
                }, this), shingetsu.plugins.Popup.hidingDuration);
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
                this.furtherPopup.setContent('<div>'
                    + ResAnchor.message.loading + '</div>');
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
            html = '<div>' + ResAnchor.message.notFound + '</div>';
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
                that.tryJump(e, aid);
            });
        });
    }
    function cancelDestroyTimer() {
        clearTimeout(this.destroyTimer);
        if (this.furtherPopup) {
            $(this.furtherPopup.container).stop(true, true).show();
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
        var root = shingetsu.plugins.rootResAnchor.furtherPopup;
        var i = root.childPopups.length;
        while (i--) {
            root.childPopups[i].destroy();
            root.childPopups.splice(i, 1);
        }
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

    var message = {
        'en': {
            loading: 'Loading...',
            notFound: 'Error or Not Found'
        },
        'ja': {
            loading: '読み込み中です・・・',
            notFound: 'エラーが発生したか、見つかりません'
        }
    };
    $.extend(ResAnchor, {
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

    shingetsu.plugins.ResAnchor = ResAnchor;

    var resAnchor = new ResAnchor();
    resAnchor.furtherPopup = new shingetsu.plugins.Popup({
        container: document.body
    });
    resAnchor.parseContent();
    shingetsu.plugins.rootResAnchor = resAnchor;
});
