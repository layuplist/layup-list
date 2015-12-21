/*
 * Extracts median information from Dartmouth.
 *
 * Example Usage:
 *  phantomjs crawl_medians.js 13s 13x 13f 14w 14s 14x 14f 15w 15s 15x
 *
 * Available terms are shown on:
 * http://www.dartmouth.edu/~reg/transcript/medians/
 *
 * Created using phantomjs 2.0.0
 */
phantom.page.injectJs('llcommon.js');

var terms = ARGS.slice(1).map(function(term) { return term.toLowerCase(); });
var mediansURL = "http://www.dartmouth.edu/~reg/transcript/medians/";

var parseMediansAtURLs = function(terms, urls) {
  if (urls.length === 0) {
    console.log("success!");
    phantom.exit();
  } else {
    var url = urls.pop();
    var term = terms.pop();
    console.log("Parsing medians from: " + url);
    var page = llcommon.createPage();
    llcommon.openPage(page, url, function() {
      var mediansOnPage = page.evaluate(extractMediansFromPage);
      console.log(mediansOnPage.length + " found!");

      mediansOnPage.sort(function(a, b) {
        if (a.course.department === b.course.department) {
          if (a.course.number === b.course.number) {
            return parseInt(a.course.subnumber) - parseInt(b.course.subnumber);
          } else {
            return parseInt(a.course.number) - parseInt(b.course.number);
          }
        } else {
          return a.course.department < b.course.department ? -1 : 1;
        }
      });

      llcommon.exportDataToJSON(mediansOnPage, term + "_medians.json", function() {
        console.log("Exported.");
      });
      setTimeout(function() { parseMediansAtURLs(terms, urls); }, llcommon.timeout);
    });
  }
};

var extractMediansFromPage = function() {
  var rows = $("table > tbody > tr");
  var medians = [];
  for (var r = 0; r < rows.length; r++) {
    var medianData = rows[r].children;
    medians.push({
      term: medianData[0].innerHTML,
      course: {
        department: medianData[1].innerHTML.split("-")[0],
        number: medianData[1].innerHTML.split("-")[1].split(".")[0],
        subnumber: medianData[1].innerHTML.split("-")[1].split(".")[1]
      },
      section: medianData[1].innerHTML.split("-")[2],
      enrollment: medianData[2].innerHTML,
      median: medianData[3].innerHTML
    });
  }
  return medians;
};

parseMediansAtURLs(terms, terms.map(function(term) {
  return mediansURL + term + ".html";
}));
