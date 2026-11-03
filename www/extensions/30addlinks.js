///gateway.cgi & /thread.cgi menu add link.
//license: http://www.kmonos.net/nysl/ or public domain. (dual license).

shingetsu.addInitializer(() => {
    ['top', 'bottom'].forEach((id) => {
        const menu = document.getElementById(id);
        if (menu && menu.classList.contains('navbar')) {
            const menu_a = menu.getElementsByTagName('a');
            const menu_link = menu_links();
            const link = makelink(menu_a, menu_link);
            addmenulinks(menu, link);
        }
    });

    const topmenu = document.querySelector('ul.topmenu');
    if (topmenu) {
        const topmenu_a = topmenu.querySelectorAll('a');
        const topmenu_link = topmenu_links();
        const toplink = makelink(topmenu_a, topmenu_link);
        addtopmenulinks(topmenu, toplink);
    }

    function menu_links() {
        const links = [];
        //links.push ('href Text|href Japanese Text|URI');
        //OR
        //links.push ('MENU[href]'); //Original
        //example links.push ('Archive|過去ログ|http://archive.shingetsu.info/');
        //example links.push ('MENU[/gateway.cgi]');
        //links.push ('GATEWAY|ゲートウェイ|/gateway.cgi');
        links.push('MENU[/gateway.cgi]'); //TOP
        links.push('MENU[/gateway.cgi/changes]'); //CHANGES
        links.push('MENU[/gateway.cgi/recent]'); //RECENT
        //links.push ('MENU[/gateway.cgi/new]'); //NEW
        links.push('MENU[/gateway.cgi/rss]'); //RSS
        return links;
    }

    function topmenu_links() {
        const links = [];
        links.push('TOP|トップ|/');
        //links.push ('MENU|メニュー|/menu.html');
        links.push('MENU[/gateway.cgi/changes]'); //CHANGES
        links.push('MENU[/gateway.cgi/index]'); //INDEX
        links.push('MENU[/gateway.cgi/recent]'); //RECENT
        //links.push ('MENU[/gateway.cgi/new]'); //NEW
        //links.push ('MENU[http://archive.shingetsu.info/]'); //Archive
        links.push('Archive|保管庫|/kakolog.html');
        links.push('MENU[/admin.cgi/search]'); //Search
        links.push('MENU[/admin.cgi/status]'); //Status
        //links.push ('MENU[http://shingetsu.info/]'); //Official Site
        links.push('Official|公式|http://shingetsu.info/'); //Official Site
        //links.push ('MENU[/gateway.cgi/motd]'); //Agreement
        links.push('Agreement|利用条件|/gateway.cgi/motd');
        links.push('MENU[/gateway.cgi/rss]'); //RSS
        links.push('Hoven|Hoven|/hoven_a0.12_winsaku_1.5.3r1.zip');
        return links;
    }

    function makelink(menu_a, menu_link) {
        const link = [];
        for (let i = 0; i < menu_link.length; i++) {
            const item = menu_link[i];
            if (/MENU\[[^\]]+\]/.test(item)) {
                let hd;
                const matchHttp = item.match(/MENU\[(http:\/\/[^\]]+)\]/);
                if (matchHttp) {
                    hd = matchHttp[1];
                } else {
                    const matchPath = item.match(/MENU\[([^\]]+)\]/);
                    if (matchPath) {
                        hd = location.protocol + '//' + location.host + matchPath[1];
                    }
                }
                if (hd) {
                    for (let j = 0; j < menu_a.length; j++) {
                        if (menu_a[j] && menu_a[j].href === hd) {
                            link.push('  <a href="' + hd + '">' + menu_a[j].innerHTML + '</a>');
                        }
                    }
                }
            } else {
                const m = item.match(/(.*)\|(.*)\|(.*)/);
                if (m) {
                    if (shingetsu.uiLang === 'ja') {
                        link.push('  <a href="' + m[3] + '">' + m[2] + '</a>');
                    } else {
                        link.push('  <a href="' + m[3] + '">' + m[1] + '</a>');
                    }
                }
            }
        }
        return link;
    }

    function addmenulinks(menu, link) {
        const container = menu.querySelector('ul.nav');
        if (container) {
            container.innerHTML = '';
            link.forEach((htmlStr) => {
                const li = document.createElement('li');
                li.innerHTML = htmlStr;
                container.appendChild(li);
            });
        }
    }

    function addtopmenulinks(topmenu, link) {
        topmenu.innerHTML = '';
        link.forEach((htmlStr) => {
            const li = document.createElement('li');
            li.innerHTML = htmlStr;
            topmenu.appendChild(li);
        });
    }
});
