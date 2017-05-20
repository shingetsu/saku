//Copyright (c) 2017, WhiteCat6142. (MIT Licensed)
shingetsu.initialize(function () {
  $("dd>a:not(.innerlink)").each(function(i,e){if(/\.(jpg|png|gif)$/.test(e.getAttribute("href")))$(e).html('<img src="' + e.getAttribute("href") + '" height="210" style="display: inline;">');});
});
