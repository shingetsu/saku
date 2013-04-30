/* -*- coding: utf-8 -*-
 * image spoiler-alert.
 * licenced by public domain.
 */

shingetsu.initialize(function () {
    if ($.browser.msie) {
        return;
    }

    function onload(){
        $('#records').find('img').spoilerAlert({max: 10, partial: 2});
    }

    shingetsu.addScriptPath('jquery/spoiler/spoiler.min.js', onload);
});
