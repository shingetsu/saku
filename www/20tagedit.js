/* Tag Edit Tool.
 * Copyright (C) 2007 shinGETsu Project.
 * $Id$
 */

initFunc[initFunc.length] = function () {
    if (location.pathname.search('/admin.cgi/edittag') != 0) {
        return;
    }

    var checked = {};

    function insertTag(tag) {
        var form = document.getElementById('savetag');
        if (form.tag.value != '') {
            form.tag.value += ' ' + tag;
        } else {
            form.tag.value = tag;
        }
    }

    function removeTag(tag) {
        var form = document.getElementById('savetag');
        var tmp = ' ' + form.tag.value + ' ';
        tmp = tmp.replace(' '+tag+' ', ' ');
        tmp = tmp.replace(/\s+/g, ' ');
        tmp = tmp.replace(/^\s+/g, '');
        tmp = tmp.replace(/\s+$/g, '');
        form.tag.value = tmp;
    }

    function toggleTag(tag) {
        var strtag = tag.innerHTML;
        if (checked[strtag]) {
            tag.style.backgroundColor = '#efefef';
        } else {
            tag.style.backgroundColor = '#ccc';
        }
    }

    function toggleAllTags(strtag) {
        var span = document.getElementsByTagName('span');
        for (var i=0; i<span.length; i++) {
            if ((span[i].className == 'tag') &&
                (span[i].innerHTML == strtag)) {
                toggleTag(span[i]);
            }
        }
        checked[strtag] = ! checked[strtag];
    }

    function clickTag(tag) {
        var strtag = tag.innerHTML;
        if (! checked[strtag]) {
            insertTag(strtag);
        } else {
            removeTag(strtag);
        }
        toggleAllTags(strtag);
    }

    var span = document.getElementsByTagName('span');
    var strcheck = ' ' + document.getElementById('savetag').tag.value + ' ';
    for (var i=0; i<span.length; i++) {
        if (span[i].className == 'tag') {
            span[i].onclick =
                (function (tag) {
                    return function () {
                        clickTag(tag);
                    }})(span[i]);
            span[i].style.cursor = 'pointer';
            var strtag = span[i].innerHTML;
            if ((strcheck.search(' ' + strtag +' ') >= 0) &&
                (! checked[strtag])) {
                toggleAllTags(strtag);
            }
        }
    }
};
