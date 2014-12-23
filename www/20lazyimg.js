/*
 * Load jQuery Lazy
 * Copyright (C) 2014 shinGETsu Project.
 */

shingetsu.initialize(function () {
    function applyLazy($container) {
        $container.find("img[data-lazyimg]").lazy({
            effect: 'fadeIn',
            effectTime: 500
        });

        if ($container.hasClass('popup')) {
            $container.find("img[data-lazyimg]").each(function (i, e) {
                $(e).attr('src', $(e).attr('data-src'))
                    .removeAttr('data-lazyimg')
                    .removeAttr('data-src');
            });
        }
    }

    shingetsu.addRecordsModifiers(applyLazy);
});
