/* Popup Res Anchor.
 * Copyright (C) 2005-2012 shinGETsu Project.
 */

shingetsu.initialize(function () {
    var ajaxCache = {};

    shingetsu.plugins.popupAnchor = function (e, aid) {
        function doPopup(coordinate, html) {
            html = html.replace(new RegExp('</?(input|a)[^<>]*>', 'ig'), '')
                       .replace(new RegExp('(<br[^<>]*>\\s*)*$', 'i'), '');
            if (html.search(/<dt/) < 0) {
                html = '<div>Error or Not Found</div>';
            }
            shingetsu.plugins.showPopup(coordinate, html);
        }

        function popupInner(coordinate, dt, dd) {
            var html = '<dl><dt>' + dt.html() + '</dt><dd>' + dd.html() + '</dd></dl>';
            doPopup(coordinate, html);
        }

        function popupAjax(coordinate, aid) {
            if (ajaxCache[aid]) {
                doPopup(coordinate, ajaxCache[aid]);
                return;
            }
            shingetsu.plugins.showPopup(coordinate, '<div>Loading...</div>');
            $.ajax({
                url: e.currentTarget.href + '?ajax=true',
                dataType: 'html',
                success: function (html) { 
                    ajaxCache[aid] = html;
                    doPopup(coordinate, html);
                }
            });
        }

        var coordinate = new shingetsu.plugins.Coordinate(e);
        var dt = $('#r' + aid);
        var dd = $('#b' + aid);
        if (dt.length && dd.length) {
            popupInner(coordinate, dt, dd);
        } else {
            popupAjax(coordinate, aid);
        }
    };

    function tryJump(event, id) {
        shingetsu.plugins.hidePopup();
        if (! document.getElementById('r' + id)) {
            return;
        }
        if (event.originalEvent.button === 1) {
            return;
        }
        event.preventDefault();
        $('body').animate({scrollTop: $('#r' + id).offset().top}, 'fast'); 
        location.hash = '#r' + id;
    }

    $('a').each(function (i, anchor) {
        if (anchor.className != 'innerlink') {
            return;
        }
        if (anchor.href.search(/([0-9a-f]{8})/) <= 0) {
            return;
        }
        var id = RegExp.$1;
        $(anchor).mouseover(function (e) { shingetsu.plugins.popupAnchor(e, id) })
                 .mouseout(function (e) { shingetsu.plugins.hidePopup() })
                 .click(function (e) { tryJump(e, id) });
    });
});
