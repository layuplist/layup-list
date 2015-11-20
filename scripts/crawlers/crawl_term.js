/*
 * Extracts courses that are available for a certain term.
 *
 * Check what terms are available:
 * http://oracle-www.dartmouth.edu/dart/groucho/timetable.main
 *
 * Created using phantomjs 2.0.0
 */
phantom.page.injectJs('llcommon.js');

var url = 'http://oracle-www.dartmouth.edu/dart/groucho/timetable.display_courses';
var includeVariableAttribute = {
  room: false,
  building: false,
  enrollment: false,
  status: false,
};

if (ARGS.length !== 3) {
  console.log("Usage:   \tphantomjs " + ARGS[0] + " [YEAR] [TERM]");
  console.log("Examples:\tphantomjs " + ARGS[0] + " 2016 W");
  console.log("         \tphantomjs " + ARGS[0] + " 2016 1");
  phantom.exit(-1);
}

var cleanData = function(data) {
  return String(data).trim()
}

var createTerm = function(year, season) {
  season = season.toLowerCase();
  if (season === "w") {
    season = 1;
  } else if (season === "s") {
    season = 3;
  } else if (season === "x") {
    season = 6;
  } else if (season === "f") {
    season = 9;
  }

  if (year.length === 2) {
    year = "20" + year
  } else if (year.length !== 4) {
    console.log("Year must be either four or two digits.");
    phantom.exit(-1);
  }
  return "" + year + "0" + season;
}

var term = createTerm(ARGS[1], ARGS[2]);
var data = 'distribradio=alldistribs&depts=no_value&periods=no_value&distribs=no_value&distribs_i=no_value&distribs_wc=no_value&pmode=public&term=&levl=&fys=n&wrt=n&pe=n&review=n&crnl=no_value&classyear=2008&searchtype=Subject+Area%28s%29&termradio=selectterms&terms=no_value&subjectradio=selectsubjects&hoursradio=allhours&sortorder=dept&terms=' + term;
var page = llcommon.createPage();
console.log("Loading page... term: " + term);
page.open(url, 'post', data, function(status) {
  if (status !== 'success') {
    console.log('Unable to load page. Term parsed as: ' + term);
    phantom.exit(-1);
  }

  page.includeJs(llcommon.jqueryCDN, function() {
    console.log("Loaded page. Retrieving rows.");
    var data = page.evaluate(function(includeVariableAttribute, cleanData) {
      var courses = [];
      $(".data-table > table > tbody > tr").each(function(idx) {
        if (idx !== 0) {
          var cells = $(this).find("td");

          var numbers = $(cells[3]).text().split(".");
          var subnumber = numbers[1];
          subnumber = typeof subnumber === "undefined" ? "" : subnumber;

          courses.push({
            crn: cleanData($(cells[1]).text()),
            program: cleanData($(cells[2]).text()),
            number: cleanData(numbers[0]),
            subnumber: cleanData(subnumber),
            section: cleanData($(cells[4]).text()),
            title: cleanData($(cells[5]).text()),
            crosslisted: cleanData($(cells[7]).text()),
            period: cleanData($(cells[8]).text()),
            room: cleanData($(cells[9]).text()),
            building: cleanData($(cells[10]).text()),
            instructor: cleanData($(cells[11]).text()),
            world_culture: cleanData($(cells[12]).text()),
            distribs: cleanData($(cells[13]).text()),
            limit: cleanData($(cells[14]).text()),
            enrollment: cleanData($(cells[15]).text()),
            status: cleanData($(cells[16]).text()),
          });

          for (attribute in includeVariableAttribute) {
            if (!includeVariableAttribute[attribute]) {
              delete courses[courses.length - 1][attribute];
            }
          }
        }
      });
      return courses;
    }, includeVariableAttribute, cleanData);

    data.sort(function(a, b) { return a.crn - b.crn; });
    llcommon.exportDataToJSON(data, term + "_courses.json", function() {
      console.log("success! " + data.length + " courses crawled and exported.");
      phantom.exit()
    });
  });
});
