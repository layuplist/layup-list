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

var terms = system.args.slice(1).map(function(term) { return term.toLowerCase(); });
var mediansURL = "http://www.dartmouth.edu/~reg/transcript/medians/";

var parseMediansAtURLs = function(urls, medians) {
  if (urls.length === 0) {
    llcommon.exportDataToJSON(medians, "medians.json", function() {
      console.log("success! " + medians.length + " medians crawled and exported.");
      phantom.exit();
    });
  } else {
    var url = urls.pop();
    console.log("Parsing medians from: " + url);
    var page = llcommon.createPage();
    llcommon.openPage(page, url, function() {
      var mediansOnPage = page.evaluate(extractMediansFromPage);
      console.log(mediansOnPage.length + " found.");
      medians = medians.concat(mediansOnPage);
      setTimeout(function() { parseMediansAtURLs(urls, medians); }, llcommon.timeout);
    });
  }
}

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
      enrollment: medianData[2].innerHTML,
      median: medianData[3].innerHTML
    });
  }
  return medians;
}

parseMediansAtURLs(terms.map(function(term) {
  return mediansURL + term + ".html"
}), []);
