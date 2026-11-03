/* -*- coding: utf-8 -*-
 * markdown extension
 * https://github.com/WhiteCat6142/shingetsu-extensons
 */

shingetsu.initialize(() => {

    const msgMarkdown = '[MD]';

    function addLink(container) {
        const dts = container.querySelectorAll('dt');
        dts.forEach((dt) => {
            if (dt.hasAttribute('data-record-id')) {
                const existingAnchor = dt.querySelector('a[data-markdown-id]');
                if (existingAnchor) {
                    existingAnchor.remove();
                }

                const id = dt.getAttribute('data-record-id');
                const anchor = document.createElement('a');
                anchor.href = 'javascript:;';
                anchor.textContent = msgMarkdown;
                anchor.setAttribute('data-markdown-id', id);
                dt.appendChild(anchor);
            }
        });
    }

    function showMarkdown(dd) {
        let md = dd._mdElement;
        if (!md) {
            const text = dd.textContent;
            md = document.createElement('dd');
            md.className = 'markdown';
            dd.after(md);

            if (text.indexOf('@markdown') === 0) {
                md.innerHTML = marked(text.substring('@markdown'.length));
            } else {
                md.innerHTML = marked(text);
            }

            const img = dd.querySelector('img');
            if (img) {
                md.appendChild(img.cloneNode(true));
            }
            dd._mdElement = md;
        }
        dd.style.display = 'none';
        md.style.display = '';
        dd.dataset.isMarkdown = 'true';
    }

    function toggleMarkdown(id) {
        const dd = document.getElementById('b' + id);
        if (!dd) {
            return;
        }
        if (dd.dataset.isMarkdown === 'true') {
            if (dd._mdElement) {
                dd._mdElement.style.display = 'none';
            }
            dd.style.display = '';
            dd.dataset.isMarkdown = 'false';
        } else {
            showMarkdown(dd);
        }
    }

    function onload() {
        const dds = document.querySelectorAll('dd');
        dds.forEach((ele) => {
            ele._mdElement = null;
            const text = ele.textContent;
            if (text.indexOf('@markdown') === 0) {
                showMarkdown(ele);
            } else {
                ele.dataset.isMarkdown = 'false';
            }
        });

        document.addEventListener('click', (e) => {
            const anchor = e.target.closest('a[data-markdown-id]');
            if (anchor) {
                e.preventDefault();
                const id = anchor.getAttribute('data-markdown-id');
                toggleMarkdown(id);
            }
        });
    }

    shingetsu.addScriptPath('contrib/marked.min.js', onload);
    shingetsu.addRecordsModifiers(addLink);
});
