#!/usr/bin/env python
# coding: utf-8
__author__ = 'Алексей'

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'pdfupload.settings'
import django
django.setup()

import json
from time import gmtime, strftime
from subprocess import Popen, PIPE
from datetime import datetime
from workflow.analyze import analyze_signastation, analyze_colorant, analyze_platesize, analyze_complects, analyze_order
from workflow.models import Outputter, PrintingPress


# Walk into directories in filesystem
# Ripped from os module and slightly modified
# for alphabetical sorting
#
def sortedWalk(top, topdown=True, onerror=None):
    from os.path import join, isdir, islink

    names = os.listdir(top)
    names.sort()
    dirs, nondirs = [], []

    for name in names:
        if isdir(os.path.join(top, name)):
            dirs.append(name)
        else:
            nondirs.append(name)

    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        path = join(top, name)
        if not os.path.islink(path):
            for x in sortedWalk(path, topdown, onerror):
                yield x
    if not topdown:
        yield top, dirs, nondirs


def detect_outputter(pdfname):
    """
    Альтернативная версия, только для импорта
    """
    fname, fext = os.path.splitext(pdfname)
    parts = fname.lower().split("_")

    for company in Outputter.objects.all():
        if company.name.lower() in parts:
            outputter = company

    if 'outputter' not in locals():
        outputter = Outputter.objects.get(name='Admin')

    return outputter


def analyze_machine(pdfname):
    """
    Альтернативная версия, только для импорта
    Функция определяет основные параметры PDF (основываясь на первой странице файла)
    :param
        pdfname: str
         Путь к pdf файлу
    :return:
        machine - объект типа PrintingPress (or None if cant detect)
                - None, если не удалось определить
    """
    pdftotext_command = r"pdftotext '{input}' - | grep -E '({machines})'"\
        .format(input=pdfname, machines='|'.join([i.name for i in PrintingPress.objects.all()]))

    stdout = Popen(pdftotext_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()

    try:
        found_string = stdout[0].split()[0]
        if found_string == 'FS_Speedmaster':
            found_string = 'Speedmaster'
        for press in PrintingPress.objects.all():
            if found_string == press.name:
                machine = press
    except IndexError:
        primary_machines = PrintingPress.objects.filter(name__in=['Speedmaster', 'Dominant', 'Planeta'])

        # Высчитываем размер страниц в пдф
        plate_sizes = analyze_platesize(pdfname)

        # время создания файла
        mtime = os.path.getmtime(pdfname)
        timepdf = datetime.fromtimestamp(mtime)

        # предполагаем, что все страницы в ПДФ одинаковые и используем только размер первого листа
        w = plate_sizes[1][0]
        h = plate_sizes[1][1]

        # До этой даты большие форматы выводили на Планету, потом поставили Спидмастер
        sm_installed = datetime(2009, 11, 15)

        # Теперь сравниваем полученные размеры с известными
        # Сравнение можно проводить только для первой страницы, т.к все равно заливаем на одного выводильщика
        for press in primary_machines:
            if (press.plate_w == w) and (press.plate_h == h):
                machine = press

        # Если точного совпадения не найдено, тогда стоим предположения:
        if w == 1010:
            machine = PrintingPress.objects.get(name='Planeta')
        elif w == 1030:
            machine = PrintingPress.objects.get(name='Speedmaster')
        elif w == 740:
            machine = PrintingPress.objects.get(name='Dominant')
        elif w == 745:
            machine = PrintingPress.objects.get(name='Dominant')
        elif (w < 721) and (h < 521):
            machine = PrintingPress.objects.get(name='Dominant')
        else:
            if timepdf < sm_installed:
                print 'BEFORE'
                machine = PrintingPress.objects.get(name='Planeta')
            else:
                print 'AFTER'
                machine = PrintingPress.objects.get(name='Speedmaster')
    return machine


def main():
    import_path = '/mnt/oldpdf/print/2014'
    tree = sortedWalk(import_path)

    ### Что нужно для записи в базу
    # - номер заказа- из имени файла
    # - машина      - на основе размера страницы
    # - contractor  - выводильщик (если не указан, то Admin)
    # - plates      - кол-во пластин - либо HDAG тег, либо написать на основе gs
    # - complects   - кол-во комплектов
    # - created     - дата
    # - bg          - цвет полоски (может зависет от успешности каких-то этапов импорта)
    # - f           - имя файла

   #print '{}  {}\t{}\t[{}][{}]  {}  {} {}'.format(order, machine.name, outputter.name, plates, complects, created, bg, f).expandtabs(15)
    print 'Order Machine       Outputter [Pl][Cmpl] Created      Bg                Filename'
    print '--------------------------------------------------------------------------'

    with open('dump.txt', 'w') as j:
        for dir, dirs, files in tree:
            for f in files:
                if os.path.splitext(f)[1] == '.pdf':  # and (f == '1018_Gift_Snezinki-goluboy_Leonov.pdf'):

                    order = analyze_order(pdf_full_path)

                    pdf_full_path = os.path.join(dir, f)

                    mtime = os.path.getmtime(pdf_full_path)

                    created = strftime("%d %b %Y", gmtime(mtime))

                    complects = analyze_complects(pdf_full_path)

                    machine = analyze_machine(pdf_full_path)

                    if analyze_signastation(pdf_full_path):
                        plates, _ = analyze_colorant(pdf_full_path)
                        bg = 'default'
                    else:
                        # анализ кол-ва плит альтернативным методом
                        plates = 0
                        bg = 'danger'

                    outputter = detect_outputter(pdf_full_path)

                    contractor_error = ''    # код ошибки заливки файла на вывод
                    preview_error = ''       # код ошибки заливки превьюхи на кинап


                    print '{}  {}\t{}\t[{}][{}]\t{}  {}\t{}'.format(order, machine.name, outputter.name, plates, complects, created, bg, f).expandtabs(10)

                    j.write(';'.join((order, machine.name, outputter.name, str(plates), str(complects), created, bg, f, '\n')))


if __name__ == '__main__':
    main()