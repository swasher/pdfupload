#!/usr/bin/env python
# coding: utf-8
__author__ = 'Алексей'

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'pdfupload.settings'
import django
django.setup()

from workflow.models import Grid, PrintingPress, Ctpbureau
import time
from datetime import datetime

def main():

    with open('dump.txt', 'r') as j:
        for line in j:
            if ';' in line:
                order, machinetext, outputtertext, plates, complects, created, bg, f, _ = line.strip().split(';')
                # print 'order', order
                # print 'machinetext', machinetext
                # print 'outputter', outputter
                # print 'plates', plates
                # print 'complects', complects
                # print 'created', created
                # print 'bg', bg, '\n'

                date = datetime.strptime(created, "%d %b %Y")

                for press in PrintingPress.objects.all():
                    if machinetext == press.name:
                        machine = press

                for contractor in Ctpbureau.objects.all():
                    if outputtertext == contractor.name:
                        outputter = contractor

                try:
                    row = Grid()
                    row.order = int(order)
                    row.datetime = date
                    row.pdfname = f
                    row.machine = machine
                    row.total_pages = int(complects)
                    row.total_plates = int(plates)
                    row.contractor = outputter
                    row.contractor_error = 'IMPORTED'
                    row.preview_error = 'OK'
                    row.colors = ''
                    row.inks = ''
                    row.bg = bg
                    # print 'row.datetime', row.datetime
                    print 'row.pdfname', row.pdfname
                    # print 'row.machine', row.machine
                    # print 'row.total_pages', row.total_pages
                    # print 'row.total_plates', row.total_plates
                    # print 'row.contractor', row.contractor
                    # print 'row.contractor_error', row.contractor_error
                    # print 'row.preview_error', row.preview_error
                    # print 'row.colors', row.colors
                    # print 'row.inks', row.inks
                    # print 'row.bg', row.bg, '\n'
                    row.save()
                except Exception, e:
                    print 'ERROR save: file {}, Exception {}'.format(f, e)





if __name__ == '__main__':
    main()