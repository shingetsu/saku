//'Write ID' to 'Res Number' Change.
//license: http://www.kmonos.net/nysl/ or public domain. (dual license).


shingetsu.initialize(() => {
    function id_res() {
        const dts = document.querySelectorAll('#records dt');
        const dds = document.querySelectorAll('#records dd');
        const ids = pushdId();
        const resplus = pushdPlusRes();
        const idres = {};

        for (let i = dts.length - 1; i >= 0; i--) {
            //idres[ids[i]] = i + 1 + resplus + " (" + ids[i] + ")"; //好みに合わせて書き換えて
            idres[ids[i]] = i + 1 + resplus;
        }

        for (let i = 0; i < dts.length; i++) {
            const at = dts[i].getElementsByTagName('a')[0];
            const nt = dts[i].getElementsByTagName('span')[0];

            if (at) {
                if (resplus >= 0) {
                    //at.innerHTML = "";
                    //at.innerHTML = at.innerHTML.replace(ids[i], "[" + idres[ids[i]] + "]"); //dtフィールド（見出し？）
                    at.innerHTML = at.innerHTML.replace(ids[i], idres[ids[i]] + " ");
                    const span = document.createElement('span');
                    span.innerHTML = 'ID:' + ids[i] + ' ';
                    const a = dts[i].getElementsByTagName('a');
                    const a_last = a[a.length - 1];
                    if (a_last) {
                        if (a_last.getAttribute('href') === 'javascript:;') {
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
                const id = nt.innerHTML.match(/[a-z0-9]{8}/g);
                if (id) {
                    for (let j = 0; j < id.length; j++) {
                        if (idres[id[j]]) {
                            nt.innerHTML = nt.innerHTML.replace(id[j], idres[id[j]]); //nameフィールド
                        }
                    }
                }
            }

            const ad = dds[i].getElementsByTagName('a');
            if (ad) {
                for (let k = 0; k < ad.length; k++) {
                    if (ad[k].innerHTML.match("&gt;&gt;.*")) {
                        const id = ad[k].innerHTML.replace("&gt;&gt;", "");
                        if (idres[id]) {
                            ad[k].innerHTML = ad[k].innerHTML.replace(id, idres[id]); //ddフィールド（本文）
                        }
                    }
                }
            }
        }
    }

    function res_id() {
        const ids = pushdId();
        const resplus = pushdPlusRes();
        const form = document.querySelector('#postarticle');
        if (!form) return;

        const form_split = form.body.value.split(">>");
        let form_name = form.name.value;

        for (let i = 1; i < form_split.length; i++) {
            if (form_split[i]) {
                const regex = /^([0-9]+)(( )|(\n)|(\r)|($)|([^0-9a-z]))/;
                if (regex.test(form_split[i])) {
                    const m = form_split[i].match(regex);
                    const targetIndex = parseInt(m[1]) - 1 - resplus;
                    if (ids[targetIndex]) {
                        const n = ids[targetIndex] + m[2];
                        form_split[i] = form_split[i].replace(m[0], n);
                    }
                }
            }
        }

        let loop = 1;
        while (loop) {
            if (form_name) {
                const nameRegex = /(^|>>|[^0-9a-z]+| )([0-9]+)(( )|($)|([^0-9a-z]+))/;
                if (nameRegex.test(form_name)) {
                    const m = form_name.match(nameRegex);
                    const targetIndex = parseInt(m[2]) - 1 - resplus;
                    if (ids[targetIndex]) {
                        const n = m[1] + ids[targetIndex] + m[3];
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
        const maxrec = pushdMaxRec();
        const maxpage = pushdMaxPage();
        const cpage = currentPage();
        let resplus = 0;

        if (cpage === maxpage) {
            return 0;
        } else if (cpage < 0) {
            return -1;
        } else {
            const ids = pushdId();
            const pagesize = ids.length;
            const last_res = maxrec - (pagesize * maxpage);
            resplus = (maxpage - cpage - 1) * pagesize + last_res;
        }
        return resplus;
    }

    function pushdId() {
        const dts = document.querySelectorAll('#records dt');
        const ids = [];
        const re = /^r/i;
        for (let i = 0; i < dts.length; i++) {
            ids[i] = dts[i].id.replace(re, "");
        }
        return ids;
    }

    function pushdMaxPage() {
        const as = document.querySelectorAll('#pagenavi a');
        if (as.length < 5) { //as[0].innerHTML = 'Go to the last article', as[1].innerHTML = '&lt;&lt;last', as[2].innerHTML = 'Archive'
            return 0;
        } else if (/&gt;&gt;/.test(as[as.length - 3].innerHTML)) {
            const i = as.length - 4;
            return parseInt(as[i].innerHTML);
        } else {
            const i = as.length - 3;
            const prelast = parseInt(as[i].innerHTML);
            return prelast + 1;
        }
    }

    function currentPage() {
        const page = /^\/thread\.cgi\/.*\/p[0-9]+$/.test(location.pathname);
        const perma = /^\/thread\.cgi\/.*\/[a-z0-9]+$/.test(location.pathname);
        if (page) {
            const match = location.pathname.match(/\/p[0-9]+$/);
            const current = match ? match[0].replace("/p", "") : "0";
            return parseInt(current);
        } else if (perma) {
            return -1;
        } else {
            return 0;
        }
    }

    function pushdMaxRec() {
        const statusEl = document.getElementById('status');
        const rec_n_size = statusEl ? statusEl.textContent : '';
        const match = rec_n_size.match(/\(.*\/([0-9]+)\//);
        return match ? parseInt(match[1]) : 0;
    }

    function debug() {
        const statusEl = document.getElementById('status');
        const rec_n_size = statusEl ? statusEl.textContent : '';
        alert(rec_n_size);
        const match = rec_n_size.match(/\(.*\/([0-9]+)\//);
        if (match) {
            alert(match[1]);
        }
    }

    function addReplaceLink() {
        let msg_res_id = '[Res to ID]';
        if (shingetsu.uiLang === 'ja') { msg_res_id = '[レス番号からIDに変換]'; }
        const p = document.querySelector('#postarticle div');
        if (!p) return;
        const span = document.createElement('span');
        span.innerHTML = '<a href="javascript:;" id="res_id" name="res_id">' + msg_res_id + '</a>';
        span.querySelector('a').addEventListener('click', res_id);
        p.appendChild(span);
    }

    function addDebugLink() {
        let msg_debug = '[DEBUG]';
        if (shingetsu.uiLang === 'ja') { msg_debug = '[デバッグ]'; }
        const p = document.querySelector('#postarticle div');
        if (!p) return;
        const span = document.createElement('span');
        span.innerHTML = '<a href="javascript:;" id="debug" name="debug">' + msg_debug + '</a>';
        span.querySelector('a').addEventListener('click', debug);
        p.appendChild(span);
    }

    function addonSubmit() {
        const form = document.querySelector('#postarticle');
        if (form) {
            form.addEventListener('submit', res_id);
        }
    }

    if (/\/thread\.cgi\/.*/.test(location.pathname)){
        id_res();
        addReplaceLink();
        //addDebugLink();
        addonSubmit();
    }
});
