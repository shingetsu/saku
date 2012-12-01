shingetsu.initialize(function () {
    var Position = {
       offset: function(elm) {
          var pos = {};
          pos.x = this.getOffset('Left', elm);
          pos.y = this.getOffset('Top', elm);
          return pos;
       },

       getOffset: function(prop, el) {
          el = el.get(0);
          if(el.offsetParent.tagName.toLowerCase() == "body")
             return el['offset'+prop];
          else
             return el['offset'+prop]+ this.getOffset(prop, el.offsetParent);
       },

       page: function(e) {
          var pos = {};
          pos.x = e.pageX;
          pos.y = e.pageY;
          return pos;
       }
    };

    if (! document.all) {
        // NOT IE
    } else if (document.compatMode == 'CSS1Compat') {
       Position.page = function() {
          var pos = {};
          pos.x = event.x + document.documentElement.scrollLeft;
          pos.y = event.y + document.documentElement.scrollTop;
          return pos;
       };
    } else {
       Position.page = function() {
          var pos = {};
          pos.x = event.x + document.body.scrollLeft;
          pos.y = event.y + document.body.scrollTop;
          return pos;
       };
    };

    /* --------------------------------------------- */

    var ElementResizer = function() {
       this.initialize.apply(this, arguments);
    }

    ElementResizer.prototype = {
       _enable: false,
       _cursor: false,

       initialize: function(elm) {
          this.elm = elm;
          var self = this;
          elm.mousedown(function (e) { self.start(e); });
          elm.mousemove(function (e) { self.pointer(e); });
          $(document.body).mouseup( function (e) { self.stop(e); });
          $(document.body).mousemove( function (e) { self.doResize(e); });
       },

       pointer: function(e) {
          if(!this._cursor && this.resizePoint(e)) {
             this.elm.css('cursor', 'se-resize');
             this._cursor = true;
          } else if(this._cursor && !this.resizePoint(e)) {
             this.elm.css('cursor', 'default');
             this._cursor = false;
          }
       },

       start: function(e) {
          if(this.resizePoint(e))
             this._enable = true;
       },

       stop: function() {
          this._enable = false;
       },

       resizePoint: function(e) {
          var offset = Position.offset(this.elm);
          var page   = Position.page(e);

          offset.y += this.elm.get(0).offsetHeight;
          offset.x += this.elm.get(0).offsetWidth;

          if(offset.y - 32 < page.y && page.y < offset.y &&
             offset.x - 32 < page.x && page.x < offset.x - 8) {
             return true;
          }
       },

       doResize: function(e) {
          if(!this._enable) return;
          var offset = Position.offset(this.elm);
          var page   = Position.page(e);

          var width  = page.x - offset.x + 24;
          var height = page.y - offset.y + 16;
          if (width  < 50) width  = 50;
          if (height < 50) height = 50;

          this.elm.css('height', height + 'px');
          this.elm.css('width', width  + 'px');
       }
    }

    if(location.pathname.match(/\/thread\.cgi\/.*/)){
       new ElementResizer($('#postarticle textarea[name=body]'));
    }
});
