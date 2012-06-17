/* Popup.
 * Copyright (C) 2005-2012 shinGETsu Project.
 */

shingetsu.plugins.Coordinate = function (e) {
    if (e) {
        this.x = e.pageX;
        this.y = e.pageY;
    } else {
        this.x = event.clientX;
        this.y = event.clientY;
    }
}

shingetsu.plugins.hidePopup = function () {
    $('#popup').html('').hide().css('padding', 0);
    $('select').show();
}

shingetsu.plugins.showPopup = function (coordinate, objects) {
    var popup = $('#popup');
    popup.html('');
    popup.append($(objects));

    var width = popup.width();
    var height = popup.height();
    var posX = Math.max($(document).scrollLeft(), coordinate.x + 20);
    var posY = Math.max($(document).scrollTop(), coordinate.y - height);
    popup.css('left', posX + 'px')
         .css('top', posY + 'px')
         .css('paddingLeft', '1em')
         .css('paddingRight', '1em')
         .show();
    $('select').hide();
}

shingetsu.initialize(function () {
    var popup = $('<div>');
    popup.attr('id', 'popup')
         .css('position', 'absolute')
         .css('left', '0')
         .css('top', '0')
         .hide()
         .appendTo($(document.body));
});
