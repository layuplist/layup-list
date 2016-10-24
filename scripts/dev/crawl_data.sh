#!/bin/bash
# Call this from root directory of repo
# Check what this does before you call it... everytime. The parameters WILL change.
# Requires phantomjs 2.0.0

wd=$(pwd);
cd data;
phantomjs $wd/scripts/crawlers/crawl_orc_courses.js;
cd medians;
python $wd/scripts/crawlers/crawl_medians.py 14s 14x 14f 15w 15s 15x 15f 16w 16s 16x;
cd ../terms;
phantomjs $wd/scripts/crawlers/crawl_term.js 2017 W;
cd $wd
python scripts/crawlers/crawl_course_pages.py
