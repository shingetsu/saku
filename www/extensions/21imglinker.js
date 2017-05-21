//Copyright (c) 2017, WhiteCat6142. (MIT Licensed)
shingetsu.initialize(function () {
  $("dd>a:not(.innerlink)").each(function(i,e){if(/\.(jpg|png|gif)$/.test(e.getAttribute("href")))$(e).prepend($('<img>',{ src:e.getAttribute("href"),style:"display: block;"}).height(210));});
});
