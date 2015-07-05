#!/usr/bin/python
# -- coding: utf-8 --

import os
import logging
import re
from subprocess import Popen, PIPE
from util import mm, pt, fail
from genericpath import isfile

from models import PrintingPress, Outputter
from django.conf import settings
from signamarks import mark_extraction, detect_mark


def analyze_platesize(pdfname):
    from PyPDF2 import PdfFileReader

    pdf = PdfFileReader(open(pdfname, "rb"))
    pages = pdf.pages

    plate_sizes = {}

    for index, page in enumerate(pages, 1):
        start_x, start_y = page.mediaBox.lowerLeft
        end_x, end_y = page.mediaBox.upperRight
        w = mm(end_x - start_x)
        h = mm(end_y - start_y)
        if h > w:
            w, h = h, w
        plate_sizes[index] = (w, h)

    return plate_sizes


def analyze_machine_OLD(pdfname):
    """
    DEPRECATED
    new function use direct substract from signa mark with pdfminer
    """

    """
    Функция определяет основные параметры PDF (основываясь на сигна-метке на первой странице файла)
    :param
        pdfname: Путь к pdf файлу
    :return:
        machine - объект типа PrintingPress (or None if cant detect)
                - None, если не удалось определить
    """
    pdftotext_command = r"pdftotext '{input}' - | grep -E '({machines})'"\
        .format(input=pdfname, machines='|'.join([i.name for i in PrintingPress.objects.all()]))

    stdout = Popen(pdftotext_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()

    try:
        found_string = stdout[0].split()[0]
        for press in PrintingPress.objects.all():
            if found_string == press.name:
                machine = press
    except IndexError:
        # Тут есть проблема - что делать с двумя машинами с одинаковыми форматами, например Speedmaster и FS_Speedmaster?
        # Пока в голову приходит только прибить гвоздями определенные машины, по одной для каждого формата пластин.
        # В будущем можно добавить поле какое-то в базу, типа приоритета.
        primary_machines = PrintingPress.objects.filter(name__in=['Speedmaster', 'Dominant', 'Planeta'])

        # Высчитываем размер страниц в пдф
        plate_sizes = analyze_platesize(pdfname)

        # Теперь сравниваем полученные размеры с известными
        # Сравнение можно проводить только для первой страницы, т.к все равно заливаем на одного выводильщика
        for press in primary_machines:
            if (press.plate_w == plate_sizes[1][0]) and (press.plate_h == plate_sizes[1][1]):
                machine = press

    return machine


def analyze_machine(pdfname):
    """
    Функция определяет основные параметры PDF (основываясь на сигна-метке на первой странице файла)
    :param
        pdfname: Путь к pdf файлу
    :return:
        machine - объект типа PrintingPress (or None if cant detect)
                - None, если не удалось определить
    """
    machine = None

    marks = mark_extraction(pdfname)
    machine_mark_name, machine_mark_regex = detect_mark(settings.MARKS_MACHINE, marks)

    try:
        extracted_text = marks[0][machine_mark_name][0]
        mark_content = re.findall(machine_mark_regex, extracted_text)[0]

        # TODO delete debugging
        # print('extracted_text=', extracted_text.encode('UTF-8'))
        # print('regex=',machine_mark_regex)
        # print('type result=', type(mark_content))
        # print('result=', mark_content)
        # exit()

    except KeyError, e:
        print('Файл не содержит cигновской метки {} с названием печ. машины.'.format(machine_mark_name))
        mark_content = None

    #print('\n', 'mark_with_machine_name')
    #print(extracted_text.encode('utf-8'))

    if mark_content:
        for press in PrintingPress.objects.all():
            if press.name == mark_content:
                machine = press
    else:
        print('Trying detect machine by plate size...')
        # Если первый способ провалился, пробуем определить машину, основываясь на размере пластины.

        # Тут есть проблема - что делать с двумя машинами с одинаковыми форматами, например Speedmaster и FS_Speedmaster?
        # Пока в голову приходит только прибить гвоздями определенные машины, по одной для каждого формата пластин.
        # В будущем можно добавить поле какое-то в базу, типа приоритета.
        primary_machines = PrintingPress.objects.filter(name__in=['Speedmaster', 'Dominant', 'Planeta'])

        # Высчитываем размер страниц в пдф
        plate_sizes = analyze_platesize(pdfname)

        # Теперь сравниваем полученные размеры с известными
        # Сравнение можно проводить только для первой страницы, т.к все равно заливаем на одного выводильщика
        for press in primary_machines:
            if (press.plate_w == plate_sizes[1][0]) and (press.plate_h == plate_sizes[1][1]):
                machine = press

    return machine


def analyze_signastation(pdfname):
    """
    :param pdfname: Путь к pdf-файлу
    :return: Возвращиет True, если файл создан в Heidelberg Signastation
    """
    pdfinfo_command = "pdfinfo '{}' | grep Creator | tr -s ' ' | cut -f 2 -d ' '".format(pdfname)
    stdout = Popen(pdfinfo_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().strip()
    if stdout == 'PrinectSignaStation':
        valid_signa = True
    else:
        valid_signa = False
    return valid_signa


def analyze_complects(pdfname):
    pdfinfo_command = r"pdfinfo -box '{}' | grep 'Page'".format(pdfname)
    stdout = Popen(pdfinfo_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()
    pages = stdout[0].split(" ")[10]

    """Как детектить размер страницы(только первой)
    s = stdout[1].split(" ")
    width = s[7]
    height = s[9]
    width = mm(width)
    height = mm(height)"""

    return pages


def analyze_papersize_OLD(pdfname):
    """
    DEPRECATED
    new function use direct substract from signa mark with pdfminer
    """

    """
    Функция возвращает словарь: {номер страницы: машина, ширина листа, высота листа}
    Если файл не найден, - то возвращается None
    Если файл не Сигновский, нет инфы о страницах, - то возвращается пустой словарь
    :param pdfname:
    :return:
    """

    if not isfile(pdfname):
        papersizes = None
        return papersizes

    # machines должно быть вида Dominant|Speedmaster|Planeta
    pdftotext_command = r"pdftotext '{input}' - | grep -E '({machines})'"\
        .format(input=pdfname, machines='|'.join([i.name for i in PrintingPress.objects.all()]))

    stdout = Popen(pdftotext_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()

    papersizes = {}
    # TODO enumerate(stdout, 1)
    for index, value in enumerate(stdout):
        page_number = index + 1
        page_param = value.split()  # return somthing like ['Speedmaster', '900,0', 'x', '640,0']
        page_machine = page_param[0]
        page_paper_x = int(float(page_param[1].replace(',', '.')))  # В Сигне число имеет запятую вместо точки
        page_paper_y = int(float(page_param[3].replace(',', '.')))
        papersizes[page_number] = (page_machine, page_paper_x, page_paper_y)
    return papersizes


def analyze_papersize(pdfname):
    """
    Функция возвращает словарь: {номер страницы: машина, ширина листа, высота листа}
    Если файл не найден, - то возвращается None
    Если файл не Сигновский, нет инфы о страницах, - то возвращается пустой словарь
    :param pdfname:
    :return:
    """

    print('Start analyze_papersize')
    marks = mark_extraction(pdfname)

    # todo delete
    #from pprint import pprint
    #pprint(marks)

    machine_mark_name, machine_mark_regex = detect_mark(settings.MARKS_MACHINE, marks)
    paper_mark_name, paper_mark_regex = detect_mark(settings.MARKS_PAPER, marks)

    papersizes = {}
    for page, piece_info in marks.items():
        page_number = page + 1

        # `piece_info['Machine']` возвращает список: (u'Выведено: Speedmaster', 'pssMO14_1', 'TextMark')
        # далее regex извлекает нужную нам часть метки, - имя машины или размеры бумаги

        try:
            machine = re.findall(machine_mark_regex, piece_info[machine_mark_name][0])[0]
        except KeyError:
            print('Страница {} не содержит cигновской метки {}'.format(page_number, machine_mark_name))
            machine = None

        try:
            paper = re.findall(paper_mark_regex, piece_info[paper_mark_name][0])[0]
            paper_w = int(round(float(paper[0].replace(',', '.'))))
            paper_h = int(round(float(paper[1].replace(',', '.'))))
        except KeyError:
            print('Страница не содержит cигновской метки {}'.format(paper_mark_name))
            paper_w, paper_h = None, None

        #print(page_number, machine.encode('utf-8'), paper)
        papersizes[page_number] = (machine, paper_w, paper_h)

    # todo delete
    #from pprint import pprint
    #pprint(papersizes)

    return papersizes


def analyze_colorant(pdfname):
    """
    :param pdfname: path to pdf file
    :return:
    return_total_plates(int) - общее количество плит
    pdf_colors(dict) - словарь, где ключ - номер страницы (начиная с 1), значение - список сепараций
    """
    from PyPDF2 import PdfFileReader

    pdf = PdfFileReader(open(pdfname, "rb"))
    pages = list(pdf.pages)

    return_total_plates = 0
    return_colors = {}

    # TODO enumerate(stdout, 1)
    for page, content in enumerate(pages):
        colors = content['/PieceInfo']['/HDAG_COLORANT']['/Private']['/HDAG_ColorantNames']

        #colors contain string for one page:
        #['/Magenta', '/Cyan', '/Yellow']
        #['/PANTONE#20Warm#20Red#20C', '/PANTONE#20Green#200921#20C', '/Yellow']

        #remove slash and fix pantone names
        colors = [s.replace('#20', '_') for s in colors]
        colors = [s.replace('/', '') for s in colors]

        return_colors[page+1] = colors
        return_total_plates += len(colors)

    return return_total_plates, return_colors


def colorant_to_string(pdf_colors):
    """
    :param pdf_colors: Это словарь, ключ - номер страницы, значение - список из строк-названий красок
    :return: short_colors: строка, краткий список красок на первом пейдже
    """
    if pdf_colors == '':
        return ''

    cmyk = ['Cyan', 'Magenta', 'Yellow', 'Black']

    # colors == ['PANTONE_Reflex_Blue_C', 'Cyan', 'Magenta', 'PANTONE_246_C']
    colors = pdf_colors[1]

    #убираем из пантонов слово Pantone и знаки подчеркивания
    inks = []
    for separations in colors:
        parts = separations.split("_")
        if 'PANTONE' in parts:
            parts.remove('PANTONE')
        newcolor = ''.join(parts)
        inks.append(newcolor)

    # inks == ['ReflexBlueC', 'Cyan', 'Magenta', '246C']

    replaced_colors = ''
    #если краски - только CMYK
    if set(inks) == set(cmyk):
        #то возвращаем пустую строку - в название файла никакая инфа не добавится
        # print 'only cmyk'
        short_colors = ''
    else:
        #иначе заменяем краски Cyan Magenta Yellow Black на их заглавные буквы и ставим их в начало строки
        print 'inks', inks
        for ink in cmyk:
            if ink in inks:
                inks.remove(ink)
                replaced_colors += ink[0]
        if replaced_colors:
            inks.insert(0, replaced_colors)

        # inks == ['CM', 'ReflexBlueC', '246C']

        # объеденяем список в строку через дефис и добавляем спереди подчеркивание
        short_colors = '_' + '-'.join(inks)
    return short_colors


def detect_outputter(pdfname):
    """
    Возвращает объект, соответствующий подрядчику вывода форм.
    :param pdfname: имя pdf файла
    :return: outputter (instance of FTP_server)
    """

    fname, fext = os.path.splitext(pdfname)

    # Тут нужен unicode, потому что имя файла может содержать русские буквы,
    # и будет лажа при сравнении типа str (fname) с типом unicode (Outputter.objects.all())
    # TODO лажа все равно происходит!!!
    parts = fname.encode('UTF-8').lower().split("_")

    for company in Outputter.objects.all():
        if company.name.lower() in parts:
            outputter = company

    if 'outputter' in locals():
        print 'Outputter successfully detected: {}\n'.format(outputter.name)
    else:
        print 'Outputter cant detected'
        logging.error('{0} Outputter is UNKNOWN'.format(pdfname))
        exit()

    return outputter


def detect_preview_ftp(machine):
    """
    Возвращает объект, на какой фтп заливать превью. Связь между печатной машиной и фтп
    описана в поле uploadtarget модели PrintingPress
    :param machine:
    :return:
    """
    if machine.uploadtarget == '':
        preview_ftp = None
    else:
        preview_ftp = machine.uploadtarget
    return preview_ftp


def analyze_inkcoverage(pdfname):
    """
    Анализ заполнения краски
    :param pdfname: pdfname(str)
        пусть к файлу pdf
    :return: inks(dict)
        словарь, в котором ключ - номер страницы, значение - список из четырех float цифр, в процентах
    """

    print '\n-->Starting ink coverage calculating...'
    gs_command = r"gs -q -o - -sProcessColorModel=DeviceCMYK -sDEVICE=ink_cov {}".format(pdfname)
    stdout = Popen(gs_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()
    print 'Ink coverage calculating finish.'

    inks = {}

    # TODO enumerate(stdout, 1)
    for index, s in enumerate(stdout):
        args = s.split()[0:4]
        args = [float(x) for x in args]
        inks[index + 1] = args

    return inks


def analyze_order(pdfname):
    order = re.findall("(\d+)", pdfname)[0]
    if order is None:
        order = 0
    return order