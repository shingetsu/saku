/* Initializer.
 * Copyright (C) 2010 shinGETsu Project.
 * $Id$
 */

var shingetsu = (function () {
    var _initializer = [];

    var shingetsu = {
        debugMode: false,
        plugins: {},
        uiLang: 'en'
    };

    shingetsu.log = function (arg) {
        if (! shingetsu.debugMode) {
            return;
        } else if (typeof console == 'object') {
            console.log(arg);
        } else {
            alert(arg);
        }
    };

    shingetsu.addInitializer = function (func) {
        _initializer[_initializer.length] = func;
    };

    var _initialize = function () {
        for (var i=0; i < _initializer.length; i++) {
            if (shingetsu.debugMode) {
               _initializer[i]();
            } else {
                try {
                   _initializer[i]();
                } catch (e) {
                    shingetsu.log(e);
                }
            }
        }
    };

    if (document.addEventListener) {
        document.addEventListener('DOMContentLoaded',
                                  _initialize, false);
    } else if (window.attachEvent) {
        window.attachEvent('onload', _initialize);
    } else {
        window.onload = _initialize;
    }

    return shingetsu;
})();
