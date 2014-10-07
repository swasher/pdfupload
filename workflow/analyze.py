#!/usr/bin/python
#coding: utf-8
__author__ = 'Алексей'

import os
import logging
from subprocess import Popen, PIPE
from util import mm, pt
from genericpath import isfile

from models import PrintingPress, Outputter


def analyze(pdfname):
    """
    Функция определяет основные параметры PDF (основываясь на первой странице файла)
    :param
        pdfname: str
         Путь к pdf файлу
    :return:
        machine - объект типа PrintingPress (or None if cant detect)
        pages - кол-во страниц
    """

    pdfinfo_command = r"pdfinfo -box {0} | grep 'Page'".format(pdfname)
    pdfinfo_result = Popen(pdfinfo_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()

    pages = pdfinfo_result[0].split(" ")[10]

    s = pdfinfo_result[1].split(" ")
    width = s[7]
    height = s[9]
    width = mm(width)
    height = mm(height)

    # Итерируем по всем записям модели PrintingPress, если у очередной записи
    # совпадают ширина и высота пластины с шириной и высотой первого листа pdf,
    # тогда копируем эту запись в переменную machine

    machine = None
    for press in PrintingPress.objects.all():
        if width == press.plate_w and height == press.plate_h:
            machine = press

    # machine = None
    # for press in classes.PrintingPress._registry:
    #     if width == press.plate_w and height == press.plate_h:
    #         machine = classes.PrintingPress._dic[press.name]

    return machine, pages


def analyze_papersize(pdfname):
    """
    Функция возвращает словарь, в котором ключ - номер страницы, значения: машина, ширина листа, высота листа.
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
        .format(input=pdfname, machines='|'.join([i.name for i in
                                                  PrintingPress.objects.all()]))

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
    cmd = r"cat {} | grep --binary-files=text 'HDAG_ColorantNames'".format(pdfname)
    result_strings = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()

    total_plates = 0
    #total_pages = len(result_strings)
    pdf_colors = {}
    for index, color in enumerate(result_strings):
        # Убираем из строки HDAG_ColorantNames занки '/[]', разделяем
        # строку на список, убираем первый элемент (HDAG_ColorantNames)
        separations = color.translate(None, '/[]').split()[1:]
        total_plates += len(separations)

        #fix pantone names
        separations = [s.replace('#20', '_') for s in separations]

        #Создаем словарь, где ключ - номер страницы, значение - список сепараций
        pdf_colors[index+1] = separations
    return total_plates, pdf_colors


def analyze_colorant_korol(pdfname):
    """
    Генерирует строку для Короля, с краткими именами красок на первой странице пдф'а
    :param pdfname: path to pdf file
    :return:
    short_colors(string)
    """
    cmd = r"cat {} | grep --binary-files=text 'HDAG_ColorantNames'".format(pdfname)
    result_strings = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()

    separations = result_strings[0].translate(None, '/[]').split()[1:]
    #fix pantone names
    separations = [s.replace('#20', '_') for s in separations]
    l = []
    for colors in separations:
        parts = colors.split("_")
        if 'PANTONE' in parts:
            parts.remove('PANTONE')
        newcolor = ''.join(parts)
        l.append(newcolor)

    short_colors = '-'.join(l)
    if short_colors == 'Black-Cyan-Magenta-Yellow':
        short_colors = ''
    else:
        short_colors = '_'+short_colors

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