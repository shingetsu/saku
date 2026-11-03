/**
 * Post button controller.
 * Copyright (c) 2025 shinGETsu Project.
 */

shingetsu.initialize(() => {
    const form = document.querySelector('#postarticle');
    if (!form) return;

    form.addEventListener('submit', () => {
        const button = form.querySelector('button');
        if (button) {
            button.disabled = true;
            setTimeout(() => {
                button.disabled = false;
            }, 1000);
        }
        return true;
    });
});
