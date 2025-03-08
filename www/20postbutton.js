// Post button controller.
// Copyright (c) 2025 shinGETsu Project.

shingetsu.initialize(function() {
    $('#postarticle').submit(function () {
        $('#postarticle button').prop('disabled', true);
        setTimeout(function () {
            $('#postarticle button').prop('disabled', false);
        }, 1000);
        return true;
    });
});
