import os
import secrets

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# Due we move setting to module, we need up to three level above of this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Example using type of enveronment
#
#ENV      = os.getenv('DJANGO_ENVIRONMENT', 'development')
#DEV_ENV  = ENV == 'development'
#TEST_ENV = ENV == 'staging'
#PROD_ENV = ENV == 'production'


SECRET_KEY = secrets.SECRET_KEY
MARK_MACHINE = secrets.MARK_MACHINE


# Get home dir for tmp, input and log
from os.path import expanduser
HOME_DIR = expanduser("~")

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_rq',
    'bootstrap3_datetime',
    'workflow',
    'django_rq_dashboard',
    'django_nvd3',
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware'
)


ROOT_URLCONF = 'pdfupload.urls'

WSGI_APPLICATION = 'pdfupload.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': secrets.DATABASE_NAME,
        'USER': secrets.DATABASE_USER,
        'PASSWORD': secrets.DATABASE_PASSWORD,
        'HOST': 'localhost',
        'PORT': '',
    }
}


RQ_QUEUES = {
    'default': {
    'HOST': 'localhost',
    'PORT': 6379,
    'DB': 0,
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_L10N = True

USE_TZ = True
#USE_TZ = False


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + '/static_root/'
LOGIN_URL = '/login_redirect'

STATICFILES_DIRS = (
    BASE_DIR + '/static_root/jpg',
)

INPUT_PATH = HOME_DIR + '/input/'
TEMP_PATH = HOME_DIR + '/tmp/'

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s \t %(message)s <p>',
                    datefmt='%d/%m/%Y %H:%M',
                    filename=HOME_DIR + '/log/django_debug.log',
                    level=logging.DEBUG)

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
#             'datefmt' : "%d/%b/%Y %H:%M:%S"
#         },
#         'simple': {
#             'format': '%(levelname)s %(message)s'
#         },
#     },
#     'handlers': {
#         'filedebug': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': BASE_DIR + '/workflow/templates/debug.html',
#             'formatter': 'verbose'
#         },
#         'fileinfo': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': BASE_DIR + '/workflow/templates/info.html',
#             'formatter': 'simple'
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'propagate': True,
#             'level': 'DEBUG',
#         },
#         'pdfupload': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#         },
#     }
# }

#CRISPY_TEMPLATE_PACK = 'bootstrap3'