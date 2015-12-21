#!/bin/bash
# Call this from root directory of repo
# Check what this does before you call it... everytime. The parameters WILL change.
# Requires phantomjs 2.0.0

wd=$(pwd);
cd data;
phantomjs $wd/scripts/crawlers/crawl_undergraduate_courses.js;
cd medians;
phantomjs $wd/scripts/crawlers/crawl_medians.js 13x 13f 14w 14s 14x 14f 15w 15s 15x 15f;
cd ../terms;
phantomjs $wd/scripts/crawlers/crawl_term.js 2016 1;
