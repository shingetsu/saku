// save "name", "mail", "signature", "desc_send", "error" in post form.
// original by Anonymous in shinGETsu.
// improved by shiroboushi.
// licenced by public domain.

shingetsu.initialize(function() {
    const saved = parse(localStorage.getItem('recform'));
    if (saved) {
        load(saved);
    }

    function load(saved) {
        const fields = {
            '#postarticle #dopost': 'dopost',
            '#error': 'error'
        };
        for (const [selector, key] of Object.entries(fields)) {
            const el = document.querySelector(selector);
            if (el) el.checked = !!saved[key];
        }

        const inputs = {
            '#name': 'name',
            '#mail': 'mail',
            '#passwd': 'passwd'
        };
        for (const [selector, key] of Object.entries(inputs)) {
            const el = document.querySelector(selector);
            if (el) el.value = saved[key] ?? '';
        }

        document.querySelectorAll('#postarticle .post-advanced').forEach(element => {
            const hasName = saved.name && element.querySelector('#name');
            const hasMail = saved.mail && element.querySelector('#mail');
            const hasPasswd = saved.passwd && element.querySelector('#passwd');
            const hasUnchecked = element.querySelector('input[type="checkbox"]:not(:checked)');

            if (hasName || hasMail || hasPasswd || hasUnchecked) {
                element.classList.remove('post-advanced');
            }
        });
    }

    function parse(saved) {
        try {
            return JSON.parse(saved);
        } catch (e) {
            return null;
        }
    }

    function save() {
        const item = {};
        const form = document.querySelector('#postarticle');

        if (!form) return;

        item.name = form.querySelector('[name="name"]')?.value || '';
        item.mail = form.querySelector('[name="mail"]')?.value || '';
        item.passwd = form.querySelector('[name="passwd"]')?.value || '';
        item.dopost = form.querySelector('[name="dopost"]')?.checked || false;
        item.error = form.querySelector('[name="error"]')?.checked || false;

        localStorage.setItem('recform', JSON.stringify(item));
    }

    const p = document.querySelector('#postarticle');
    if (!p) return;
    p.addEventListener('submit', save);
});
