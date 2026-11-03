/**
 * Initializer.
 * Copyright (C) 2010 shinGETsu Project.
 *
 * addScriptPath came from
 * http://temping-amagramer.blogspot.jp/2012/02/jqueryjavascriptscript.html
 */

const shingetsu = (() => {
    const initializers = [];
    const recordsModifiers = [];

    const instance = {
        debugMode: false,
        plugins: {},
        rootPath: '/',
        dummyQuery: '',
        uiLang: 'en'
    };

    instance.log = (arg) => {
        if (typeof console === 'object' && typeof console.log === 'function') {
            console.log(arg);
        } else if (instance.debugMode) {
            alert(arg);
        }
    };

    instance.initialize = (func) => {
        if (typeof func === 'function') {
            initializers.push(func);
        }
    };
    instance.addInitializer = instance.initialize;

    instance.addRecordsModifiers = (func) => {
        if (typeof func === 'function') {
            recordsModifiers.push(func);
        }
    };

    instance.addScriptPath = (path, onload = () => {}) => {
        const sep = path.includes('?') ? '&' : '?';
        const realPath = instance.rootPath + path + sep + instance.dummyQuery;

        const script = document.createElement('script');
        script.src = realPath;
        script.onload = onload;
        document.head.appendChild(script);
    };

    instance.modifyRecords = (container = document) => {
        for (const modifier of recordsModifiers) {
            if (instance.debugMode) {
                modifier(container);
                continue;
            }
            try {
                modifier(container);
            } catch (e) {
                instance.log(e);
            }
        }
    };

    const runInitializers = () => {
        for (const init of initializers) {
            if (instance.debugMode) {
                init();
                continue;
            }
            try {
                init();
            } catch (e) {
                instance.log(e);
            }
        }
        instance.modifyRecords(document);
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runInitializers, { once: true });
    } else {
        runInitializers();
    }

    return instance;
})();
