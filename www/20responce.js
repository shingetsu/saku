/* -*- coding: utf-8 -*-
 * Response Post.
 * Copyright (C) 2006,2010 shinGETsu Project.
 * $Id$
 */

shingetsu.addInitializer(function () {
    function res(id) {
        var form = document.getElementById('postarticle');
        if (form) {
            if (form.body.value) {
                form.body.value += '\n>>' + id + '\n';
            } else {
                form.body.value = '>>' + id + '\n';
            }
            var p = form.getElementsByTagName('p')[0];
            var ref = document.getElementById('resreferrer');
            if (ref.innerHTML == '') {
                var br = document.createElement('br');
                p.insertBefore(br, form.body);
            }
            var span = document.createElement('span');
            var e = document.all? 'null': 'event';
            span.innerHTML = ' <a href="#r' + id + '"'
                           + ' onmouseover="shingetsu.plugins.popupAnchor('
                           + e +', \'' + id + '\');"'
                           + ' onmouseout="shingetsu.plugins.hidePopup()">'
                           + '&gt;&gt;' + id + '</a>';
            ref.appendChild(span);
            form.body.focus();
        }
    }

    var form = document.getElementById('postarticle');
    if (! form) {
        return;
    }
    var msg_res = 'Res.';
    if (shingetsu.uiLang == 'ja') {
        msg_res = '返信';
    }
    var dts = document.getElementsByTagName('dt');
    for (var i=0; i<dts.length; i++) {
        var a = document.createElement('a');
        a.href = 'javascript:;';
        a.innerHTML = '[' + msg_res + ']';
        if (a.addEventListener) {
            a.addEventListener(
                'click',
                (function (id) {
                    return function (e) {res(id);}
                })(dts[i].id.substr(1)),
                false);
        } else if (a.attachEvent) {
            a.attachEvent(
                'onclick',
                (function (id) {
                    return function (e) {res(id);}
                })(dts[i].id.substr(1)));
        }
        dts[i].appendChild(a);
    }
    var p = form.getElementsByTagName('p')[0];
    var ref = document.createElement('span');
    ref.id = 'resreferrer';
    p.insertBefore(ref, form.body);
});
