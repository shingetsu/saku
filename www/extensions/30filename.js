///thread.cgi add thread file name.
//please click thread file size display. (ex, 0.0MB).
//license: http://www.kmonos.net/nysl/ or public domain. (dual license).

shingetsu.initialize(() => {
    function add_filename() {
        const fileInput = document.querySelector('#postarticle input[name="file"]');
        if (!fileInput || !fileInput.value) {
            return;
        }

        const filename = fileInput.value;
        const span = document.createElement('span');
        span.textContent = ' ' + filename;
        span.style.display = 'none';

        const mb = document.getElementById('status');
        if (mb) {
            mb.appendChild(span);
            mb.addEventListener('click', () => {
                // 表示状態をトグルする（none なら空文字＝表示、block等なら非表示）
                span.style.display = span.style.display === 'none' ? 'inline' : 'none';
            });
        }
    }

    if (/\/thread\.cgi\//.test(location.pathname)) {
        add_filename();
    }
});
