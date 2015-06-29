from .defaults import *

DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

INSTALLED_APPS += (
    'debug_toolbar',
)
