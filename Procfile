web: gunicorn layup_list.wsgi --log-file -
worker: celery -A layup_list worker -l info -B --scheduler django
