#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Алексей'

import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdfupload.settings")
#from django.conf import settings

import django_rq
import workflow.views

pdfName = sys.argv[1]

# Если не поставить timeout, то на больших файлах, которые долго крутятся, будет вываливаться ошибка
# JobTimeoutException: Job exceeded maximum timeout value (180 seconds).
django_rq.enqueue(workflow.views.processing, pdfName, timeout=3600)