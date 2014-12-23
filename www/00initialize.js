/* Initializer.
 * Copyright (C) 2010-2014 shinGETsu Project.
 *
 * addScriptPath came from
 * http://temping-amagramer.blogspot.jp/2012/02/jqueryjavascriptscript.html
 */

var shingetsu = (function () {
    var _initializer = [];
    var _recordsModifiers = [];

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

    shingetsu.addRecordsModifiers = function (func) {
        _recordsModifiers[_recordsModifiers.length] = func;
    };

    shingetsu.addScriptPath = function (path, onload) {
        if (typeof onload != 'function') {
            onload = function() {};
        }
        var sep = (path.indexOf('?') > 0) ? '&' : '?';
        var realPath = shingetsu.rootPath + path + sep + shingetsu.dummyQuery;
        var script = $('<script>');
        script.attr('type', 'text/javascript')
              .attr('src', realPath)
              .on('load', function() { onload(); });
        document.getElementsByTagName('head')[0].appendChild(script[0]);
    };

    shingetsu.modifyRecords = function ($container) {
        for (var i = 0; i < _recordsModifiers.length; i++) {
            if (shingetsu.debugMode) {
               _recordsModifiers[i]($container);
               continue;
            }
            try {
               _recordsModifiers[i]($container);
            } catch (e) {
                shingetsu.log(e);
            }
        }
    };

    var _initialize = function () {
        for (var i = 0; i < _initializer.length; i++) {
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
        shingetsu.modifyRecords($(document));
    };

    $(_initialize);

    return shingetsu;
})();
