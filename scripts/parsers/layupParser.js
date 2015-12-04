/**
 * layupParser.js
 *
 * Parse the csv containing layup data
 *
 * Usage: node layupParser.js [path to CSV file]
 * Output: layups.json
 * 
 */

var fs = require('fs');
var jsonfile = require('jsonfile');
var csv = require('csv');


var parseCSV = function(file) {
  var buf = fs.readFileSync(file).toString('utf8');
  // npm is the bomb
  csv.parse(buf, {columns: true}, function(err, data) {
    writeJSON('./layups.json', data);
  });
};

var writeJSON = function(outfile, outJSON) {
  jsonfile.writeFileSync(outfile, outJSON);
};


var main = function() {
  parseCSV(process.argv[2]);
};

main();
