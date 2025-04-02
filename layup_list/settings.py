import os
import dj_database_url
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ['DEBUG'] == "True"
ALLOWED_HOSTS = ['ll-prod.herokuapp.com', '.layuplist.com', 'layup-list-a10b5d7eb6ed.herokuapp.com'] if not DEBUG else ['0.0.0.0', 'localhost']
AUTO_IMPORT_CRAWLED_DATA = os.environ.get('AUTO_IMPORT_CRAWLED_DATA') == "True"

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'debug_toolbar',
    'pipeline',
    'crispy_forms',
    'crispy_bootstrap5',
    'hijack',
    'django_celery_beat',
    'django_celery_results',
    'apps.analytics',
    'apps.recommendations',
    'apps.spider',
    'apps.web',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # add whitenoise to middleware (correct whitenoise configuration in django 5)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'hijack.middleware.HijackUserMiddleware', # add hijack middleware; now required in django hijack 3.7+
]

ROOT_URLCONF = 'layup_list.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CRISPY_TEMPLATE_PACK = 'bootstrap3'

WSGI_APPLICATION = 'layup_list.wsgi.application'

HIJACK_LOGIN_REDIRECT_URL = '/recommendations/'
HIJACK_LOGOUT_REDIRECT_URL = '/eligible_for_recommendations/'
HIJACK_ALLOW_GET_REQUESTS = True
HIJACK_USE_BOOTSTRAP = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
DATABASES['default'] = dj_database_url.config()

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Crispy Forms configuration (necessary when using bootstrap5)
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = '/static/'
ROOT_ASSETS_DIR = os.path.join(BASE_DIR, 'root_assets')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), ROOT_ASSETS_DIR)
STORAGES = { # STATICFILES_STORAGE was fully deprecated in django v5.1, with this being the documentation's new recommended way to configure storage. (django-pipeline's documentation is outdated and still says to use STATICFILES_STORAGE; there's an open issue about this with updated instructions: https://github.com/jazzband/django-pipeline/issues/831)
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage', # Django's default is 'django.core.files.storage.FileSystemStorage'
    },
    'staticfiles': {
        'BACKEND': 'pipeline.storage.PipelineManifestStorage',
    },
}
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)
PIPELINE = {
    'COMPILERS': (
        'react.utils.pipeline.JSXCompiler',
    ),
    'YUGLIFY_BINARY': os.path.join(BASE_DIR, '../.heroku/vendor/node/bin/yuglify'), # this is remarkably jank but for some reason it's the only thing that works (even after trying to add to PATH in bin/pre_compile) — post_compile runs after collectstatic so it's too late to do anything
    'JAVASCRIPT': {
        'app': {
            'source_filenames': (
                'js/plugins.js',
                'js/vendor/jquery.highlight.js',
                'js/web/base.jsx',
                'js/web/common.jsx',
                'js/web/landing.jsx',
                'js/web/current_term.jsx',
                'js/web/course_detail.jsx',
                'js/web/course_review_search.jsx',
            ),
            'output_filename': 'js/app.js',
        }
    },
    'STYLESHEETS': {
        'app': {
            'source_filenames': (
                'css/web/base.css',
                'css/web/current_term.css',
                'css/web/course_detail.css',
                'css/web/course_review_search.css',
                'css/web/landing.css',
                'css/web/auth.css',
            ),
            'output_filename': 'css/app.css',
            'extra_context': {
                'media': 'screen,projection',
            },
        }
    }
}


# Email server
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = 'support@layuplist.org'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        },
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
] if not DEBUG else []


if not DEBUG:
    SERVER_EMAIL = 'support@layuplist.org'
    ADMINS = [('Support', 'support@layuplist.org')]


SESSION_COOKIE_AGE = 3153600000  # 100 years
SESSION_COOKIE_SECURE = not DEBUG


CELERY_BROKER_URL = os.environ["REDIS_URL"]
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TIMEZONE = "US/Pacific"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
