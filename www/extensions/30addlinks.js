///gateway.cgi & /thread.cgi menu add link.
//license: http://www.kmonos.net/nysl/ or public domain. (dual license).

shingetsu.addInitializer(function () {
    var menu = document.getElementById ('top');
    if (menu && menu.className == 'navbar') {
        var menu_a = menu.getElementsByTagName ('a');
        var menu_link = menu_links();
        var link = makelink (menu_a, menu_link);
        addmenulinks(menu, link);
    }
    var menu = document.getElementById ('bottom');
    if (menu && menu.className == 'navbar') {
        var menu_a = menu.getElementsByTagName ('a');
        var menu_link = menu_links();
        var link = makelink (menu_a, menu_link);
        addmenulinks(menu, link);
    }
    var topmenu = $('ul.topmenu');
    if (topmenu) {
        var topmenu_a = topmenu.find('a').get();
        var topmenu_link = topmenu_links();
        var toplink = makelink (topmenu_a, topmenu_link);
        addtopmenulinks(topmenu, toplink);
    }

    function menu_links () {
        var links = new Array();
        //links.push ('href Text|href Japanese Text|URI');
        //OR
        //links.push ('MENU[href]'); //Original
        //example links.push ('Archive|過去ログ|http://archive.shingetsu.info/');
        //example links.push ('MENU[/gateway.cgi]');
        //links.push ('GATEWAY|ゲートウェイ|/gateway.cgi');
        links.push ('MENU[/gateway.cgi]'); //TOP
        links.push ('MENU[/gateway.cgi/changes]'); //CHANGES
        links.push ('MENU[/gateway.cgi/recent]'); //RECENT
        //links.push ('MENU[/gateway.cgi/new]'); //NEW
        links.push ('MENU[/gateway.cgi/rss]'); //RSS
        return links;
    }

    function topmenu_links () {
        var links = new Array();
        links.push ('TOP|トップ|/');
        //links.push ('MENU|メニュー|/menu.html');
        links.push ('MENU[/gateway.cgi/changes]'); //CHANGES
        links.push ('MENU[/gateway.cgi/index]'); //INDEX
        links.push ('MENU[/gateway.cgi/recent]'); //RECENT
        //links.push ('MENU[/gateway.cgi/new]'); //NEW
        //links.push ('MENU[http://archive.shingetsu.info/]'); //Archive
        links.push ('Archive|保管庫|/kakolog.html');
        links.push ('MENU[/admin.cgi/search]'); //Search
        links.push ('MENU[/admin.cgi/status]'); //Status
        //links.push ('MENU[http://shingetsu.info/]'); //Official Site
        links.push ('Official|公式|http://shingetsu.info/'); //Official Site
        //links.push ('MENU[/gateway.cgi/motd]'); //Agreement
        links.push ('Agreement|利用条件|/gateway.cgi/motd');
        links.push ('MENU[/gateway.cgi/rss]'); //RSS
        links.push ('Hoven|Hoven|/hoven_a0.12_winsaku_1.5.3r1.zip');
        return links;
    }

    function makelink (menu_a, menu_link) {
        var link = new Array();
        for (i=0; i<menu_link.length; i++) {
            if (menu_link[i].match(/MENU\[[^\]]+\]/)) {
                if (menu_link[i].match(/MENU\[http:\/\/.*\]/)) {
                    var d = menu_link[i].match(/MENU\[(http:\/\/.*)\]/);
                    var hd = d[1];
                    //alert (hd);
                } else {
                    var d = menu_link[i].match(/MENU\[([^\]]+)\]/);
                    var hd = 'http://' + location.host + d[1];
                }
                //if (hd) {
                    for (j=0; j<menu_a.length; j++) {
                        if (menu_a[j] && menu_a[j].href == hd) {
                            link.push('  <a href="' + hd + '">' + menu_a[j].innerHTML + '</a>');
                        }
                    }
                //}
            } else {
                var m = menu_link[i].match(/(.*)\|(.*)\|(.*)/);
                if (shingetsu.uiLang == 'ja') {
                    link.push('  <a href="' + m[3] + '">' + m[2] + '</a>');
                } else {
                    link.push('  <a href="' + m[3] + '">' + m[1] + '</a>');
                }
            }
        }
        return link;
    }

    function addmenulinks (menu, link) {
        var container = $(menu).find('ul.nav');
        container.empty();
        for (i=0; i<link.length; i++) {
            var li = $('<li>');
            li.html(link[i]);
            container.append(li);
        }
    }

    function addtopmenulinks(topmenu, link) {
        topmenu.empty();
        for (i=0; i<link.length; i++) {
            var li = $('<li>');
            li.html(link[i]);
            topmenu.append(li);
        }
    }
});
