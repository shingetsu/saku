// save "name", "mail", "signature", "desc_send", "error" in post form.
// original by Anonymous in shinGETsu.
// improved by shiroboushi.
// licenced by public domain.

shingetsu.addInitializer(function()
{
    //alert(document.cookie);
    if (document.cookie.search(/sg=1/) >= 0)
    {
        var form = parse();
        //alert('load');
        //alert(typeof form['dopost']);
        //alert(typeof form['error']);
        if(form['dopost'] == 'true')
        {
            document.forms["postarticle"].elements["dopost"].checked = true;
        }
        else
        {
            document.forms["postarticle"].elements["dopost"].checked = false;
        }
        if(form['error'] == 'true')
        {
            document.forms["postarticle"].elements["error"].checked = true;
        }
        else
        {
            document.forms["postarticle"].elements["error"].checked = false;
        }
        document.forms["postarticle"].elements["name"].value = form["name"];
        document.forms["postarticle"].elements["mail"].value = form["mail"];
        document.forms["postarticle"].elements["passwd"].value = form["sign"];
        //document.forms["postarticle"].elements["dopost"].checkd = form["dopost"];
        //document.forms["postarticle"].elements["error"].checkd = form["dopost"];
    }
    function parse()
    {
        // parse cookie by thread and return key-value.
        var data = document.cookie.split(";");
        var retd = {};
        for(var i = 0; i < data.length;i++)
        {
            tmp = data[i].split('=');
            tmp[0] = tmp[0].replace(new RegExp(' ', 'g'), '');    // remove space in key.
            retd[tmp[0]] = decodeURI(tmp[1]);
        }
        //alert(retd);
        return retd;
    }

    function save()
    {
        var name = document.forms["postarticle"].elements["name"].value;
        var mail = document.forms["postarticle"].elements["mail"].value;
        var sign = document.forms["postarticle"].elements["passwd"].value;
        var dopost = document.forms["postarticle"].elements["dopost"].checked + '';
        var error = document.forms["postarticle"].elements["error"].checked + '';
        //alert('save');
        //alert(dopost);
        //alert(error);
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
    var postarticle = document.getElementById("postarticle");
    if (postarticle.addEventListener)
    {
        postarticle.addEventListener("submit", save, false);
    }
    else if (postarticle.attachEvent)
    {
        postarticle.addEventListener("onsubmit", save);
    }
})
