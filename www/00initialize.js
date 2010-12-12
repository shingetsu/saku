/* Initializer.
 * Copyright (C) 2010 shinGETsu Project.
 * $Id$
 */

shingetsu._initializer = [];
shingetsu.plugins = {};


shingetsu.log = function (arg) {
    if (console) {
        console.log(arg);
    }
}


shingetsu.addInitializer = function (func) {
    shingetsu._initializer[shingetsu._initializer.length] = func;
};


shingetsu._initialize = function () {
    for (var i=0; i < shingetsu._initializer.length; i++) {
        try {
            shingetsu._initializer[i]();
        } catch (e) {
            shingetsu.log(e);
        }
    }
};


(function() {
    if(document.addEventListener) {
        document.addEventListener('DOMContentLoaded',
                                  shingetsu._initialize, false);
    } else if (window.attachEvent) {
        window.attachEvent('onload', shingetsu._initialize);
	} else {
		window.onload = shingetsu._initialize;
	}
})();
