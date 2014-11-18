#!/usr/bin/python
#coding: utf-8
__author__ = 'Алексей'

import os
import logging
from subprocess import Popen, PIPE
from util import mm, pt, fail
from genericpath import isfile

from models import PrintingPress, Outputter


def analyze_machine(pdfname):
    """
    Функция определяет основные параметры PDF (основываясь на первой странице файла)
    :param
        pdfname: str
         Путь к pdf файлу
    :return:
        machine - объект типа PrintingPress (or None if cant detect)
        pages - кол-во страниц
    """
    machine = None

    pdftotext_command = r"pdftotext {input} - | grep -E '({machines})'"\
        .format(input=pdfname, machines='|'.join([i.name for i in PrintingPress.objects.all()]))

    pdftotext_result = Popen(pdftotext_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()

    #print '|'.join([i.name for i in PrintingPress.objects.all()])
    #print pdftotext_result
    #print pdftotext_result[0].split()[0]

    try:
        found_string = pdftotext_result[0].split()[0]
    except:
        fail('Cant detect machine')

    for press in PrintingPress.objects.all():
        if found_string == press.name:
            machine = press

    return machine


def analyze_complects(pdfname):
    pdfinfo_command = r"pdfinfo -box {0} | grep 'Page'".format(pdfname)
    pdfinfo_result = Popen(pdfinfo_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()
    pages = pdfinfo_result[0].split(" ")[10]

    """Как детектить размер страницы(только первой)
    s = pdfinfo_result[1].split(" ")
    width = s[7]
    height = s[9]
    width = mm(width)
    height = mm(height)"""

    return pages


def analyze_papersize(pdfname):
    """
    Функция возвращает словарь: {номер страницы: машина, ширина листа, высота листа}
    Если возвращается None - файл не найден
    Если возвращается пустой словарь - файл не Сигновский, нет инфы о страницах.
    :param pdfname:
    :return:
    """

    if not isfile(pdfname):
        papersizes = None
        return papersizes

    # machines должно быть вида Dominant|Speedmaster|Planeta
    pdftotext_command = r"pdftotext {input} - | grep -E '({machines})'"\
        .format(input=pdfname, machines='|'.join([i.name for i in PrintingPress.objects.all()]))

    pdftotext_result = Popen(pdftotext_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()

    papersizes = {}
    for index, value in enumerate(pdftotext_result):
        page_number = index + 1
        page_param = value.split()  # return somthing like ['Speedmaster', '900,0', 'x', '640,0']
        page_machine = page_param[0]
        page_paper_x = int(float(page_param[1].replace(',', '.')))  # В Сигне число имеет запятую вместо точки
        page_paper_y = int(float(page_param[3].replace(',', '.')))
        papersizes[page_number] = (page_machine, page_paper_x, page_paper_y)

    return papersizes


def analyze_colorant(pdfname):
    """
    :param pdfname: path to pdf file
    :return:
    total_pages(int) - количество страниц
    total_plates(int) - общее количество плит
    pdf_colors(dict) - словарь, где ключ - номер страницы, значение - список сепараций
    """
    import re

    cmd = r"cat {} | grep --binary-files=text 'HDAG_ColorantNames'".format(pdfname)
    result_strings = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE).stdout.read()

    total_plates = 0
    pdf_colors = {}

    #если не нашло ожидаемый 'HDAG_ColorantNames', то следующий if вызовет исключение
    try:
        # если pdf пересохранить в акробате, в нем нарушается структура. Проверяем:
        if result_strings.split()[0] == '/HDAG_ColorantNames':
            # ПДФ не изменялся после Сигны
            result_strings = result_strings.splitlines()
            for index, color in enumerate(result_strings):
                # Убираем из строки HDAG_ColorantNames,  знаки '/[]', разделяем
                # строку на список, убираем первый элемент (HDAG_ColorantNames)
                separations = color.translate(None, '/[]').split()[1:]

                #fix pantone names
                separations = [s.replace('#20', '_') for s in separations]

                #Создаем словарь, где ключ - номер страницы, значение - список сепараций
                pdf_colors[index+1] = separations

                total_plates += len(separations)
        else:
            # ПДФ был пересохранен в акробате
            print '===But was rewrite via Acrobat==='
            hd_pattern = re.compile(r'HDAG_ColorantNames\[(.+)\]\/HDAG_ColorantOrder')
            result_strings = hd_pattern.findall(result_strings)

            for index, color in enumerate(result_strings):
                separations = color.split('/')[1:]
                separations = [s.replace('#20', '_') for s in separations]
                pdf_colors[index+1] = separations
                total_plates += len(separations)
    except:
        pass

    return total_plates, pdf_colors


def colorant_to_string(pdf_colors):
    """
    :param pdf_colors: Это словарь, ключ - номер страницы, значение - список из строк-названий красок
    :return: short_colors: строка, краткий список красок на первом пейдже
    """
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
    parts = fname.split("_")

    for company in Outputter.objects.all():
        if company.name in parts:
            outputter = company

    if 'outputter' in locals():
        print 'Outputter successfully detected: {}'.format(outputter.name)
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

    print '\n-->Staring ink coverage calculating...'
    gs_command = r"gs -q -o - -sProcessColorModel=DeviceCMYK -sDEVICE=ink_cov {}".format(pdfname)
    gs_result = Popen(gs_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()
    print 'Ink coverage calculating finish.'

    inks = {}

    for index, s in enumerate(gs_result):
        args = s.split()[0:4]
        args = [float(x) for x in args]
        inks[index + 1] = args

    return inks