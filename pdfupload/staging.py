from .settings import *

DEBUG = False
TEMPLATE_DEBUG = False
IMPORT_MODE = True
TEST_MODE = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += (
    'debug_toolbar',
)

if IMPORT_MODE:
    TEST_MODE = True
