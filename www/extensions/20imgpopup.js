/* Popup Image Preview.
 * Copyright (C) 2013 shinGETsu Project.
 */

shingetsu.initialize(() => {
    function showPopupImage(coordinate, image, count) {
        if (count > 100) {
            return;
        } else if (image.complete) {
            image.width = (image.width / image.height) * 100;
            image.height = 100;
            const p = document.createElement('p');
            p.appendChild(image);
            shingetsu.plugins.showPopup(coordinate, [p]);
        } else {
            setTimeout(() => {
                showPopupImage(coordinate, image, count + 1);
            }, 100);
        }
    }

    function popupImage(e, imguri) {
        const coordinate = new shingetsu.plugins.Coordinate(e);
        const image = new Image();
        image.src = imguri;
        showPopupImage(coordinate, image, 0);
    }

    function addPopup(container) {
        const anchors = container.querySelectorAll('a');

        anchors.forEach((anchor) => {
            if (anchor.pathname.search(/[.](jpg|jpeg|gif|png|bmp)$/i) <= 0) {
                return;
            }
            const url = anchor.href;

            anchor.addEventListener('mouseover', (e) => {
                popupImage(e, url);
            });
            anchor.addEventListener('mouseout', (e) => {
                shingetsu.plugins.hidePopup();
            });
        });
    }

    shingetsu.addRecordsModifiers(addPopup);
});
