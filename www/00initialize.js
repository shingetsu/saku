/* Initializer.
 * Copyright (C) 2010 shinGETsu Project.
 *
 * addScriptPath came from
 * http://temping-amagramer.blogspot.jp/2012/02/jqueryjavascriptscript.html
 */

const shingetsu = (function () {
    const _initializer = [];
    const _recordsModifiers = [];

    const shingetsu = {
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
        const sep = (path.indexOf('?') > 0) ? '&' : '?';
        const realPath = shingetsu.rootPath + path + sep + shingetsu.dummyQuery;

        const script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = realPath;
        script.addEventListener('load', function() {
            onload();
        });
    };

    shingetsu.modifyRecords = function (container) {
        for (let i = 0; i < _recordsModifiers.length; i++) {
            if (shingetsu.debugMode) {
               _recordsModifiers[i](container);
               continue;
            }
            try {
               _recordsModifiers[i](container);
            } catch (e) {
                shingetsu.log(e);
            }
        }
    };

    const _initialize = function () {
        for (let i = 0; i < _initializer.length; i++) {
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
        shingetsu.modifyRecords(document);
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', _initialize);
    } else {
        _initialize();
    }

    return shingetsu;
})();
