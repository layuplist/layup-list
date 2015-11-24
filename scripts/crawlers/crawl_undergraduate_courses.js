/*
 * Parses the Dartmouth undergraduate course listings and generates JSON.
 *
 * 1. Retrieves departments from department directory, places in stack
 * 2. Visits each department, placing programs in stack
 * 3. Visits each program, placing courses in stack
 * 5. Exports course data
 *
 * Created using phantomjs 2.0.0
 */
phantom.page.injectJs('llcommon.js');

var Navigation = {};
var Evaluation = {};
var year = new Date().getFullYear();
var orc = "http://dartmouth.smartcatalogiq.com/en/" + year + "/orc/"
var undergradDepartmentsURL = orc + "Departments-Programs-Undergraduate/";

// programs which cannot be parsed from department pages.
var additionalPrograms = [
  {
    code: "ENVS",
    programName: "Environmental Studies",
    url: undergradDepartmentsURL + "Environmental-Studies-Program/ENVS-Environmental-Studies/"
  }
];

Navigation.start = function() {
  Navigation.departmentDirectory();
}

Navigation.departmentDirectory = function() {
  var page = llcommon.createPage();
  llcommon.openPage(page, undergradDepartmentsURL, function() {
    console.log("...retrieving departments to process");
    var departmentsToProcess = page.evaluate(Evaluation.getDepartmentLinksFromDepartmentDirectory);
    console.log("...retrieved.");

    console.log("...retrieving programs");
    departmentsToProcess.reverse();
    setTimeout(function () {
      Navigation.departments(departmentsToProcess, []);
    }, llcommon.timeout);
  });
}

Navigation.departments = function(remainingDepartments, programs) {
  if (remainingDepartments.length === 0) {
    console.log("...retrieving courses")
    setTimeout(function () {
      Navigation.programs(programs.concat(additionalPrograms), []);
    }, llcommon.timeout);
  } else {
    var department = remainingDepartments.pop();

    var page = llcommon.createPage();
    llcommon.openPage(page, department.url, function() {
      var newPrograms = page.evaluate(Evaluation.getProgramLinksFromDepartment);
      var programsStringBuilder = [];
      for (var p = 0; p < newPrograms.length; p++) {
        programs.push(newPrograms[p]);
        programsStringBuilder.push(newPrograms[p].code);
      }
      console.log("(" + programsStringBuilder.length + ") " + department.dptName + ": " + programsStringBuilder.join(", "))
      setTimeout(function () {
        Navigation.departments(remainingDepartments, programs);
      }, llcommon.timeout);
    });
  }
}

Navigation.programs = function (remainingPrograms, courses) {
  if (remainingPrograms.length === 0) {
    courses.sort(function(a, b) {
      if (a.department === b.department) {
        if (a.number === b.number) {
          return parseInt(a.subnumber) - parseInt(b.subnumber);
        } else {
          return parseInt(a.number) - parseInt(b.number);
        }
      } else {
        return a.department < b.department ? -1 : 1;
      }
    });

    llcommon.exportDataToJSON(courses, "undergraduate_courses.json", function() {
      console.log("success! " + courses.length + " courses crawled and exported.");
      phantom.exit()
    });
  } else {
    var program = remainingPrograms.pop();

    var page = llcommon.createPage();
    llcommon.openPage(page, program.url, function() {
      var newCourses = page.evaluate(Evaluation.getCourseLinksFromProgram);
      var numbers = [];
      for (var c = 0; c < newCourses.length; c++) {
        if (newCourses[c].subnumber === undefined) {
          numbers.push(newCourses[c].number);
        } else {
          numbers.push(newCourses[c].number + "." + newCourses[c].subnumber);
        }
        courses.push(newCourses[c]);
      }
      console.log(program.code + ": " + numbers.join(", "));

      setTimeout(function () {
        Navigation.programs(remainingPrograms, courses);
      }, llcommon.timeout);
    });
  }
}

Evaluation.getDepartmentLinksFromDepartmentDirectory = function() {
  /*
   * pull department's name and links from
   * "Departments/Programs and Courses - Undergraduate" page.
   */
  var departments = $("#sc-programlinks > ul > li > p > a");
  var d = [];
  for (var i = 0; i < departments.length; i++) {
    d.push({
      dptName: departments[i].innerHTML,
      url: departments[i].href
    });
  }
  return d;
}

Evaluation.getProgramLinksFromDepartment = function() {
  var programs = $("#sc-programlinks > ul > li > p > a");
  var p = [];
  for (var i = 0; i < programs.length; i++) {
    var values = programs[i].innerHTML.split(" - ");
    if (values.length >= 2) {
      p.push({
        code: values[0],
        programName: values[1],
        url: programs[i].href
      });
    }
  }
  return p;
}

Evaluation.getCourseLinksFromProgram = function() {
  var courses = $(".sc-child-item-links > li > a");
  var c = [];
  for (var i = 0; i < courses.length; i++) {
    var values = courses[i].innerHTML.split("&nbsp;");
    if (values.length !== 3) { continue; }
    var numbers = values[1].split("-")[0].split(".");
    var cleanedNumber = numbers[0].split(" ")
    cleanedNumber = cleanedNumber[cleanedNumber.length - 1]
    c.push({
      department: values[0].split(" ")[0],
      number: cleanedNumber,
      subnumber: numbers[1],
      course_name: values[2],
      url: courses[i].href
    });
  }
  return c;
}

Navigation.start();
