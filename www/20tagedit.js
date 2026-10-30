/* Tag Edit Tool.
 * Copyright (C) 2007 shinGETsu Project.
 */

shingetsu.initialize(function () {
    if (location.pathname.search('/admin.cgi/edittag') != 0) {
        return;
    }

    const checked = {};

    function insertTag(tag) {
        const form = document.getElementById('savetag');
        if (form.tag.value != '') {
            form.tag.value += ' ' + tag;
        } else {
            form.tag.value = tag;
        }
    }

    function removeTag(tag) {
        const form = document.getElementById('savetag');
        let tmp = ' ' + form.tag.value + ' ';
        tmp = tmp.replace(' '+tag+' ', ' ');
        tmp = tmp.replace(/\s+/g, ' ');
        tmp = tmp.replace(/^\s+/g, '');
        tmp = tmp.replace(/\s+$/g, '');
        form.tag.value = tmp;
    }

    function toggleTag(tag) {
        const strtag = tag.innerHTML;
        if (checked[strtag]) {
            tag.style.backgroundColor = '#efefef';
        } else {
            tag.style.backgroundColor = '#ccc';
        }
    }

    function toggleAllTags(strtag) {
        const span = document.getElementsByTagName('span');
        for (let i=0; i<span.length; i++) {
            if ((span[i].className == 'tag') &&
                (span[i].innerHTML == strtag)) {
                toggleTag(span[i]);
            }
        }
        checked[strtag] = ! checked[strtag];
    }

    function clickTag(tag) {
        const strtag = tag.innerHTML;
        if (! checked[strtag]) {
            insertTag(strtag);
        } else {
            removeTag(strtag);
        }
        toggleAllTags(strtag);
    }

    const span = document.getElementsByTagName('span');
    const strcheck = ' ' + document.getElementById('savetag').tag.value + ' ';
    for (let i=0; i<span.length; i++) {
        if (span[i].className == 'tag') {
            span[i].onclick =
                (function (tag) {
                    return function () {
                        clickTag(tag);
                    }})(span[i]);
            span[i].style.cursor = 'pointer';
            const strtag = span[i].innerHTML;
            if ((strcheck.search(' ' + strtag +' ') >= 0) &&
                (! checked[strtag])) {
                toggleAllTags(strtag);
            }
        }
    }
});
