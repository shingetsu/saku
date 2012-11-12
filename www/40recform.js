// save "name", "mail", "signature", "desc_send", "error" in post form.
// original by Anonymous in shinGETsu.
// improved by shiroboushi.
// licenced by public domain.

shingetsu.initialize(function() {
    if (document.cookie.search(/sg=1/) >= 0) {
        load();
    }

    function load() {
        var saved = parse(document.cookie);
        $('#dopost').attr('checked', (saved.dopost == 'true'));
        $('#error').attr('checked', (saved.error == 'true'));
        $('#name').val(saved.name);
        $('#mail').val(saved.mail);
        $('#passwd').val(saved.sign);

        $('#postarticle').find('.post-advanced').each(function (i, element) {
            element = $(element);
            if (element.find(':text[value!=""], :password[value!=""]').length > 0) {
                element.removeClass('post-advanced');
            }
            if (element.find(':checkbox:not(:checked)').length > 0) {
                element.removeClass('post-advanced');
            }
        });
    }

    function parse(cookie) {
        var ret = {};
        $.each(cookie.split(';'), function (i, val) {
            var tmp = val.split('=');
            tmp[0] = tmp[0].replace(/ /g, '');
            ret[tmp[0]] = decodeURI(tmp[1]);
        });
        return ret;
    }

    function save()
    {
        console.log("save");
        var name = document.forms["postarticle"].elements["name"].value;
        var mail = document.forms["postarticle"].elements["mail"].value;
        var sign = document.forms["postarticle"].elements["passwd"].value;
        var dopost = document.forms["postarticle"].elements["dopost"].checked + '';
        var error = document.forms["postarticle"].elements["error"].checked + '';
        name = encodeURI(name);
        mail = encodeURI(mail);
        sign = encodeURI(sign);
        dopost = encodeURI(dopost);
        error = encodeURI(error);

        var exp = new Date();
        exp.setTime(exp.getTime()+1000*60*60*24*32);
        exp = "expires=" + exp.toGMTString() + ";";
        var path = "path=/thread.cgi/;"
        var sg = 'sg=1;';

        name = 'name=' + name + ';';
        mail = 'mail=' + mail + ';';
        sign = 'sign=' + sign + ';';
        dopost = 'dopost=' + dopost + ';';
        error = 'error=' + error + ';';

        document.cookie = sg + exp;
        document.cookie = path + exp;
        document.cookie = name + exp;
        document.cookie = mail + exp;
        document.cookie = sign + exp;
        document.cookie = dopost + exp;
        document.cookie = error + exp;
    }

    $('#postarticle').submit(save);
});
