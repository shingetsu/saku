/**
 * Response Post.
 * Copyright (C) 2006 shinGETsu Project.
 */

shingetsu.initialize(() => {
    const msgRes = shingetsu.uiLang === 'ja' ? '[返信]' : '[Res.]';

    const res = (id) => {
        const textArea = document.getElementById('body');
        if (!textArea) return;

        const appendText = `>>${id}\n`;
        textArea.value = textArea.value ? textArea.value + appendText : appendText;

        const anchor = document.createElement('a');
        anchor.textContent = `>>${id}`;

        const records = document.getElementById('records');
        if (records && records.querySelector(`#r${id}`)) {
            anchor.setAttribute('href', `#r${id}`);
            anchor.classList.add('innerlink');
        } else {
            const match = location.href.match(/(.+\/thread\.cgi\/[^\/]*)/);
            if (match && match[1]) {
                anchor.setAttribute('href', `${match[1]}/${id}`);
                anchor.classList.add('reclink');
            }
        }

        const resreferrer = document.getElementById('resreferrer');
        if (resreferrer) {
            resreferrer.appendChild(anchor);
            if (shingetsu.plugins?.rootResAnchor?.parseContent) {
                shingetsu.plugins.rootResAnchor.parseContent(resreferrer);
            }
        }

        textArea.focus();
    };

    const addLink = (container) => {
        const elContainer = container instanceof HTMLElement ? container : container?.[0];
        if (!elContainer) return;

        const dts = elContainer.querySelectorAll('dt');
        dts.forEach((dt) => {
            const recordId = dt.getAttribute('data-record-id');
            if (recordId) {
                const existingAnchor = dt.querySelector('a[data-responce-id]');
                if (existingAnchor) {
                    existingAnchor.remove();
                }

                const anchor = document.createElement('a');
                anchor.href = 'javascript:;';
                anchor.textContent = msgRes;
                anchor.dataset.responceId = recordId;

                dt.appendChild(anchor);
            }
        });
    };

    const ref = document.createElement('div');
    ref.id = 'resreferrer';

    const bodyElem = document.getElementById('body');
    if (bodyElem?.parentNode) {
        bodyElem.parentNode.insertBefore(ref, bodyElem);
    }

    shingetsu.addRecordsModifiers(addLink);

    document.addEventListener('click', (e) => {
        const anchor = e.target.closest('a[data-responce-id]');
        if (anchor) {
            e.preventDefault();
            const responseId = anchor.dataset.responceId;
            if (responseId) {
                res(responseId);
            }
        }
    });
});
