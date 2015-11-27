/* -*- coding: utf-8 -*-
 * markdown extension
 * https://github.com/WhiteCat6142/shingetsu-extensons
 */

shingetsu.initialize(function () {

    var msgMarkdown = '[MD]';

    function addLink($container) {
        $container.find('dt').each(function (i, dt) {
            var $dt = $(dt);
            if ($dt.attr('data-record-id')) {
                $dt.find('a[data-markdown-id]').remove();
                var id = $dt.attr('data-record-id');
                var $anchor = $('<a>');
                $anchor.attr('href', 'javascript:;')
                       .text(msgMarkdown)
                       .attr('data-markdown-id', id);
            }
            $dt.append($anchor);
        });
    }

    function toggleMarkdown(id) {
        $dd = $('#b' + id);
        if ($dd.length == 0) {
            return;
        }
        var $md = null;
        if ($dd.data('isMarkdown')) {
            $md = $dd.data('md-element');
            $md.remove();
            $dd.data('md-element', null);
            $dd.show();
            $dd.data('isMarkdown', false);
        } else {
            var text = $dd.data('orig-text');
            var $md = $('<dd>');
            $md.addClass('markdown');
            $md.insertAfter($dd);
            $dd.hide();
            if (text.startsWith("@markdown")) {
                $md.html(marked(text.substring("@markdown".length)));
            } else {
                $md.html(marked(text));
            }
            $dd.data('md-element', $md);
            $dd.data('isMarkdown', true);
        }
    }


    function onload() {
        $.each($("dd"),function(i, ele) {
            $ele = $(ele);
            $ele.data('orig-html', $ele.html());
            $ele.data('orig-text', $ele.text());
            $ele.data('md-element', null);
            var text = $ele.text();
            if (text.startsWith("@markdown")) {
                var $md = $('<dd>');
                $md.addClass('markdown');
                $md.insertAfter($ele);
                $ele.hide();
                $md.html(marked(text.substring("@markdown".length)));
                $ele.data('md-element', $md);
                $ele.data('isMarkdown', true);
            } else {
                $ele.data('isMarkdown', false);
            }
        });

        $(document).on('click', 'a[data-markdown-id]', function (e) {
            toggleMarkdown($(this).attr('data-markdown-id'));
            return false;
        });
    }

    shingetsu.addScriptPath('contrib/marked.min.js', onload);
    shingetsu.addRecordsModifiers(addLink);
});
