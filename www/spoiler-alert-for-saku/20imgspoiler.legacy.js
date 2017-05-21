/* -*- coding: utf-8 -*-
 * image spoiler-alert.
 * licenced by public domain.
 */


shingetsu.addInitializer(function () {
    $('#records').find('img').spoilerAlert({max: 10, partial: 2});
});