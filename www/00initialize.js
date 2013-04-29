/* Initializer.
 * Copyright (C) 2010-2013 shinGETsu Project.
 *
 * addScriptPath came from
 * http://temping-amagramer.blogspot.jp/2012/02/jqueryjavascriptscript.html
 */

var shingetsu = (function () {
    var _initializer = [];

    var shingetsu = {
        debugMode: false,
        plugins: {},
        rootPath: '/',
        dummyQuery: '',
        uiLang: 'en'
    };

    shingetsu.log = function (arg) {
        if (typeof console == 'object') {
            console.log(arg);
        } else if (shingetsu.debugMode) {
            alert(arg);
        }
    };

    shingetsu.initialize = function (func) {
        _initializer[_initializer.length] = func;
    };
    shingetsu.addInitializer = shingetsu.initialize;

    shingetsu.addScriptPath = function (path, onload) {
        if (typeof onload != 'function') {
            onload = function() {};
        }
        var sep = (path.indexOf('?') > 0) ? '&' : '?';
        var realPath = shingetsu.rootPath + path + sep + shingetsu.dummyQuery;
        var script = document.createElement('script');
        script.setAttribute('type', 'text/javascript');
        script.setAttribute('src', realPath);
        if ($.browser.msie) {
            script.onreadystatechange = function() {
                if (script.readyState == 'complete'
                    || script.readyState == 'loaded') {
                    onload();
                }
            };
        } else {
            script.onload = function() {
                onload();
            };
        }
        document.getElementsByTagName('head')[0].appendChild(script);
    };

    var _initialize = function () {
        for (var i=0; i < _initializer.length; i++) {
            if (shingetsu.debugMode) {
               _initializer[i]();
               continue;
            }
            try {
               _initializer[i]();
            } catch (e) {
                shingetsu.log(e);
            }
        }
    };

    $(_initialize);

    return shingetsu;
})();
