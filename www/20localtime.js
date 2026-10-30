// Localtime of User Agent.
// Copyright (c) 2006 shinGETsu Project.

shingetsu.initialize(function () {
    function format(n) {
        return ('0' + n).substr(-2);
    }

    function myLocaltime(date) {
        let year = date.getYear();
        if (year < 1900) year += 1900;
        const month = format(date.getMonth()+1);
        const day = format(date.getDate());
        const hours = format(date.getHours());
        const minutes = format(date.getMinutes());
        return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes;
    }

    function overrideDatetime(container) {
        const elements = container.querySelectorAll('span.stamp[data-stamp]');
        elements.forEach(function(el) {
            const stamp = el.getAttribute('data-stamp');
            if (stamp === "0" || stamp === 0) {
                el.innerHTML = '0000-00-00 00:00';
            } else {
                const date = new Date();
                date.setTime(Number(stamp) * 1000);
                el.innerHTML = myLocaltime(date);
            }
        });
    }

    shingetsu.addRecordsModifiers(overrideDatetime);
});
