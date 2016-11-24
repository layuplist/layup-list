#!/bin/bash
# Call this from root directory of repo

python manage.py migrate

# import reviews
# python scripts/importers/import_layups_as_reviews.py
python scripts/importers/import_reviews.py

# compute the initial scorings
python scripts/compute/compute_initial_scores.py
