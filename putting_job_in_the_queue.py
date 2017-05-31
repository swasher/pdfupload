#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Алексей'

import os
import sys
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'pdfupload.settings'
django.setup()

import django_rq
from workflow.views import processing

pdfName = sys.argv[1]

# Если не поставить timeout, то на больших файлах, которые долго крутятся, будет вываливаться ошибка
# JobTimeoutException: Job exceeded maximum timeout value (180 seconds).
django_rq.enqueue(processing, pdfName, timeout=3600)