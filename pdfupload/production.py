# coding: utf-8

from .settings import *

DEBUG = False
TEMPLATE_DEBUG = False
IMPORT_MODE = False
TEST_MODE = False

ALLOWED_HOSTS = ['*']

if IMPORT_MODE:
    TEST_MODE = True


# TEST_MODE - файлы не отсылаются на фтп
# IMPORT_MODE - получаемые файлы только вносятся в базу, не отсылаются, дата берется как дата создания файла.