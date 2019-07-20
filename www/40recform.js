// save "name", "mail", "signature", "desc_send", "error" in post form.
// original by Anonymous in shinGETsu.
// improved by shiroboushi.
// licenced by public domain.

shingetsu.initialize(function() {
    var saved = parse(localStorage.getItem('recform'));
    if (saved) {
        load(saved);
    }

    function load(saved) {
        $('#dopost').attr('checked', (saved.dopost == 'true'));
        $('#error').attr('checked', (saved.error == 'true'));
        $('#name').val(saved.name);
        $('#mail').val(saved.mail);
        $('#passwd').val(saved.sign);

        $('#postarticle').find('.post-advanced').each(function (i, element) {
            element = $(element);
            if (saved.name && element.find('#name').length > 0) {
                element.removeClass('post-advanced');
            }
            if (saved.mail && element.find('#mail').length > 0) {
                element.removeClass('post-advanced');
            }
            if (saved.sign && element.find('#passwd').length > 0) {
                element.removeClass('post-advanced');
            }
            if (element.find(':checkbox:not(:checked)').length > 0) {
                element.removeClass('post-advanced');
            }
        });
    }

    function parse(saved) {
        try {
            return JSON.parse(saved);
        } catch {
            return null;
        }
    }

    function save()
    {
        var item = {};
        item.name = document.forms['postarticle'].elements['name'].value;
        item.mail = document.forms['postarticle'].elements['mail'].value;
        item.sign = document.forms['postarticle'].elements['passwd'].value;
        item.dopost = document.forms['postarticle'].elements['dopost'].checked + '';
        item.error = document.forms['postarticle'].elements['error'].checked + '';
        localStorage.setItem('recform', JSON.stringify(item));
    }

    $('#postarticle').submit(save);
});
