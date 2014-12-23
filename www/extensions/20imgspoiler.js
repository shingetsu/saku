/* -*- coding: utf-8 -*-
 * image spoiler-alert.
 * licenced by public domain.
 */

shingetsu.initialize(function () {
    function onload() {
        function spoilerImages($container) {
            $container.find('img').spoilerAlert({max: 10, partial: 2});
        }
        shingetsu.addRecordsModifiers(spoilerImages);
        spoilerImages($('#records'));
    }

    shingetsu.addScriptPath('jquery/spoiler/spoiler.min.js', onload);
});
