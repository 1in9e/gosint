;
(function () {
  var vueAppend = {}

  var fireEvent = function (element, event) {
      var evt = document.createEvent('HTMLEvents');
      evt.initEvent(event, true, true);
      return !element.dispatchEvent(evt);
  };


  var slice = [].slice,
    singleTagRE = /^<(\w+)\s*\/?>(?:<\/\1>|)$/,
    tagExpanderRE = /<(?!area|br|col|embed|hr|img|input|link|meta|param)(([\w:]+)[^>]*)\/>/ig,
    table = document.createElement('table'),
    fragmentRE = /^\s*<(\w+|!)[^>]*>/,
    tableRow = document.createElement('tr'),
    containers = {
      'tr': document.createElement('tbody'),
      'tbody': table,
      'thead': table,
      'tfoot': table,
      'td': tableRow,
      'th': tableRow,
      '*': document.createElement('div')
    };

  var fragment = function (html, name, properties) {
    var dom, container
    // A special case optimization for a single tag
    if (singleTagRE.test(html)) dom = document.createElement(RegExp.$1)

    if (!dom) {
      if (html.replace) html = html.replace(tagExpanderRE, "<$1></$2>")
      if (name === undefined) name = fragmentRE.test(html) && RegExp.$1
      if (!(name in containers)) name = '*'

      container = containers[name]
      container.innerHTML = '' + html
      dom = slice.call(container.childNodes).map(function (child) {
        return container.removeChild(child)
      })
    }

    return dom
  }

  function traverseNode(node, fun) {
    fun(node)
    for (var key in node.childNodes) {
      traverseNode(node.childNodes[key], fun)
    }
  }

  var append = function (nodes, target, cb) {
    var pendingIndex = 0;
    var doneIndex = 0;
    nodes.forEach(function (_node) {
      var node = _node.cloneNode(true)
      if (document.documentElement !== target && document.documentElement.contains(target)) {
        traverseNode(target.insertBefore(node, null), function (el) {
          if (el.nodeName != null && el.nodeName.toUpperCase() === 'SCRIPT' && (!el.type || el.type === 'text/javascript')) {
            pendingIndex++;
            if (el.src) {
              var http = new XMLHttpRequest();
              http.open('GET', el.src, true);
              http.onreadystatechange = function () {
                if (http.readyState === 4) {
                  // Makes sure the document is ready to parse.
                  if (http.status === 200) {
                    el.innerHTML = http.responseText;
                    var target = el.ownerDocument ?
                      el.ownerDocument.defaultView :
                      window;
                    target['eval'].call(target, el.innerHTML);
                    doneIndex++;
                    if (doneIndex === pendingIndex) {
                      cb();
                    }
                  }
                }
              };
              http.send(null);
            } else {
              var target = el.ownerDocument ? el.ownerDocument.defaultView : window
              target['eval'].call(target, el.innerHTML);
              doneIndex++;
              if (doneIndex === pendingIndex) {
                cb();
              }
            }
          }
        })
      }
    })
  }

  var exec = function (el, val) {
    if (val) {
      try {
        el.innerHTML = '';
        append(fragment(val), el, function cb() {
          fireEvent(el, 'appended');
        })
      } catch (e) {
        fireEvent(el, 'appenderr');
        console.error(e);
      }
    }
  }

  // exposed global options
  vueAppend.config = {};

  vueAppend.install = function (Vue) {
    Vue.directive('append', {
      inserted: function (el, data) {
        exec(el, data.value);
      },
      componentUpdated: function (el, data) {
        if (data.value !== data.oldValue) {
          exec(el, data.value);
        }
      }
    })
  }

  if (typeof exports == "object") {
    module.exports = vueAppend;
  } else if (typeof define == "function" && define.amd) {
    define([], function () {
      return vueAppend
    });
  } else if (window.Vue) {
    window.VueAppend = vueAppend;
    Vue.use(vueAppend);
  }

})();
