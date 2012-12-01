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

    /* --------------------------------------------- */

    var IncrementalFilter = function() {
       this.initialize.apply(this, arguments);
    }

    IncrementalFilter.prototype = {
       _timer: false,

       initialize: function(input, lists, func) {
          this.lists = lists;
          this.input = input;
          this._func = func;
          addEvent(input, 'focus', this.start.bind(this));
          addEvent(input, 'blur',  this.stop.bind(this));
       },

       start: function() {
          this._timer = setInterval(this.update.bind(this), 500);
       },

       stop: function() {
          clearInterval(this._timer);
          this.update();
       },

       update: function(e) {
          var val = this.input.value;
          try { ''.match(val); } catch(e) { return; }

          for(var span, i = 0; span = this.lists[i];i++) {
             this._func(val, span);
          }
       }
    }

   if(location.pathname.match(/\/gateway\.cgi\/.*/)){
      // フィルタ
      var tpt = document.forms[0].filter;
      if(tpt) {
         new IncrementalFilter(tpt, document.getElementsByTagName('li'), function(val, span) {
            var name = (span.getElementsByTagName('a'))[0].innerHTML;
            span.style.display = (name.match(val, 'i')) ? '' : 'none';
         });

      }

      // タグ
      var tag = document.forms[1].tag;
      if(tag) {
         new IncrementalFilter(tag, document.getElementsByTagName('li'), function(val, span) {
            var result;
            if(val.length > 0) {
               var a = span.getElementsByTagName('a');
               for(var elm, i = 1;elm = a[i];i++) {
                  if(elm.innerHTML.match(val, 'i')) {
                     result = 1;
                     break;
                  }
               }
            } else {
               result = 1;
            }
            span.style.display = (result) ? '' : 'none';
         });
      }
   }
});
