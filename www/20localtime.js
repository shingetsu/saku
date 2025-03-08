// Localtime of User Agent.
// Copyright (C) 2006 shinGETsu Project.

shingetsu.initialize(function () {
    function format(n) {
        return ('0' + n).substr(-2);
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

    function overrideDatetime($container) {
        $container.find('span.stamp[data-stamp]').each(function() {
            var container = $(this);
            var stamp = container.attr('data-stamp');
            if (stamp == 0) {
                container.html('0000-00-00 00:00');
            } else {
                var date = new Date();
                date.setTime(container.attr('data-stamp') * 1000);
                container.html(myLocaltime(date));
            }
        });
    }

    shingetsu.addRecordsModifiers(overrideDatetime);
});
