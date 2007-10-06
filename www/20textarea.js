/* -*- coding: utf-8 -*-
  * Text Area Conttoller.
 * Copyright (C) 2006,2007 shinGETsu Project.
 * $Id$
 */

initFunc[initFunc.length] = function () {
    var form = document.getElementById('postarticle');
    if (! form) {
        return;
    }
    var msg_spread = 'Spread';
    var msg_reduce = 'Reduce';
    var msg_preview = 'Preview';
    var msg_edit = 'Edit';
    if (uiLang == 'ja') {
        msg_spread = '拡大';
        msg_reduce = '縮小';
        msg_preview = 'プレビュー';
        msg_edit = '編集再開';
    }

    function addEvent(obj, func) {
        if (obj.addEventListener) {
            obj.addEventListener('click', func, false);
        } else if (a.attachEvent) {
            obj.attachEvent('onclick', func);
        }
    }

    function removeEvent(obj, func) {
        if (obj.removeEventListener) {
            obj.removeEventListener('click', func, false);
        } else if (a.detachEvent) {
            obj.detachEvent('onclick', func);
        }
    }

    function spreadMsg() {
        form.body.rows = 30;
        form.body.style.width = '90%';
        var a = document.getElementById('textsize');
        a.innerHTML = '[' + msg_reduce + ']';
        removeEvent(a, spreadMsg);
        addEvent(a, reduceMsg);
    }

    function reduceMsg() {
        form.body.style.width = '';
        form.body.rows = 5;
        form.body.cols = 70;
        var a = document.getElementById('textsize');
        a.innerHTML = '[' + msg_spread + ']';
        removeEvent(a, reduceMsg);
        addEvent(a, spreadMsg);
    }

    function html_format(message) {
        var e = document.all? 'null': 'event';
        message = message.replace(/&/g, '&amp;');
        message = message.replace(/</g, '&lt;');
        message = message.replace(/>/g, '&gt;');
        message = message.replace(/&gt;&gt;([0-9a-f]{8})/g,
                    '<a href="#r$1"' +
                    ' onmouseover="popupAnchor(' + e +', \'$1\');"' +
                    ' onmouseout="hidePopup();"' +
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
                       '#r' + $2 +
                       '">[[' + $1 + '/' + $2 + ']]</a>';
            });
        return message;
    }

    function showPreview() {
        var a = document.getElementById('previewctrl');
        var area = document.getElementById('preview');
        var message = form.body.value;
        var textsize = document.getElementById('textsize');
        var ref = document.getElementById('resreferrer');
        message = html_format(message);
        form.body.style.display = 'none';
        textsize.style.display = 'none';
        if (ref) {
            ref.style.display = 'none';
        }
        if (document.all) {
            area.innerHTML = '<pre>' + message + '</pre>'
        } else {
            area.innerHTML = '<p>' + message + '</p>'
        }
        area.style.display = 'block';
        a.innerHTML = '[' + msg_edit + ']';
        removeEvent(a, showPreview);
        addEvent(a, hidePreview);
    }

    function hidePreview() {
        var a = document.getElementById('previewctrl');
        var area = document.getElementById('preview');
        var textsize = document.getElementById('textsize');
        var ref = document.getElementById('resreferrer');
        area.style.display = 'none';
        form.body.style.display = 'inline';
        textsize.style.display = 'inline';
        if (ref) {
            ref.style.display = 'inline';
        }
        a.innerHTML = '[' + msg_preview + ']';
        removeEvent(a, hidePreview);
        addEvent(a, showPreview);
    }

    var p = form.getElementsByTagName('p')[0];
    var br = p.getElementsByTagName('br')[2];

    // Preview
    var span = document.createElement('span');
    span.innerHTML = ' <a href="" id="previewctrl" name="previewctrl"' +
                     ' onclick="return false;" onkeypress="return false;">[' +
                     msg_preview  + ']</a>'
    p.insertBefore(span, br);
    var preview = document.createElement('div');
    preview.id = 'preview';
    preview.style.display = 'none';
    form.appendChild(preview);
    var a = document.getElementById('previewctrl');
    addEvent(a, showPreview);

    // Text area size
    span = document.createElement('span');
    span.innerHTML = ' <a href="" id="textsize" name="textsize"' +
                     ' onclick="return false;" onkeypress="return false;">[' +
                     msg_spread  + ']</a>'
    p.insertBefore(span, br);
    a = document.getElementById('textsize');
    addEvent(a, spreadMsg);
};
