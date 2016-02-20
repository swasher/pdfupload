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

STATIC_ROOT = HOME_DIR + '/static_root/'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    BASE_DIR + '/static',
)

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
SMSC_LOGIN = secrets.SMSC_LOGIN
SMSC_PASSWORD = secrets.SMSC_PASSWORD

ALLOWED_HOSTS = []

#
# APPLICATION SETUP
#

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
            'templates',
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

INSTALLED_APPS = [
    'grappelli',
    #'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_rq',
    'bootstrap3_datetime',
    'django_rq_dashboard',
    'django_nvd3',
    'crispy_forms',
    'accounts',
    'technologichka',
    'stanzforms',
    'workflow',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware'
]

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


#
# INTERNATIONALIZATION AND TZ
#

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_L10N = True
USE_TZ = False


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
# BATTARIES CONFIG
#

CRISPY_TEMPLATE_PACK = 'bootstrap3'

SUIT_CONFIG = {
    # header
    'ADMIN_NAME': 'Технологичка онлайн',
    # 'HEADER_DATE_FORMAT': 'l, j. F Y',
    # 'HEADER_TIME_FORMAT': 'H:i',

    # forms
    # 'SHOW_REQUIRED_ASTERISK': True,  # Default True
    # 'CONFIRM_UNSAVED_CHANGES': True, # Default True

    # menu
    # 'SEARCH_URL': '/admin/auth/user/',
    # 'MENU_ICONS': {
    #    'sites': 'icon-leaf',
    #    'auth': 'icon-lock',
    # },
    # 'MENU_OPEN_FIRST_CHILD': True, # Default True
    # 'MENU_EXCLUDE': ('auth.group',),
    'MENU': (
        #'sites',
        {'app': 'rept', 'label': 'Технологички', 'icon': 'icon-cog', 'models': ('order',)},
        '-',
        {'label': 'Контрагенты', 'models': ('rept.customer', 'rept.contractor')},
        {'label': 'Словари', 'models': ('rept.printingpress', 'rept.operationlist')},
    ),

    # misc
    # 'LIST_PER_PAGE': 15
}



#
# LOAD SERVER-DEPENDING SETTINGS
#

SERVER_TYPE = os.getenv('SERVER_TYPE')

DEV_ENV  = SERVER_TYPE == 'development'
TEST_ENV = SERVER_TYPE == 'staging'
PROD_ENV = SERVER_TYPE == 'production'

if PROD_ENV:
    from production import *
elif TEST_ENV:
    from staging import *
elif DEV_ENV:
    from development import *

