/* -*- coding: utf-8 -*-
 * Advanced form inputs.
 * Copyright (C) 2012 shinGETsu Project.
 */

shingetsu.initialize(function () {
    let msg_show = 'Show detail';
    let msg_hide = 'Hide detail';
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

    Controller.prototype._forEachInput = function(callback) {
        if (!this._inputs) return;
        if (window.NodeList && this._inputs instanceof NodeList || Array.isArray(this._inputs)) {
            this._inputs.forEach(callback);
        } else {
            callback(this._inputs);
        }
    };

    Controller.prototype.hide = function (speed) {
        const duration = speed === 'fast' ? 200 : (speed === 'slow' ? 600 : 400);

        this._forEachInput(el => {
            if (el && el.nodeType === 1) {
                const animation = el.animate([
                    { opacity: 1 },
                    { opacity: 0 }
                ], { duration: duration, easing: 'ease' });

                animation.onfinish = () => {
                    el.style.display = 'none';
                };
            }
        });

        this._isShowing = false;
        if (this._button) {
            this._button.textContent = msg_show;
        }
    };

    Controller.prototype.show = function (speed) {
        const duration = speed === 'fast' ? 200 : (speed === 'slow' ? 600 : 400);

        this._forEachInput(el => {
            if (el && el.nodeType === 1) {
                el.style.display = '';
                el.animate([
                    { opacity: 0 },
                    { opacity: 1 }
                ], { duration: duration, easing: 'ease' });
            }
        });

        this._isShowing = true;
        if (this._button) {
            this._button.textContent = msg_hide;
        }
    };

    const form = document.querySelector('#postarticle');
    if (!form) {
        return;
    }

    const button = document.createElement('button');
    form.querySelector('#buttons').appendChild(button);

    const inputs = form.querySelectorAll('.post-advanced');
    const controller = new Controller(inputs, button);

    button.addEventListener('click', function (e) {
        controller.toggle(e);
    });

    controller.hide(0);
});
