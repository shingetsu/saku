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

        var anchor = $('<a>');
        anchor.attr('href', '#r' + id)
              .addClass('innerlink')
              .text('>>' + id);

        $('#resreferrer').append(anchor);
        shingetsu.plugins.rootResAnchor.parseContent($('#resreferrer'));
        textArea.focus();
    }

    $('dt').each(function (i, dt) {
        dt = $(dt);
        var id = dt.attr('id').substr(1);
        var anchor = $('<a>');
        anchor.attr('href', 'javascript:;')
              .text(msg_res)
              .attr('data-responce-id', id)
              .click(function (e) { res(id) });
        dt.append(anchor);
    });

    var ref = $('<div>');
    ref.attr('id', 'resreferrer');
    $('#body').before(ref);

    shingetsu.plugins.responce = {
        responceTo: res
    };
});
