#!/bin/bash
# Call this from root directory of repo
# Check what this does before you call it... everytime. The parameters WILL change.
# Requires phantomjs 2.0.0

wd=$(pwd);
cd data/terms;
phantomjs $wd/scripts/crawlers/crawl_term.js 2017 W;
cd $wd
