/**
 * Tag Edit Tool.
 * Copyright (C) 2007 shinGETsu Project.
 */

shingetsu.initialize(() => {
    if (!location.pathname.startsWith('/admin.cgi/edittag')) {
        return;
    }

    const checked = {};
    const savetagForm = document.getElementById('savetag');
    if (!savetagForm) return;

    const insertTag = (tag) => {
        const tagInput = savetagForm.tag;
        if (tagInput.value.trim() !== '') {
            tagInput.value += ` ${tag}`;
        } else {
            tagInput.value = tag;
        }
    };

    const removeTag = (tag) => {
        const tagInput = savetagForm.tag;
        let tmp = ` ${tagInput.value} `;
        tmp = tmp.replace(` ${tag} `, ' ');
        tagInput.value = tmp.replace(/\s+/g, ' ').trim();
    };

    const toggleTag = (tagElement, isChecked) => {
        tagElement.style.backgroundColor = isChecked ? '#ccc' : '#efefef';
    };

    const toggleAllTags = (strtag) => {
        const spans = document.querySelectorAll('span.tag');
        spans.forEach((span) => {
            if (span.textContent === strtag) {
                toggleTag(span, !checked[strtag]);
            }
        });
        checked[strtag] = !checked[strtag];
    };

    const clickTag = (tagElement) => {
        const strtag = tagElement.textContent;
        if (!checked[strtag]) {
            insertTag(strtag);
        } else {
            removeTag(strtag);
        }
        toggleAllTags(strtag);
    };

    const spans = document.querySelectorAll('span.tag');
    const tagInputValue = savetagForm.tag ? savetagForm.tag.value : '';
    const strcheck = ` ${tagInputValue} `;

    spans.forEach((span) => {
        const strtag = span.textContent;

        span.style.cursor = 'pointer';
        span.addEventListener('click', () => clickTag(span));

        if (strcheck.includes(` ${strtag} `) && !checked[strtag]) {
            toggleAllTags(strtag);
        }
    });
});
