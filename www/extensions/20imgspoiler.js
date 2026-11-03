/* -*- coding: utf-8 -*-
 * image spoiler-alert.
 * licenced by public domain.
 */

shingetsu.initialize(() => {
    function applySpoiler(img) {
        if (img.dataset.spoilerApplied) return;
        img.dataset.spoilerApplied = 'true';

        const originalFilter = img.style.filter;
        img.style.filter = 'blur(10px)';
        img.style.cursor = 'pointer';
        img.style.transition = 'filter 0.3s ease';

        img.addEventListener('click', () => {
            if (img.style.filter && img.style.filter !== 'none') {
                img.style.filter = 'none';
            } else {
                img.style.filter = 'blur(10px)';
            }
        });
    }

    function spoilerImages(container) {
        const images = container.querySelectorAll('img');
        images.forEach((img) => {
            applySpoiler(img);
        });
    }

    shingetsu.addRecordsModifiers(spoilerImages);
        
    const recordsEl = document.getElementById('records');
    if (recordsEl) {
        spoilerImages(recordsEl);
    }
});
