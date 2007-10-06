/* Localtime of User Agent.
 * Copyright (C) 2006 shinGETsu Project.
 * $Id$
 */

initFunc[initFunc.length] = function () {
    function format(n) {
        if (n < 10) {
            return '0' + n;
        } else {
            return n;
        }
    }

    function myLocaltime(date) {
        var year = date.getYear();
        if (year < 1900) year += 1900;
        var month = format(date.getMonth()+1);
        var day = format(date.getDate());
        var hours = format(date.getHours());
        var minutes = format(date.getMinutes());
        return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes;
    }

    var span = document.getElementsByTagName('span');
    for (var i=0; i<span.length; i++) {
        if ((span[i].className == 'stamp') &&
            (span[i].id.search(/^s([0-9]+)$/) == 0)) {
            var stamp = RegExp.$1;
            var date = new Date();
            date.setTime(stamp*1000);
            span[i].innerHTML = myLocaltime(date);
        }
    }
};
