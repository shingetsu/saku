/* -*- coding: utf-8 -*-
 * markdown extension
 * https://github.com/WhiteCat6142/shingetsu-extensons
 */

shingetsu.initialize(function () {

    function onload() {
        $.each($("dd"),function(i,ele) {
            var t = $(ele).text();
            if (t.startsWith("@markdown")) {
                $(ele).html(marked(t.substring("@markdown".length)));
            }
        });
    }

    shingetsu.addScriptPath('contrib/marked.min.js', onload);
});
