"""
Imports manual json blob of dummy users

to run: python scripts/importers/import_dummy_user [OPTIONAL FILE]
"""



import os
import sys
import django
import json
from django.db import transaction

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "layup_list.settings")
django.setup()

from django.contrib.auth.models import User

from web.models import Course, Review

DEFAULT_FILENAME = "data/user/dummy_users.json"
filename = DEFAULT_FILENAME if len(sys.argv) == 1 else sys.argv[1]

with transaction.atomic():
    with open(filename) as data_file:
        dummy_users = json.load(data_file)

        for user in dummy_users:
            username = user["username"]
            password = User.objects.make_random_password()

            try:
                user = User.objects.create_user(username=username, password=password)
                print user
            except Exception as e:
                print e
                print "Failed to create user: ", username, " with password: ", password
