///gateway.cgi/changes & /gateway.cgi/index, /gateway.cgi/recent  add (filter) link.
//license: http://www.kmonos.net/nysl/ or public domain. (dual license).

shingetsu.addInitializer(function () {
    function mklink() {
        var filterlink = new Array();
        filterlink[0] = document.createElement('a');
        filterlink[0].innerHTML = 'OFFICIAL'
        filterlink[1] = document.createElement('a');
        filterlink[1].innerHTML = 'DIARY'
        filterlink[2] = document.createElement('a');
        filterlink[2].innerHTML = 'ALL'
        if (shingetsu.uiLang == 'ja') {
            filterlink[0].innerHTML = '公式';
            filterlink[1].innerHTML = '日記';
            filterlink[2].innerHTML = '全て';
        }
        filterlink[0].href = location.pathname + '?filter=%E3%82%80%E3%81%A4%E3%81%AE%E6%97%A5%E8%A8%98%7C%E6%96%B0%E6%9C%88%E3%81%AE%E9%96%8B%E7%99%BA%7C%E9%9B%91%E8%AB%87%24%7C%E3%82%A2%E3%83%83%E3%83%97%E3%83%AD%E3%83%BC%E3%83%80%7C%E4%BB%8A%E5%BE%8C%E3%82%B9%E3%83%AC';
        filterlink[1].href = location.pathname + '?filter=%E6%97%A5%E8%A8%98';
        filterlink[2].href = location.pathname;
        return filterlink;
    }

    function add_filterlink() {
        var filterlink = mklink();
        var p_message = document.getElementsByTagName('p')[1];
        var p = document.createElement('p');
        var ul = document.createElement('ul');
        var li = new Array();
        if (filterlink) {
            for (var i=0; i< filterlink.length; i++) {
                li[i] = document.createElement('ul');
                li[i].style.display = 'inline';
                //li[i].style.marginLeft = '-2ex';
                li[i].appendChild(filterlink[i]);
                ul.appendChild(li[i]);
            }
            p.appendChild(ul);
            p.style.marginLeft = '-3ex';
            p_message.appendChild(p);
        }
    }

    if (location.pathname.match(/\/gateway\.cgi\/changes/)) {
        add_filterlink();
    //} else if (location.pathname.match(/\/gateway\.cgi\/index/)) {
    //    add_filterlink();
    } else if (location.pathname.match(/\/gateway\.cgi\/recent/)) {
        add_filterlink();
    }

});
