/* -*- coding: utf-8 -*-
 * Response Post.
 * Copyright (C) 2006 shinGETsu Project.
 */

shingetsu.initialize(function () {
    let msg_res = '[Res.]';
    if (shingetsu.uiLang == 'ja') {
        msg_res = '[返信]';
    }

    function res(id) {
        const textArea = document.getElementById('body');
        const appendText = '>>' + id + '\n';

        if (textArea.value) {
            textArea.value += appendText;
        } else {
            textArea.value = appendText;
        }

        const anchor = document.createElement('a');
        anchor.textContent = '>>' + id;

        const records = document.getElementById('records');
        if (records && records.querySelector('#r' + id)) {
            anchor.setAttribute('href', '#r' + id);
            anchor.classList.add('innerlink');
        } else {
            const match = location.href.match(/(.+\/thread\.cgi\/[^\/]*)/);
            if (match && match[1]) {
                anchor.setAttribute('href', match[1] + '/' + id);
                anchor.classList.add('reclink');
            }
        }

        const resreferrer = document.getElementById('resreferrer');
        if (resreferrer) {
            resreferrer.appendChild(anchor);
            shingetsu.plugins.rootResAnchor.parseContent(resreferrer);
        }

        textArea.focus();
    }

    function addLink(container) {
        const elContainer = container instanceof HTMLElement ? container : container[0];
        if (!elContainer) return;

        const dts = elContainer.querySelectorAll('dt');
        dts.forEach(function (dt) {
            const recordId = dt.getAttribute('data-record-id');
            if (recordId) {
                const existingAnchor = dt.querySelector('a[data-responce-id]');
                if (existingAnchor) {
                    existingAnchor.remove();
                }

                const anchor = document.createElement('a');
                anchor.setAttribute('href', 'javascript:;');
                anchor.textContent = typeof msg_res !== 'undefined' ? msg_res : '';
                anchor.setAttribute('data-responce-id', recordId);

                dt.appendChild(anchor);
            }
        });
    }

    const ref = document.createElement('div');
    ref.id = 'resreferrer'; // または ref.setAttribute('id', 'resreferrer');

    const bodyElem = document.getElementById('body');
    if (bodyElem && bodyElem.parentNode) {
        bodyElem.parentNode.insertBefore(ref, bodyElem);
    }

    shingetsu.addRecordsModifiers(addLink);

    document.addEventListener('click', function (e) {
        const anchor = e.target.closest('a[data-responce-id]');
        if (anchor) {
            e.preventDefault();
            const responseId = anchor.getAttribute('data-responce-id');
            res(responseId);
        }
    });
});
