from .settings import *

DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = True

INSTALLED_APPS += (
    'debug_toolbar',
)

INTERNAL_IPS = '172.28.128.1'
