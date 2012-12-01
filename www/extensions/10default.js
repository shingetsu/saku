
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


function $(e) {
   return document.getElementById(e);
}

function $C(name, doc, tag) {
   if(!tag) tag = '*';
   if(!doc) doc = document;
   name = name.replace(/\-/g, "\\-");

   var results = new Array();
   var elements = (tag == '*' && doc.all) ? doc.all : doc.getElementsByTagName(tag);
   var reg = new RegExp('(^|\s)' + name + '(\s|$)');

   for(var elm, i = 0; elm = elements[i]; i++) {
      if(reg.test(elm.className))
         results.push(elm);
   }

   return results;
}
