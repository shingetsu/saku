shingetsu.initialize(function () {
    var IncrementalFilter = function() {
       this.initialize.apply(this, arguments);
    }

    IncrementalFilter.prototype = {
       _timer: false,

       initialize: function(input, lists, func) {
          this.lists = lists;
          this.input = input;
          this._func = func;
          var self = this;
          input.focus(function () { self.start(); });
          input.blur(function () { self.stop(); });
       },

       start: function() {
          this._timer = setInterval(this.update.bind(this), 500);
       },

       stop: function() {
          clearInterval(this._timer);
          this.update();
       },

       update: function(e) {
          var val = this.input.val();
          try { ''.match(val); } catch(e) { return; }

          for(var span, i = 0; span = this.lists[i];i++) {
             this._func(val, span);
          }
       }
    }

   if(location.pathname.match(/\/gateway\.cgi\/.*/)){
      var listitems = $('#thread_index li').get();

      // フィルタ
      var tpt = $('#filterform input[name=filter]');
      if(tpt) {
         new IncrementalFilter(tpt, listitems, function(val, span) {
            var name = (span.getElementsByTagName('a'))[0].innerHTML;
            span.style.display = (name.match(val, 'i')) ? '' : 'none';
         });

      }

      // タグ
      var tag = $('#tagform input[name=tag]');
      if(tag) {
         new IncrementalFilter(tag, listitems, function(val, span) {
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
