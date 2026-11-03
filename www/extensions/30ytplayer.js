/**
 * YouTube Player ( 30ytplayer.js )
 *
 * \author ultraist
 * \date 2006-01-16
 *
 */

shingetsu.addInitializer(() => {
    // initialize

    const g_playerInfo = {
        x: 0,
        y: 0,
        frameX: 0,
        frameY: 0,
        flag: false,
        visible: false,
        timer: 0,
        scrollX: window.pageXOffset,
        scrollY: window.pageYOffset
    };

    const g_ytplayer = document.createElement('div');
    g_ytplayer.id = 'ytwindow';

    const body = document.body;
    body.appendChild(g_ytplayer);

    g_ytplayer.style.position = "absolute";
    g_ytplayer.style.left = "0px";
    g_ytplayer.style.top = "0px";
    g_ytplayer.style.visibility = "hidden";

    const anc = document.querySelectorAll('a');

    anc.forEach((a) => {
        const href = a.href;
        if ((href.startsWith('http://www.youtube.com/') || href.startsWith('http://youtube.com/')) && /v=([\w-]+)/.test(href)) {
            const match = href.match(/v=([\w-]+)/);
            if (match) {
                const id = match[1];
                a.addEventListener('mouseover', (event) => {
                    popupYTPlayer(event, id);
                }, false);
            }
        }
    });

    //-- handler

    function Coordinate(e) {
        if (e) {
            this.x = e.pageX;
            this.y = e.pageY;
        } else {
            this.x = window.event ? window.event.clientX : 0;
            this.y = window.event ? window.event.clientY : 0;
        }
    }

    function dragStart(e) {
        g_playerInfo.x = e.layerX || e.offsetX || 0;
        g_playerInfo.y = e.layerY || e.offsetY || 0;
        g_playerInfo.flag = true;
    }

    function dragEnd() {
        g_playerInfo.flag = false;
    }

    function move(e) {
        if (!g_playerInfo.flag) {
            return;
        }
        const x = e.pageX;
        const y = e.pageY;
        g_playerInfo.frameX = x - g_playerInfo.x;
        g_playerInfo.frameY = y - g_playerInfo.y;

        g_ytplayer.style.left = g_playerInfo.frameX + "px";
        g_ytplayer.style.top = g_playerInfo.frameY + "px";

        return false;
    }

    function scrollYTPlayer() {
        g_playerInfo.frameX -= g_playerInfo.scrollX - window.pageXOffset;
        g_playerInfo.frameY -= g_playerInfo.scrollY - window.pageYOffset;
        g_playerInfo.scrollX = window.pageXOffset;
        g_playerInfo.scrollY = window.pageYOffset;

        g_ytplayer.style.left = g_playerInfo.frameX + "px";
        g_ytplayer.style.top = g_playerInfo.frameY + "px";
    }

    function hideYTPlayer() {
        const pop = g_ytplayer;
        if (pop) {
            pop.innerHTML = "";
            pop.style.padding = "0";
            pop.style.visibility = "hidden";
            g_playerInfo.visible = false;
            clearInterval(g_playerInfo.timer);
        }
    }

    function showYTPlayer(coordinate, objects) {
        if (g_playerInfo.visible) {
            return;
        }
        const pop = g_ytplayer;
        if (!pop) {
            return null;
        }
        pop.innerHTML = '';
        objects.forEach((obj) => {
            pop.appendChild(obj);
        });

        const button = document.getElementById('ytclose');
        const button2 = document.getElementById('ytclose2');
        const bar = document.getElementById('ytbar');
        const bar2 = document.getElementById('ytbar2');

        if (!(button && bar && button2 && bar2)) {
            return;
        }

        // add event handlers
        button.onclick = hideYTPlayer;
        bar.onmousedown = dragStart;
        bar.onmouseup = dragEnd;
        bar.onmousemove = move;

        button2.onclick = hideYTPlayer;
        bar2.onmousedown = dragStart;
        bar2.onmouseup = dragEnd;
        bar2.onmousemove = move;

        const nWidth = pop.scrollWidth;
        const nHeight = pop.scrollHeight;
        let nPosX = coordinate.x + 20;
        let nPosY = coordinate.y - nHeight;

        if (window.pageYOffset && (nPosY < window.pageYOffset)) {
            nPosY = window.pageYOffset;
        } else if (nPosY < 0) {
            nPosY = 0;
        }

        g_playerInfo.frameX = nPosX;
        g_playerInfo.frameY = nPosY;
        pop.style.left = nPosX + "px";
        pop.style.top = nPosY + "px";

        pop.style.paddingLeft = "1em";
        pop.style.paddingRight = "1em";
        pop.style.visibility = "visible";
        g_playerInfo.visible = true;
        g_playerInfo.timer = setInterval(scrollYTPlayer, 50);

        return pop;
    }

    function createYTPlayer(id) {
        const url = 'http://www.youtube.com/v/' + id;
        const ytplayer = document.createElement('div');

        ytplayer.innerHTML =
            '<div id="ytbar" style="text-align:right;border:1px solid black;background:white;">'
          + '   (<a id="ytclose" href="javascript:void(0)">close</a>)'
          + '</div>'
          + '<object width="425" height="350">'
          + '   <param id="ytmovie" name="movie" value="' + url + '"></param>'
          + '   <param name="wmode" value="transparent"></param>'
          + '   <embed id="ytembed" src="' + url + '" type="application/x-shockwave-flash"'
          + '        wmode="transparent" width="425" height="350">'
          + '   </embed>'
          + '</object>'
          + '<div id="ytbar2" style="border:1px solid black;background:white;">'
          + '   (<a id="ytclose2" href="javascript:void(0)">close</a>)'
          + '</div>';

        return ytplayer;
    }

    function popupYTPlayer(e, id) {
        const coordinate = new Coordinate(e);
        const ytplayer = createYTPlayer(id);
        showYTPlayer(coordinate, [ytplayer]);
    }
});
