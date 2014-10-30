/* -*- coding: utf-8 -*-
 * Response Post.
 * Copyright (C) 2006-2012 shinGETsu Project.
 */

shingetsu.initialize(function () {
    var msg_res = '[Res.]';
    if (shingetsu.uiLang == 'ja') {
        msg_res = '[返信]';
    }

    function res(id) {
        var textArea = $('#body');
        if (textArea.val()) {
            textArea.val(textArea.val() + '\n>>' + id + '\n');
        } else {
            textArea.val('>>' + id + '\n');
        }

        var anchor = $('<a>').text('>>' + id);
        if ($('#records').find('#r' + id).length) {
            anchor.attr('href', '#r' + id)
                  .addClass('innerlink');
        } else {
            if (location.href.search(/(.+\/thread\.cgi\/[^\/]*)/) == 0) {
                anchor.attr('href', RegExp.$1 + '/' + id)
                      .addClass('reclink');
            }
        }
        $('#resreferrer').append(anchor);
        shingetsu.plugins.rootResAnchor.parseContent($('#resreferrer'));
        textArea.focus();
    }

    function addLink($container) {
        $container.find('dt').each(function (i, dt) {
            var $dt = $(dt);
            if ($dt.attr('data-record-id')) {
                $dt.find('a[data-responce-id]').remove();
                var id = $dt.attr('data-record-id');
                var $anchor = $('<a>');
                $anchor.attr('href', 'javascript:;')
                       .text(msg_res)
                       .attr('data-responce-id', id);
            }
            $dt.append($anchor);
        });
    }

    var ref = $('<div>');
    ref.attr('id', 'resreferrer');
    $('#body').before(ref);

    addLink($(document));

    shingetsu.plugins.responce = {
        'addLink': addLink
    };

    $(document).on('click', 'a[data-responce-id]', function (e) {
        res($(this).attr('data-responce-id'));
        return false;
    });
});
