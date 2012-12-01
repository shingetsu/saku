//'Write ID' to 'Res Number' Change.
//license: http://www.kmonos.net/nysl/ or public domain. (dual license).


shingetsu.initialize(function () {
    function id_res() {
        var dts = $('#records dt');
        var dds = $('#records dd');
        var ids = pushdId();
        var resplus = pushdPlusRes();
        var idres = new Array();
        for (var i=dts.length-1; i>=0; i--) {
            //idres[ids[i]] = eval(i+1+resplus) + " (" + ids[i] + ")"; //好みに合わせて書き換えて
            idres[ids[i]] = eval(i+1+resplus);
        }
        for (var i=0; i<dts.length; i++) {
            var at = dts.get(i).getElementsByTagName('a')[0];
            var nt = dts.get(i).getElementsByTagName('span')[0];
            if (at) {
                if (resplus < 0) {
                    //at.innerHTML = "";
                } else {
                    //at.innerHTML = at.innerHTML.replace(ids[i], "[" + idres[ids[i]] + "]"); //dtフィールド（見出し？）
                    at.innerHTML = at.innerHTML.replace(ids[i], idres[ids[i]] + " ");
                    var span = document.createElement('span');
                    span.innerHTML = 'ID:' + ids[i] + ' ';
                    var a = dts[i].getElementsByTagName('a');
                    if (a[a.length-1]) {
                        if (a[a.length-1].href == 'javascript:;') {
                            var a_last = a[a.length-1];
                            dts[i].removeChild(a_last);
                            dts[i].appendChild(span);
                            dts[i].appendChild(a_last);
                        } else {
                            dts[i].appendChild(span);
                        }
                    } else {
                        dts[i].appendChild(span);
                    }
                }
            }
            if (nt) {
                var id = nt.innerHTML.match(/[a-z0-9]{8}/g);
                if (id) {
                    for (var j=0; j<id.length; j++) {
                        if (idres[id[j]]) {
                            nt.innerHTML = nt.innerHTML.replace(id[j], idres[id[j]]); //nameフィールド
                        }
                    }
                }
            }
            var ad = dds[i].getElementsByTagName('a');
            if (ad) {
                for (var k=0; k<ad.length; k++) {
                    if (ad[k].innerHTML.match("&gt;&gt;.*")) {
                        var id = ad[k].innerHTML.replace("&gt;&gt;", "");
                        if (idres[id]) {
                            ad[k].innerHTML = ad[k].innerHTML.replace(id, idres[id]); //ddフィールド（本文）
                        }
                    }
                }
            }
        }
    }

    function res_id() {
        var ids = pushdId();
        var resplus = pushdPlusRes();
        var form = $('#postarticle').get(0);
        var form_split = form.body.value.split(">>");
        var form_name = form.name.value;
        for (var i=1; i<form_split.length; i++) {
            if (form_split[i]) {
                if (form_split[i].match("^([0-9]+)(( )|(\n)|(\r)|($)|([^0-9a-z]))")) {
                    var m = form_split[i].match("^([0-9]+)(( )|(\n)|(\r)|($)|([^0-9a-z]))");
                    if (ids[eval(m[1]-1-resplus)]) {
                        var n = ids[eval(m[1]-1-resplus)] + m[2];
                        form_split[i] = form_split[i].replace(m[0], n);
                    }
                }
            }
        }
        var loop = 1;
        while (loop) {
            if (form_name) {
                if (form_name.match("(^|>>|[^0-9a-z]+| )([0-9]+)(( )|($)|([^0-9a-z]+))")) {
                    var m = form_name.match("(^|>>|[^0-9a-z]+| )([0-9]+)(( )|($)|([^0-9a-z]+))");
                    if (ids[eval(m[2]-1-resplus)]) {
                        var n = m[1] + ids[eval(m[2]-1-resplus)] + m[3];
                        form_name = form_name.replace(m[0], n);
                    }
                } else {
                    loop = 0;
                }
            } else {
                loop = 0;
            }
        }
        form.body.value = form_split.join(">>");
        form.name.value = form_name;
    }

    function pushdPlusRes() {
        var maxrec = pushdMaxRec();
        var maxpage = pushdMaxPage();
        var cpage = currentPage();
        if (cpage == maxpage) {
            return 0;
        } else if (cpage < 0) {
            return -1;
        } else {
            var ids = pushdId();
            var pagesize = eval(ids.length);
            var last_res = eval(maxrec - eval(pagesize * maxpage));
            var resplus = eval(eval(maxpage - cpage - 1) * pagesize + last_res);
        }
        return resplus;
    }

    function pushdId() {
        var dts = $('#records dt');
        var ids = new Array();
        var re = new RegExp("^r", "i");
        for (var i=0; i<dts.length; i++) {
            ids[i] = dts.get(i).id.replace(re, "");
        }
        return ids;
    }

    function pushdMaxPage() {
        var as = $('#pagenavi a').get();
        if (as.length < 5) { //as[0].innerHTML = 'Go to the last article', as[1].innerHTML = '&lt;&lt;last', as[2].innerHTML = 'Archive'
            return 0;
        } else if (as[as.length -3].innerHTML.match(/&gt;&gt;/)) {
            var i = as.length - 4;
            return parseInt(as[i].innerHTML);
        } else {
            var i = as.length - 3;
            var prelast = parseInt(as[i].innerHTML);
            return eval(prelast + 1);
        }
    }

    function currentPage() {
        var page = location.pathname.match(/^\/thread\.cgi\/.*\/p[0-9]+$/);
        var perma = location.pathname.match(/^\/thread\.cgi\/.*\/[a-z0-9]+$/);
        if (page) {
            var current = String(location.pathname.match(/\/p[0-9]+$/)).replace("/p", "");
            return parseInt(current);
        } else if (perma) {
            return -1;
        } else {
            return 0;
        }
    }

    function pushdMaxRec() {
        var rec_n_size = $('#status').text();
        rec_n_size.match(/\(.*\/([0-9]+)\//);
        return parseInt(RegExp.$1);
    }

    function debug() {
        var rec_n_size = $('#status').text();
        alert(rec_n_size);
        rec_n_size.match(/\(.*\/([0-9]+)\//);
        alert(RegExp.$1);
    }

    function addReplaceLink() {
        var msg_res_id = '[Res to ID]';
        if (shingetsu.uiLang == 'ja') { msg_res_id = '[レス番号からIDに変換]'; }
        var p = $('#postarticle div').get(0);
        var span = document.createElement('span');
        span.innerHTML = '<a href="javascript:;" id="res_id" name="res_id">' + msg_res_id + '</a>';
        $(span).find('a').click(res_id);
        p.appendChild(span);
    }

    function addDebugLink() {
        var msg_debug = '[DEBUG]';
        if (shingetsu.uiLang == 'ja') { msg_debug = '[デバッグ]'; }
        var p = $('#postarticle div').get(0);
        var span = document.createElement('span');
        span.innerHTML = '<a href="javascript:;" id="debug" name="debug">' + msg_debug + '</a>';
        $(span).find('a').click(debug);
        p.appendChild(span);
    }

    function addonSubmit() {
        $('#postarticle').submit(res_id);
    }

    if (location.pathname.match(/\/thread\.cgi\/.*/)){
        id_res();
        addReplaceLink();
        //addDebugLink();
        addonSubmit();
    }
});
