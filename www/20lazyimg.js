/*
 * Load jQuery Lazy
 * Copyright (C) 2014 shinGETsu Project.
 */

shingetsu.initialize(function () {
    $("img[data-lazyimg]").lazy({
        effect: "fadeIn",
        effectTime: 500
    });
});
