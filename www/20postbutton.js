// Post button controller.
// Copyright (c) 2025 shinGETsu Project.

shingetsu.initialize(function() {
    const form = document.querySelector('#postarticle');
    if (!form) {
        return;
    }
    form.addEventListener('submit', function () {
        const button = form.querySelector('button');
        if (button) {
            button.disabled = true;
            setTimeout(function () {
                button.disabled = false;
            }, 1000);
        }
        return true;
    });
});
