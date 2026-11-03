/**
 * Text Area Controller.
 * Copyright (C) 2006 shinGETsu Project.
 */

shingetsu.initialize(() => {
    let msgSpread = 'Spread';
    let msgReduce = 'Reduce';
    let msgPreview = 'Preview';
    let msgEdit = 'Edit';
    if (shingetsu.uiLang === 'ja') {
        msgSpread = '拡大';
        msgReduce = '縮小';
        msgPreview = 'プレビュー';
        msgEdit = '編集再開';
    }

    const textArea = document.querySelector('textarea#body');
    if (!textArea) return;

    const buttonContainer = document.createElement('div');
    textArea.before(buttonContainer);
    buttonContainer.classList.add('post-advanced');

    class TextAreaController {
        constructor(textArea, button) {
            this._textArea = textArea;
            this._button = button;
            this._isBigSize = false;
        }

        toggle(event) {
            event.preventDefault();
            if (this._isBigSize) {
                this._reduce();
            } else {
                this._spread();
            }
        }

        _spread() {
            this._textArea.setAttribute('rows', '30');
            this._button.textContent = msgReduce;
            this._isBigSize = true;
        }

        _reduce() {
            this._textArea.setAttribute('rows', '7');
            this._button.textContent = msgSpread;
            this._isBigSize = false;
        }
    }

    const escapeHtml = (str) => {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    };

    const htmlFormat = (message) => {
        const match = location.href.match(/(.*?\/thread\.cgi\/[^\/]+)/);
        if (!match) return;

        const threadUri = escapeHtml(match[1]);
        let formatted = escapeHtml(message);

        formatted = formatted.replace(
            /(https?:..[^\x00-\x20"'()<>\[\]\x7F-\xFF]*)/g,
            '<a href="$1">$1</a>'
        );

        formatted = formatted.replace(
            /&gt;&gt;([0-9a-f]{8})/g,
            `<a class="reclink" href="${threadUri}/$1">&gt;&gt;$1</a>`
        );

        formatted = formatted.replace(
            /\[\[([^/<>\[\]]+)\]\]/g,
            (match, p1) => `<a href="/thread.cgi/${encodeURIComponent(p1)}">[[${p1}]]</a>`
        );

        formatted = formatted.replace(
            /\[\[([^/<>\[\]]+)\/([0-9a-f]{8})\]\]/g,
            (match, p1, p2) => `<a class="reclink" href="/thread.cgi/${encodeURIComponent(p1)}/${p2}">[[${p1}/${p2}]]</a>`
        );

        return formatted;
    };

    class PreviewController {
        constructor(textArea, previewArea, button, textAreaFriends) {
            this._textArea = textArea;
            this._previewArea = previewArea;
            this._textAreaFriends = textAreaFriends;
            this._button = button;
            this._isPreview = false;
        }

        toggle(event) {
            event.preventDefault();
            if (this._isPreview) {
                this._hide();
            } else {
                this._show();
            }
        }

        _show() {
            this._textAreaFriends.forEach((v) => {
                if (v) v.style.display = 'none';
            });
            this._textArea.style.display = 'none';

            const message = htmlFormat(this._textArea.value);
            this._previewArea.style.whiteSpace = 'pre';
            this._previewArea.innerHTML = message;

            if (shingetsu.plugins?.rootResAnchor?.parseContent) {
                shingetsu.plugins.rootResAnchor.parseContent(this._previewArea);
            }

            this._previewArea.style.display = '';
            this._button.textContent = msgEdit;
            this._isPreview = true;
        }

        _hide() {
            this._textAreaFriends.forEach((v) => {
                if (v) v.style.display = '';
            });
            this._textArea.style.display = '';
            this._previewArea.style.display = 'none';
            this._button.textContent = msgPreview;
            this._isPreview = false;
        }
    }

    const sizeButton = document.createElement('button');
    sizeButton.textContent = msgSpread;
    sizeButton.classList.add('btn');
    buttonContainer.appendChild(sizeButton);

    const previewButton = document.createElement('button');
    previewButton.textContent = msgPreview;
    previewButton.classList.add('btn');
    buttonContainer.appendChild(previewButton);

    const previewArea = document.createElement('pre');
    previewArea.style.display = 'none';
    previewArea.id = 'preview';
    buttonContainer.after(previewArea);

    const textAreaController = new TextAreaController(textArea, sizeButton);
    sizeButton.addEventListener('click', (e) => textAreaController.toggle(e));

    const textAreaFriends = [document.querySelector('#resreferrer')];
    const previewController = new PreviewController(textArea, previewArea, previewButton, textAreaFriends);
    previewButton.addEventListener('click', (e) => previewController.toggle(e));
});
