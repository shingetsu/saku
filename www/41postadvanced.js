/**
 * Advanced form inputs.
 * Copyright (C) 2012 shinGETsu Project.
 */

shingetsu.initialize(() => {
    let msgShow = 'Show detail';
    let msgHide = 'Hide detail';
    if (shingetsu.uiLang === 'ja') {
        msgShow = '詳細を表示';
        msgHide = '詳細を隠す';
    }

    class Controller {
        constructor(inputs, button) {
            this._inputs = inputs;
            this._button = button;
            this._isShowing = false;
        }

        toggle(event) {
            event.preventDefault();
            if (this._isShowing) {
                this.hide('fast');
            } else {
                this.show('fast');
            }
        }

        _forEachInput(callback) {
            if (!this._inputs) return;
            if (this._inputs instanceof NodeList || Array.isArray(this._inputs)) {
                this._inputs.forEach(callback);
            } else {
                callback(this._inputs);
            }
        }

        _getDuration(speed) {
            if (speed === 'fast') return 200;
            if (speed === 'slow') return 600;
            return 400;
        }

        hide(speed) {
            const duration = this._getDuration(speed);

            this._forEachInput((el) => {
                if (el?.nodeType === 1) {
                    const animation = el.animate([
                        { opacity: 1 },
                        { opacity: 0 }
                    ], { duration, easing: 'ease' });

                    animation.onfinish = () => {
                        el.style.display = 'none';
                    };
                }
            });

            this._isShowing = false;
            if (this._button) {
                this._button.textContent = msgShow;
            }
        }

        show(speed) {
            const duration = this._getDuration(speed);

            this._forEachInput((el) => {
                if (el?.nodeType === 1) {
                    el.style.display = '';
                    el.animate([
                        { opacity: 0 },
                        { opacity: 1 }
                    ], { duration, easing: 'ease' });
                }
            });

            this._isShowing = true;
            if (this._button) {
                this._button.textContent = msgHide;
            }
        }
    }

    const form = document.querySelector('#postarticle');
    if (!form) return;

    const buttonsContainer = form.querySelector('#buttons');
    if (!buttonsContainer) return;

    const button = document.createElement('button');
    button.classList.add('btn');
    buttonsContainer.appendChild(button);

    const inputs = form.querySelectorAll('.post-advanced');
    const controller = new Controller(inputs, button);

    button.addEventListener('click', (e) => controller.toggle(e));

    controller.hide(0);
});
