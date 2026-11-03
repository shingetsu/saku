/**
 * Localtime of User Agent.
 * Copyright (c) 2006 shinGETsu Project.
 */

shingetsu.initialize(() => {
    const format = (n) => String(n).padStart(2, '0');

    const myLocaltime = (date) => {
        const year = date.getFullYear();
        const month = format(date.getMonth() + 1);
        const day = format(date.getDate());
        const hours = format(date.getHours());
        const minutes = format(date.getMinutes());
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    };

    const overrideDatetime = (container) => {
        const elements = container.querySelectorAll('span.stamp[data-stamp]');
        elements.forEach((el) => {
            const stamp = el.getAttribute('data-stamp');
            if (stamp === '0' || stamp === 0) {
                el.textContent = '0000-00-00 00:00';
            } else {
                const date = new Date(Number(stamp) * 1000);
                el.textContent = myLocaltime(date);
            }
        });
    };

    shingetsu.addRecordsModifiers(overrideDatetime);
});
