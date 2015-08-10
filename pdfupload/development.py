from .settings import *

DEBUG = True
TEMPLATE_DEBUG = True
IMPORT_MODE = True
TEST_MODE = False

INSTALLED_APPS += (
    'debug_toolbar',
)

if IMPORT_MODE:
    TEST_MODE = True
