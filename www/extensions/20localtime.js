/* Localtime of User Agent.
 * Copyright (C) 2006-2014 shinGETsu Project.
 */

shingetsu.initialize(() => {
    function format(n) {
        return ('0' + n).slice(-2);
    }

    const tblE = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const tblJ = ['\u65e5', '\u6708', '\u706b', '\u6c34', '\u6728', '\u91d1', '\u571f'];
    const tbl = [' ', ' ', ' ', ' ', ' ', ' ', ' '];

    if (location.pathname.match(/\/thread\.cgi\/.*/)) {
        for (let i = 0; i < 7; i++) {
            if (shingetsu.uiLang === 'ja') {
                tbl[i] = '(' + tblJ[i] + ')';
            } else {
                tbl[i] = '(' + tblE[i] + ')';
            }
        }
    }

    function myLocaltime(date) {
        const year = date.getFullYear();
        const month = format(date.getMonth() + 1);
        const day = format(date.getDate());
        const hours = format(date.getHours());
        const minutes = format(date.getMinutes());
        return year + '-' + month + '-' + day + ' ' + tbl[date.getDay()] + ' ' + hours + ':' + minutes;
    }

    function overrideDatetime(container) {
        const stamps = container.querySelectorAll('span.stamp[data-stamp]');
        stamps.forEach((el) => {
            const stamp = el.getAttribute('data-stamp');
            const date = new Date(stamp * 1000);
            el.textContent = myLocaltime(date);
        });
    }

    shingetsu.addRecordsModifiers(overrideDatetime);
});
