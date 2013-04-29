/* -*- coding: utf-8 -*-
 * Advanced form inputs.
 * Copyright (C) 2012 shinGETsu Project.
 */

shingetsu.initialize(function () {
    var msg_show = 'Show detail';
    var msg_hide = 'Hide detail';
    if (shingetsu.uiLang == 'ja') {
        msg_show = '詳細を表示';
        msg_hide = '詳細を隠す';
    }

    function Controller(inputs, button) {
        this._inputs = inputs;
        this._button = button;
        this._isShowing = false;
    }

    Controller.prototype.toggle = function (event) {
        event.preventDefault();
        if (this._isShowing) {
            this.hide('fast');
        } else {
            this.show('fast');
        }
    };

    Controller.prototype.hide = function (speed) {
        this._inputs.hide(speed);
        this._isShowing = false;
        this._button.text(msg_show);
    };

    Controller.prototype.show = function (speed) {
        this._inputs.show(speed);
        this._isShowing = true;
        this._button.text(msg_hide);
    };

    var form = $('#postarticle');

    var button = $('<button>');
    button.addClass('btn');
    form.find('.form-actions').append(button);

    var inputs = form.find('.post-advanced');
    var controller = new Controller(inputs, button);
    button.click(function (e) { controller.toggle(e) } );

    controller.hide(0);
});
