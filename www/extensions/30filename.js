///thread.cgi add thread file name.
//please click thread file size display. (ex, 0.0MB).
//license: http://www.kmonos.net/nysl/ or public domain. (dual license).

shingetsu.initialize(function () {
    function add_filename() {
        var filename = $('#postarticle input[name=file]').val();
        if (! filename) {
            return;
        }

        var span = $('<span>');
        span.text(' ' + filename);
        span.hide();

        var mb = $('#status');
        mb.append(span);
        mb.click(function () { span.toggle(); });
    }

    if (location.pathname.match(/\/thread\.cgi\//)) {
        add_filename();
    }
});
