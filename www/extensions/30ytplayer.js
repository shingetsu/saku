/**
 * YouTube Player ( 30ytplayer.js )
 * 
 * \author ultraist
 * \date 2006-01-16
 * 
 */

shingetsu.addInitializer(function () {
    // initialize
    
    var g_ytplayer;
    var g_playerInfo  = new Object;
    g_playerInfo.x      = 0;
    g_playerInfo.y      = 0;
    g_playerInfo.frameX = 0;
    g_playerInfo.frameY = 0;
    g_playerInfo.flag   = false;
    g_playerInfo.visible= false;
    g_playerInfo.timer  = 0;
    
    if (document.all) {
        var body = documentBody();
        g_playerInfo.scrollX = body.scrollLeft;
        g_playerInfo.scrollY = body.scrollTop;
    } else {
        g_playerInfo.scrollX = window.pageXOffset;
        g_playerInfo.scrollY = window.pageYOffset;
    }
    
    g_ytplayer      = document.createElement('div');
    g_ytplayer.id   = 'ytwindow';
    
    var body = document.getElementsByTagName('body')[0];
    body.appendChild(g_ytplayer);
    var pop = document.getElementById("ytwindow");
    if (pop) {
        pop.style.position = "absolute";
        pop.style.left = "0px";
        pop.style.top = "0px";
        pop.visibility = "hidden";
    }
    
    var anc = document.getElementsByTagName('a');
    
    for (var i = 0; i < anc.length; ++i) {
        if ((anc[i].href.search('http://www.youtube.com/') == 0
        	|| anc[i].href.search('http://youtube.com/') == 0)
            	&& anc[i].href.search(/v=([\w-]+)/) > 0) 
        {
            var id = RegExp.$1;
            
            if (anc[i].addEventListener) {
                anc[i].addEventListener(
                    'mouseover',
                    (function (_id) {
                        return function (event) {popupYTPlayer(event, _id);}
                    })(id),
                    false);
            } else if (anc[i].attachEvent) {
                anc[i].attachEvent(
                    'onmouseover',
                    (function (_id) {
                        return function () {popupYTPlayer(null, _id);}
                    })(id));
            }
        }
    }
    
    
    //-- handler
    
    function Coordinate(e) {
        if (e) {
            this.x = e.pageX;
            this.y = e.pageY;
        } else {
            this.x = event.clientX;
            this.y = event.clientY;
        }
    }
    
    function documentBody()
    {
        var body;
        
        if (document.all) {
            body = (document.compatMode=='CSS1Compat') 
                    ? document.documentElement : document.body;
        } else {
            body = document.body;
        }
        
        return body;
    }
    
    function dragStart(e)
    {
        if (document.all) {
            // IE7
            var body = documentBody();
            
            g_playerInfo.x = event.offsetX;
            g_playerInfo.y = event.offsetY;
        } else {
            g_playerInfo.x = e.layerX;
            g_playerInfo.y = e.layerY;
        }
        
        g_playerInfo.flag = true;
    }
    
    function dragEnd(e)
    {
        g_playerInfo.flag = false;
    }
    
    function move(e)
    {
        var x, y;
        
        if (! g_playerInfo.flag) {
            return;
        }
        if (document.all) {
            var body = documentBody();
            
            x = event.x + body.scrollLeft;
            y = event.y + body.scrollTop;
            g_playerInfo.frameX     = x - g_playerInfo.x
            g_playerInfo.frameY     = y - g_playerInfo.y;
            g_ytplayer.style.left   = g_playerInfo.frameX
            g_ytplayer.style.top    = g_playerInfo.frameY;
        } else {
            x = e.pageX;
            y = e.pageY;
            g_playerInfo.frameX     = x - g_playerInfo.x;
            g_playerInfo.frameY     = y - g_playerInfo.y;
            
            g_ytplayer.style.left   = g_playerInfo.frameX + "px";
            g_ytplayer.style.top    = g_playerInfo.frameY + "px";
        }
        
        return false;
    }
    
    function scrollYTPlayer()
    {
        if (document.all) {
            var body = documentBody();
            g_playerInfo.frameX -= g_playerInfo.scrollX - body.scrollLeft;
            g_playerInfo.frameY -= g_playerInfo.scrollY - body.scrollTop;
            g_playerInfo.scrollX = body.scrollLeft;
            g_playerInfo.scrollY = body.scrollTop;
            
            g_ytplayer.style.left   = g_playerInfo.frameX;
            g_ytplayer.style.top    = g_playerInfo.frameY;
        } else {
            g_playerInfo.frameX -= g_playerInfo.scrollX - window.pageXOffset;
            g_playerInfo.frameY -= g_playerInfo.scrollY - window.pageYOffset;
            g_playerInfo.scrollX = window.pageXOffset;
            g_playerInfo.scrollY = window.pageYOffset;
            
            g_ytplayer.style.left   = g_playerInfo.frameX + "px";
            g_ytplayer.style.top    = g_playerInfo.frameY + "px";
        }
    }
    
    function hideYTPlayer() {
        var pop = g_ytplayer;
        if (pop) {
            pop.innerHTML = "";
            pop.style.padding = 0;
            pop.visibility = "hidden";
            g_playerInfo.visible = false;
            clearInterval(g_playerInfo.timer);
        }
        if (document.all) {
            var select = document.getElementsByTagName('select');
            for (var i=0; i<select.length; i++) {
                select[i].style.visibility = 'visible';
            }
        }
    }
    
    
    function showYTPlayer(coordinate, objects) 
    {
        if (g_playerInfo.visible) {
            return;
        }
        var pop = g_ytplayer;
        
        if (! pop) {
            return null;
        }
        pop.innerHTML = '';
        for (var i=0; i<objects.length; i++) {
            pop.appendChild(objects[i]);
        }
        var button  = document.getElementById('ytclose');
        var button2 = document.getElementById('ytclose2');
        var bar     = document.getElementById('ytbar');
        var bar2    = document.getElementById('ytbar2');
        
        if (! (button && bar && button2 && bar2)) {
            return;
        }
        
        // add event handlers
        button.onclick  = hideYTPlayer;
        bar.onmousedown = dragStart;
        bar.onmouseup   = dragEnd;
        bar.onmousemove = move;
        
        button2.onclick     = hideYTPlayer;
        bar2.onmousedown    = dragStart;
        bar2.onmouseup  = dragEnd;
        bar2.onmousemove    = move;

        
        if(document.all) {
            var nWidth  = pop.clientWidth;
            var nHeight = pop.clientHeight;
            var nPosX   = coordinate.x + 20;
            var nPosY   = coordinate.y - nHeight;
            if (nPosY < 0) {
                nPosY = 0;
            }
            // IE7
            var body = documentBody();
            
            g_playerInfo.frameX = nPosX + body.scrollLeft;
            g_playerInfo.frameY = nPosY + body.scrollTop;
            pop.style.left = g_playerInfo.frameX;
            pop.style.top = g_playerInfo.frameY;
            var select = document.getElementsByTagName('select');
            for (var i=0; i<select.length; i++) {
                select[i].style.visibility = 'hidden';
            }
        } else {
            var nWidth  = pop.scrollWidth;
            var nHeight = pop.scrollHeight;
            var nPosX = coordinate.x + 20;
            var nPosY = coordinate.y - nHeight;
            if (document.body.scrollTop && (nPosY < document.body.scrollTop)) {
                nPosY = document.body.scrollTop;
            } else if (window.pageYOffset && (nPosY < window.pageYOffset)) {
                nPosY = window.pageYOffset;
            } else if (nPosY < 0) {
                nPosY = 0;
            }
            g_playerInfo.frameX = nPosX;
            g_playerInfo.frameY = nPosY
            pop.style.left = nPosX + "px";
            pop.style.top = nPosY + "px";
        }
        pop.style.paddingLeft = "1em";
        pop.style.paddingRight = "1em";
        pop.style.visibility = "visible";
        g_playerInfo.visible = true;
        g_playerInfo.timer = setInterval(scrollYTPlayer, 50);
        
        return pop;
    }
    
    
    function createYTPlayer(id)
    {
        var url = 'http://www.youtube.com/v/' + id;
        var ytplayer = document.createElement('div');
        
        ytplayer.innerHTML = 
            '<div id="ytbar" style="text-align:right;border:1px solid black;background:white;">'
        +   '   (<a id="ytclose" href="javascript:void(0)">close</a>)'
        +   '</div>'
        +   '<object width="425" height="350">'
        +   '   <param id="ytmovie" name="movie" value="' + url + '"></param>'
        +   '   <param name="wmode" value="transparent"></param>'
        +   '   <embed id="ytembed" src="' + url + '" type="application/x-shockwave-flash"'
        +   '       wmode="transparent" width="425" height="350">'
        +   '   </embed>'
        +   '</object>'
        +   '<div id="ytbar2" style=";border:1px solid black;background:white;">'
        +   '   (<a id="ytclose2" href="javascript:void(0)">close</a>)'
        +   '</div>';
        
        
        return ytplayer;
    }
    
    function popupYTPlayer(e, id)
    {
        var coordinate = new Coordinate(e);
        var ytplayer = createYTPlayer(id);
        showYTPlayer(coordinate, [ytplayer]);
    }
});
