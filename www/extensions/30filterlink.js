///gateway.cgi/changes & /gateway.cgi/index, /gateway.cgi/recent  add (filter) link.
//license: http://www.kmonos.net/nysl/ or public domain. (dual license).

shingetsu.addInitializer(() => {
    function mklink() {
        const filterlink = [];

        for (let i = 0; i < 3; i++) {
            filterlink[i] = document.createElement('a');
        }

        if (shingetsu.uiLang === 'ja') {
            filterlink[0].textContent = '公式';
            filterlink[1].textContent = '日記';
            filterlink[2].textContent = '全て';
        } else {
            filterlink[0].textContent = 'OFFICIAL';
            filterlink[1].textContent = 'DIARY';
            filterlink[2].textContent = 'ALL';
        }

        filterlink[0].href = location.pathname + '?filter=%E3%82%80%E3%81%A4%E3%81%AE%E6%97%A5%E8%A8%98%7C%E6%96%B0%E6%9C%88%E3%81%AE%E9%96%8B%E7%99%BA%7C%E9%9B%91%E8%AB%87%24%7C%E3%82%A2%E3%83%83%E3%83%97%E3%83%AD%E3%83%BC%E3%83%80%7C%E4%BB%8A%E5%BE%8C%E3%82%B9%E3%83%AC';
        filterlink[1].href = location.pathname + '?filter=%E6%97%A5%E8%A8%98';
        filterlink[2].href = location.pathname;

        return filterlink;
    }

    function add_filterlink() {
        const filterlink = mklink();
        const p_message = document.getElementsByTagName('p')[1];
        if (!p_message) return;

        const p = document.createElement('p');
        const ul = document.createElement('ul');

        filterlink.forEach((link) => {
            const li = document.createElement('ul');
            li.style.display = 'inline';
            //li.style.marginLeft = '-2ex';
            li.appendChild(link);
            ul.appendChild(li);
        });

        p.appendChild(ul);
        p.style.marginLeft = '-3ex';
        p_message.appendChild(p);
    }

    if (/\/gateway\.cgi\/changes/.test(location.pathname) || /\/gateway\.cgi\/recent/.test(location.pathname)) {
        add_filterlink();
    }
});
