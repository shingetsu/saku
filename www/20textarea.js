/* -*- coding: utf-8 -*-
 * Text Area Conttoller.
 * Copyright (C) 2006-2012 shinGETsu Project.
 */

shingetsu.initialize(function () {
    var msg_spread = 'Spread';
    var msg_reduce = 'Reduce';
    var msg_preview = 'Preview';
    var msg_edit = 'Edit';
    if (shingetsu.uiLang == 'ja') {
        msg_spread = '拡大';
        msg_reduce = '縮小';
        msg_preview = 'プレビュー';
        msg_edit = '編集再開';
    }

    var textArea = $('#body');
    var textAreaContainer = textArea.parent();
    var buttonContainer = $('<div>');
    textArea.before(buttonContainer);
    buttonContainer.addClass('post-advanced');

    function TextAreaController(textArea, button) {
        this._textArea = textArea;
        this._button = button;
        this._isBigSize = false;
    }

    TextAreaController.prototype.toggle = function (event) {
        event.preventDefault();
        if (this._isBigSize) {
            this._reduce();
        } else {
            this._spread();
        }
    };

    TextAreaController.prototype._spread = function () {
        this._textArea.attr('rows', 30).css('width', '90%');
        this._button.text(msg_reduce);
        this._isBigSize = true;
    };

    TextAreaController.prototype._reduce = function () {
        this._textArea.attr('rows', 7).css('width', '');
        this._button.text(msg_spread);
        this._isBigSize = false;
    };

    var sizeButton = $('<button>');
    buttonContainer.append(sizeButton);
    sizeButton.text(msg_spread).addClass('btn');
    

    var textAreaController = new TextAreaController(textArea, sizeButton);
    sizeButton.click(function (e) { textAreaController.toggle(e) } );


    function html_format(message) {
        var e = document.all? 'null': 'event';
        message = message.replace(/&/g, '&amp;');
        message = message.replace(/</g, '&lt;');
        message = message.replace(/>/g, '&gt;');
        message = message.replace(/&gt;&gt;([0-9a-f]{8})/g,
            '<a href="#r$1"' +
            ' onmouseover="shingetsu.plugins.popupAnchor(' + e +', \'$1\');"' +
            ' onmouseout="shingetsu.plugins.hidePopup();"' +
            '>&gt;&gt;$1</a>');
        message = message.replace(
            /(https?:..[^\x00-\x20"'()<>\[\]\x7F-\xFF]*)/g,
            '<a href="$1">$1</a>');
        message = message.replace(
            /\[\[([^/<>\[\]]+)\]\]/g,
            function ($0, $1) {
                return '<a href="/thread.cgi/' + encodeURIComponent($1) +
                       '">[[' + $1 + ']]</a>';
            });
        message = message.replace(
            /\[\[([^/<>\[\]]+)\/([0-9a-f]{8})\]\]/g,
            function ($0, $1, $2) {
                return '<a href="/thread.cgi/' + encodeURIComponent($1) +
                       '/' + $2 +
                       '">[[' + $1 + '/' + $2 + ']]</a>';
            });
        return message;
    }


    function PreviewController(textArea, previewArea, button, textAreaFriends) {
        this._textArea = textArea;
        this._previewArea = previewArea;
        this._textAreaFriends = textAreaFriends;
        this._button = button;
        this._isPreview = false;
    }

    PreviewController.prototype.toggle = function (event) {
        event.preventDefault();
        if (this._isPreview) {
            this._hide();
        } else {
            this._show();
        }
    };

    PreviewController.prototype._show = function () {
        $.each(this._textAreaFriends, function (i, v) { v.hide() });
        this._textArea.hide();
        var message = html_format(this._textArea.val());
        this._previewArea.html(message).show();
        console.log(this._previewArea);
        this._button.text(msg_edit);
        this._isPreview = true;
    };

    PreviewController.prototype._hide = function () {
        $.each(this._textAreaFriends, function (i, v) { v.show() });
        this._textArea.show();
        this._previewArea.hide();
        this._button.text(msg_preview);
        this._isPreview = false;
    };

    var previewButton = $('<button>');
    buttonContainer.append(previewButton);
    previewButton.text(msg_preview).addClass('btn');

    var previewArea = $('<pre>').hide();
    previewArea.id = 'preview';
    buttonContainer.after(previewArea);
    var textAreaFriends = [$('#resreferrer'), sizeButton];

    var previewController = new PreviewController(textArea, previewArea, previewButton, textAreaFriends);
    previewButton.click(function (e) { previewController.toggle(e) } );
});
