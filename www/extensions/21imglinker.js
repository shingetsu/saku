//Copyright (c) 2017, WhiteCat6142. (MIT Licensed)
shingetsu.initialize(() => {
    const links = document.querySelectorAll('dd > a:not(.innerlink)');
    links.forEach((e) => {
        const href = e.getAttribute('href');
        if (/\.(jpg|png|gif)$/.test(href)) {
            const img = document.createElement('img');
            img.src = href;
            img.style.display = 'block';
            img.height = 210;
            e.prepend(img);
        }
    });
});
