/*
 * llcommon.js
 *
 * Set of defaults and utilities for phantomjs
 *
 * import into phantomjs script using:
 *  `phantom.page.injectJs('llcommon.js');`
 */
var webpage = require('webpage');
var system = require('system');
var ARGS = system.args;

// print phantom errors
phantom.onError = function(msg, trace) {
  var msgStack = ['PHANTOM ERROR: ' + msg];
  if (trace && trace.length) {
    msgStack.push('TRACE:');
    trace.forEach(function(t) {
      msgStack.push(' -> ' + (t.file || t.sourceURL) + ': ' + t.line + (t.function ? ' (in function ' + t.function +')' : ''));
    });
  }
  console.error(msgStack.join('\n'));
  phantom.exit(-1);
};

var llcommon = {
  jqueryCDN: 'http://code.jquery.com/jquery-1.11.3.min.js',
  timeout: 5,
  createPage: function() {
    /*
     * Create page, enable error and console messages
     */
    var page = webpage.create();
    page.onError = function(msg, trace) {
      var msgStack = ['ERROR: ' + msg];
      if (trace && trace.length) {
        msgStack.push('TRACE:');
        trace.forEach(function(t) {
          msgStack.push(' -> ' + t.file + ': ' + t.line + (t.function ? ' (in function "' + t.function +'")' : ''));
        });
      }
      console.error(msgStack.join('\n'));
    };
    page.onConsoleMessage = function(msg) {
      console.log(msg);
    };
    return page;
  },
  openPage: function(page, url, callback) {
    this.openPageHelper(page, url, callback, false);
  },
  jQueryOpenPage: function(page, url, callback) {
    this.openPageHelper(page, url, callback, true);
  },
  openPageHelper: function(page, url, callback, jqueryEnabled) {
    /*
     * Open page, check status, load jQuery and execute callback
     */
    var that = this;
    page.open(url, function(status) {
      if (status !== 'success') {
        console.log("Could not open page to crawl. URL: " + url);
        phantom.exit(-1);
      }

      if (jqueryEnabled) {
        page.includeJs(that.jqueryCDN, function() {
          callback();
          page.close();
        });
      } else {
        callback();
        page.close();
      }
    });
  },
  exportDataToJSON: function(data, filename, success) {
    require('fs').write(filename, JSON.stringify(data), 'w');
    success(data);
  }
}
