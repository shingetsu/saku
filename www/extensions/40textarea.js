shingetsu.addInitializer(function () {

    /* utility */
    Function.prototype.bind = function(base) {
       var self = this;
       return function() {
          self.apply(base, arguments);
       }
    }

    var addEvent = (window.addEventListener) ?
       (function(elm, type, event) {
          elm.addEventListener(type, event, false);
       }) : (window.attachEvent) ?
       (function(elm, type, event) {
          elm.attachEvent('on'+type, event);
       }) :
       (function(elm, type, event) {
          elm['on'+type] = event;
       }) ;

    var Position = {
       offset: function(elm) {
          var pos = {};
          pos.x = this.getOffset('Left', elm);
          pos.y = this.getOffset('Top', elm);
          return pos;
       },

       getOffset: function(prop, el) {
          if(el.offsetParent.tagName.toLowerCase() == "body")
             return el['offset'+prop];
          else
             return el['offset'+prop]+ this.getOffset(prop, el.offsetParent);
       },

       page: (document.all) ?
          (function() {
             var pos = {};
             pos.x = event.x + document.body.scrollLeft;
             pos.y = event.y + document.body.scrollTop;
             return pos;
          })
          :
          (function(e) {
             var pos = {};
             pos.x = e.pageX;
             pos.y = e.pageY;
             return pos;
          })
    }

    /* --------------------------------------------- */

    var ElementResizer = function() {
       this.initialize.apply(this, arguments);
    }

    ElementResizer.prototype = {
       _enable: false,
       _cursor: false,

       initialize: function(elm) {
          this.elm = elm;
          addEvent(elm, 'mousedown', this.start.bind(this));
          addEvent(elm, 'mousemove', this.pointer.bind(this));
          addEvent(document.body, 'mouseup',   this.stop.bind(this));
          addEvent(document.body, 'mousemove', this.doResize.bind(this));
       },

       pointer: function(e) {
          if(!this._cursor && this.resizePoint(e)) {
             this.elm.style.cursor = 'se-resize';
             this._cursor = true;
          } else if(this._cursor && !this.resizePoint(e)) {
             this.elm.style.cursor = 'default';
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

          offset.y += this.elm.offsetHeight;
          offset.x += this.elm.offsetWidth;

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

          this.elm.style.height = height + 'px';
          this.elm.style.width  = width  + 'px';
       }
    }

    if(location.pathname.match(/\/thread\.cgi\/.*/)){
       new ElementResizer(document.getElementById('postarticle').body);
    }
});
