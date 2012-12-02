/* Localtime of User Agent.
 * Copyright (C) 2006,2010 shinGETsu Project.
 * $Id: 20localtime.js 1501 2010-12-12 05:45:40Z fuktommy $
 */

shingetsu.addInitializer(function () {
    function format(n) {
        if (n < 10) {
            return '0' + n;
        } else {
            return n;
        }
    }

    var tblE = new Array('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
    var tblJ = new Array('\u65e5','\u6708','\u706b','\u6c34','\u6728','\u91d1','\u571f');
    var tbl = new Array(' ',' ',' ',' ',' ',' ',' ');
    if (location.pathname.match(/\/thread\.cgi\/.*/)) {
        for (var i=0; i<7; i++){
            if (shingetsu.uiLang == 'ja') {
                tbl[i] = '(' + tblJ[i] + ')';
            } else {
                tbl[i] = '(' + tblE[i] + ')';
            }
        }
    }

    var span = document.getElementsByTagName('span');
    for (var i=0; i<span.length; i++) {
        if ((span[i].className == 'stamp') &&
            (span[i].id.search(/^s([0-9]+)$/) == 0)) {
            var stamp = RegExp.$1;
            var date = new Date();
            date.setTime(stamp*1000);

            var year = date.getYear();
            if (year < 1900) year += 1900;
            var month = format(date.getMonth()+1);
            var day = format(date.getDate());
            var hours = format(date.getHours());
            var minutes = format(date.getMinutes());

            span[i].innerHTML = year + '-' + month + '-' + day + tbl[date.getDay()]
                                 + hours + ":" + minutes;
        }
    }
});
