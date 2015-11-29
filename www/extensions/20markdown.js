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

    function showMarkdown($dd)
    {
        var $md = $dd.data('md-element');
        if (! $md) {
            var text = $dd.text();
            var $md = $('<dd>');
            $md.addClass('markdown');
            $md.insertAfter($dd);
            if (text.indexOf("@markdown") === 0) {
                $md.html(marked(text.substring("@markdown".length)));
            } else {
                $md.html(marked(text));
            }
            var $img = $dd.find('img');
            if ($img.length > 0) {
                $md.append($img.clone(true));
            }
            $dd.data('md-element', $md);
        }
        $dd.hide();
        $md.show();
        $dd.data('isMarkdown', true);
    }

    function toggleMarkdown(id) {
        $dd = $('#b' + id);
        if ($dd.length == 0) {
            return;
        }
        if ($dd.data('isMarkdown')) {
            $dd.data('md-element').hide();
            $dd.show();
            $dd.data('isMarkdown', false);
        } else {
            showMarkdown($dd);
        }
    }

    function onload() {
        $.each($("dd"),function(i, ele) {
            $ele = $(ele);
            $ele.data('md-element', null);
            var text = $ele.text();
            if (text.indexOf("@markdown") === 0) {
                showMarkdown($ele);
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
