# coding: utf-8
from decouple import config
import os
import pdfupload.marks
from pathlib import Path

from pdfupload import marks
#
# PATH SETUP
#

BASE_DIR = Path(__file__).parent.parent

# HOME на один уровень выше, чем BASE. Я хочу, чтобы media, log и другие директории лежили *рядом* с проектом, а не внутри
HOME_DIR = BASE_DIR.parent

INPUT_PATH = str(HOME_DIR / 'input')
TEMP_PATH = str(HOME_DIR / 'tmp')

STATIC_ROOT = str(HOME_DIR / 'static_root')
STATIC_URL = '/static/'

MEDIA_ROOT = str(HOME_DIR / 'media')
MEDIA_URL = "/media/"

#LOGIN_URL = '/login_redirect'
#LOGIN_URL = '/login'

STATICFILES_DIRS =[
    'static',
    'bower_components'
]

#
# ENVIRONMENT SETUP
#

MARKS_MACHINE = marks.MARKS_MACHINE
MARKS_PAPER = marks.MARKS_PAPER
MARKS_OUTPUTTER = marks.MARKS_OUTPUTTER

SECRET_KEY = config('SECRET_KEY')
SMSC_LOGIN = config('SMSC_LOGIN')
SMSC_PASSWORD = config('SMSC_PASSWORD')
TELEGRAM_API_KEY = config('TELEGRAM_API_KEY')
TELEGRAM_CHAT_ID = config('TELEGRAM_CHAT_ID')

ALLOWED_HOSTS = ['*']

DEBUG = config('DEBUG', cast=bool)

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
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

INSTALLED_APPS = [
    #'grappelli',
    #'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_rq',
    'bootstrap3_datetime',
    'django_nvd3',
    'crispy_forms',
    'accounts',
    'technologichka',
    'stanzforms',
    'workflow',
]
if DEBUG:
    INSTALLED_APPS.insert(0, 'debug_toolbar')


MIDDLEWARE = [
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
if DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'pdfupload.urls'

WSGI_APPLICATION = 'pdfupload.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(HOME_DIR / 'log' / 'django.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose'
        },
        'userfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(HOME_DIR / 'log' / 'user.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        'workflow': {
            'handlers': ['userfile'],
            'level': 'DEBUG',
        },
    }
}


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
# Align django messages with bootstrap colors
#
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.DEBUG: 'debug',       #no color
                message_constants.INFO: 'info',         #cyan
                message_constants.SUCCESS: 'success',   #green
                message_constants.WARNING: 'warning',   #yellow
                message_constants.ERROR: 'danger',}     #red