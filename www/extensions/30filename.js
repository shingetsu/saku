///thread.cgi add thread file name.
//please click thread file size display. (ex, 0.0MB).
//license: http://www.kmonos.net/nysl/ or public domain. (dual license).

shingetsu.addInitializer(function () {
    function add_filename() {
        var file = document.getElementsByTagName('input')[1];
        var span = document.createElement('span');
        span.innerHTML = ' ' + file.value;
        var ps = document.getElementsByTagName('p');
        var mb = ps[ps.length - 2];
        if (mb.attachEvent) {
            mb.attachEvent('onclick', on_filename);
        } else {
            mb.addEventListener('click', on_filename, false);
        }
        mb.appendChild(span);
        span.style.display = 'none';
    }

    function on_filename() {
        var spans = document.getElementsByTagName('span');
        var span = spans[spans.length - 1];
        if (span.style.display == 'none') {
            //p.style.display = 'block'; 
            span.style.display = 'inline'; 
        } else {
            span.style.display = 'none';
        }
    }

    if (location.pathname.match(/\/thread\.cgi\//)) {
        add_filename();
    }
});
