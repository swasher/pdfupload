from .settings import *

DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = False

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += (
    'debug_toolbar',
)

