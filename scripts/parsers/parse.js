/**
 * parse.js
 *
 * Parse the crawled HTML from course picker. Does things synchronously (relieves
 * callback confusion & done once anyways).
 *
 *
 * Usage: node parse.js [path to NEW REVIEW files] [path to OLD REVIEW FILES]
 * Output: new_reviews.json old_reviews.json (JSON array in both)
 *
 */

var cheerio = require('cheerio');
var fs = require('fs');
var jsonfile = require('jsonfile');
var path = require('path')


/**
 * parseNew(): Takes an HTML string and finds the course dept, number, and review comments
 * @param  {[string]} html: the HTML we want to parse
 * @return {[object]} courseJSON: the object with parsed data stored as properties. Note this is a Javascript object
 *                                 and is not JSON yet!
 */
var parseNew = function(html) {
  var $ = cheerio.load(html);

  var COMMENT_TYPE = {
    0: "course",
    1: "professor",
    2: "workload"
  };
  var courseJSON = {};


  // parsing course info
  try {
    var courseID = $('.PageTitle > h1 > a').attr('title').split(" ").slice(3, 5);
    courseJSON.department = courseID[0];
    courseJSON.number = courseID[1];
  } catch (e) {
    if (e instanceof(TypeError)) {
      courseJSON.department = "";
      courseJSON.number = "";
    }
  }

  var courseProf = $('#content > h2 > a').attr('title');

  if (!courseProf) {
    courseJSON.professor = "";
  } else {
    courseJSON.professor = courseProf.split(" ").slice(3, 5).join(" ");
  }
  courseJSON.term = $('.compact > td')[1].children[0].data.split(" ").join("").substring(2);


  // parsing the student comments (on course, prof, workload)
  courseJSON.comments = {};
  $('#prof-comment').each(function(index) {
    courseJSON.comments[COMMENT_TYPE[index]] = $(this).html();
  });

  return courseJSON;
};


/**
 * parseOld(): Takes an HTML string and finds the course dept, number, and review comments
 * @param  {[string]} html: the HTML we want to parse
 * @return {[object]} courseJSON: the object with parsed data stored as properties. Note this is a Javascript object
 *                                 and is not JSON yet!
 */
var parseOld = function(html) {
  var $ = cheerio.load(html);
  var courseJSON = {};


  // parsing course info
  try {
    var courseID = $('.PageTitle > h1 > a').attr('title').split(" ").slice(3, 5);
    courseJSON.department = courseID[0];
    courseJSON.number = courseID[1];
    var courseProf = $('#content > h2 > a').attr('title');

    if (!courseProf) {
      courseJSON.professor = "";
    } else {
      courseJSON.professor = courseProf.split(" ").slice(3, 5).join(" ");
    }
    courseJSON.term = $('.compact > td')[1].children[0].data.split(" ").join("").substring(2);

    // parsing the student comments (on course, prof, workload)
    courseJSON.comments = {};

    courseJSON.comments.oldReview = $('.old_reviews_comments > p').html();
  } catch (e) {
    if (e instanceof(TypeError)) {
    }
  }

  return courseJSON;
};


/**
 * writeToFile: Handles JSON file writing semantics
 *
 * Unfortunately they templated old reviews vs new reviews differently, which explains
 * the version param
 *
 * @param  {[string]} outfile: name of JSON file to write to
 * @param  {[string]} param: name of JSON file to write to
 */
var writeToFile = function(dir, outfile, param) {
  var outJSON = [];
  files = fs.readdirSync(dir);
  files.forEach(function(file) {

    if (path.extname(file) === '.html' || parseInt(file) > -1) {
      var full_file = dir + file;
      var buf = fs.readFileSync(full_file).toString('utf8');

      if (param === "old") {
        outJSON.push(parseOld(buf));
      } else {
        outJSON.push(parseNew(buf));
      }

    } else {
      console.log("You should be parsing html files");
    }
  });
  jsonfile.writeFileSync(outfile, outJSON);
};


/**
 * main()
 */
var main = function() {

  if (process.argv.length < 3) {
    console.log("Need to provide one or more paths to html files.");
  }
  writeToFile(process.argv[2], './new_reviews.json', "new");
  writeToFile(process.argv[3], './old_reviews.json', "old");
};

main();
