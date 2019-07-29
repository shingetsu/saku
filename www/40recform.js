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
        $('#dopost').prop('checked', saved.dopost);
        $('#error').prop('checked', saved.error);
        $('#name').val(saved.name);
        $('#mail').val(saved.mail);
        $('#passwd').val(saved.passwd);

        $('#postarticle').find('.post-advanced').each(function (i, element) {
            element = $(element);
            if (saved.name && element.find('#name').length > 0) {
                element.removeClass('post-advanced');
            }
            if (saved.mail && element.find('#mail').length > 0) {
                element.removeClass('post-advanced');
            }
            if (saved.passwd && element.find('#passwd').length > 0) {
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
        } catch (e) {
            return null;
        }
    }

    function save()
    {
        var item = {};
        var form = $('#postarticle');
        item.name = form.find('[name=name]').val();
        item.mail = form.find('[name=mail]').val();
        item.passwd = form.find('[name=passwd]').val();
        item.dopost = form.find('[name=dopost]').prop('checked');
        item.error = form.find('[name=error]').prop('checked');
        localStorage.setItem('recform', JSON.stringify(item));
    }

    $('#postarticle').submit(save);
});
