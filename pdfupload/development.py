from .settings import *

DEBUG = True
TEMPLATE_DEBUG = True
IMPORT_MODE = False
TEST_MODE = True

INSTALLED_APPS += (
    'debug_toolbar',
)

if IMPORT_MODE:
    TEST_MODE = True

INTERNAL_IPS = '172.28.128.1'
