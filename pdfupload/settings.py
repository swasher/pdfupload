# coding: utf-8

import os
import secrets
import marks
from os.path import join

#
# PATH SETUP
#

# BASE_DIR two levels upper than settings.py

# default BASE_DIR buggy for me - __file__ return relative path instead absolute
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# look discussion here - https://code.djangoproject.com/ticket/21409 (espesially comment 5 and 6)
# and here - http://stackoverflow.com/a/7116925/1334825
# but probably it will be work fine in python3

p = os.path
BASE_DIR = p.abspath(p.normpath(p.join(p.dirname(__file__), p.pardir)))

# HOME на один уровень выше, чем BASE. Я хочу, чтобы media, log и другие директории лежили *рядом* с проектом, а не внутри
HOME_DIR = os.path.dirname(BASE_DIR)

INPUT_PATH = HOME_DIR + '/input/'
TEMP_PATH = HOME_DIR + '/tmp/'

STATIC_ROOT = BASE_DIR + '/static_root/'
STATIC_URL = '/static/'

MEDIA_ROOT = HOME_DIR + '/media/'
MEDIA_URL = "/media/"

LOGIN_URL = '/login_redirect'

#
# ENVIRONMENT SETUP
#

TTY = secrets.TTY

SECRET_KEY = secrets.SECRET_KEY
MARKS_MACHINE = marks.MARKS_MACHINE
MARKS_PAPER = marks.MARKS_PAPER
MARKS_OUTPUTTER = marks.MARKS_OUTPUTTER

DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []



#
# APPLICATION SETUP
#

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',               # for using `request` in templates, in particular, redirect to rq_dashboard
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


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
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_L10N = True
USE_TZ = True
#USE_TZ = False



#
# LOGGING SETUP
#


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


#
# LOAD SERVER-DEPENDING SETTINGS
#

ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

DEV_ENV  = ENVIRONMENT == 'development'
TEST_ENV = ENVIRONMENT == 'staging'
PROD_ENV = ENVIRONMENT == 'production'

if PROD_ENV:
    from production import *
elif TEST_ENV:
    from staging import *
elif DEV_ENV:
    from development import *