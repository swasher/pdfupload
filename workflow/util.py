#!/usr/bin/python
#coding: utf-8
# __author__ = 'Алексей'

import os
import sys
import logging
import time
import subprocess

from datetime import datetime
from django.conf import settings
from ftplib import FTP


def mm(points):
    """
    Convert postscript points to millimetres. 1 pt = 25.4/72 mm
    :param points: (float) points
    :return: (float) millimetres
    """
    return int(round(float(points)/72*25.4))


def pt(mm):
    """
    :param mm: (float)
    :return: points (float)
    """
    return int(float(mm)*72/25.4)


def dict_to_multiline(dic):
    """
    Функция преобразует словарь в текстовый объект, где каждая строка вида key: value1 value.
    Используется, например, для вывода колоранотов в html
    :param dic(dic): словарь
    :return: text(str)
    """
    text = ''
    try:
        for k, v in dic.iteritems():
            text += str(k)+': '
            for i in v:
                text += i + ' '
            text += "\n"
    except AttributeError:
        # исключение возникает, если файл не сигновский. dic в этом случае - пустая строка
        # возвращается также пустая строка
        pass
    return text


def inks_to_multiline(dic):
    """
    Аналог функции dict_to_multiline, но адаптированная для ink coverage
    :param dic(dic): словарь
    :return: text(str)
    """
    text = ''
    for k, v in dic.iteritems():
        text += str(k)+': '
        text += "C{:.1f}% M{:.1f}% Y{:.1f}% B{:.1f}%".format(v[0], v[1], v[2], v[3])
        text += "\n"
    return text


def handle(block):
    global sizeWritten, totalSize
    sizeWritten += 1024
    percentComplete = sizeWritten * 100 / totalSize
    sys.stdout.write("{0} percent complete \r".format(percentComplete))


def sendfile(pdf, receiver):
    """
    Функция выполняет заливку на фтп
    :param pdf_abs_path:str Путь к файлу (абсолютный)
    :param receiver:Ftp Объект получателя, список получателей в файле ftps, объекты
    формируются из файла функцией -==-
    :return: status:boolean - флаг удачного завершения
                e:exception - код ошибки
    """
    global sizeWritten, totalSize

    status = True
    e = None

    sizeWritten = 0
    totalSize = os.path.getsize(pdf.abspath)
    #print 'name:',receiver.name
    #print 'ip:',receiver.ip
    #print 'port:',receiver.port,  type(receiver.port)
    #print 'login:',receiver.login
    #print 'pass:',receiver.passw
    print '\n-->Try connect to {}...'.format(receiver.name)
    try:
        ftp = FTP()
        ftp.connect(receiver.ip, port=receiver.port, timeout=20)  # timeout is 15 seconds
        ftp.login(receiver.login, receiver.passw)
    except Exception, e:
        logging.error('{} upload to {}: {}'.format(pdf.name, receiver.name, e))
        print '···connect FAILED with error: {}'.format(e)
        status = False
        return status, e
    else:
        print '···connect passed'
        localfile = open(pdf.abspath, "rb")
        try:
            ftp.set_pasv(True)
            ftp.cwd(receiver.todir)
            print 'Start uploading {} to {} ...'.format(pdf.name, receiver.name)
            start = time.time()
            if settings.TEST_MODE:
                print('SKIPPING UPLOAD')
            else:
                ftp.storbinary("STOR " + pdf.name, localfile, 1024, handle)
            #print 'Size in kb ', totalSize/1024
            #print 'Time in s ', (time.time()-start)
            speed = totalSize / (time.time() - start) / 1024
            print 'Speed: {0:.1f} kB/s equivalent to {1:.2f} MBit/s'.format(speed, speed * 8 / 1024)
        except Exception, e:
            logging.error('{} upload to {}: {}'.format(pdf.name, receiver.name, e))
            print 'upload FAILED with error: {}'.format(e)
            status = False
            return status, e
            #siteecho(pdf.name, receiver.name, 'FAILED', machine, complects, html_data)
        else:
            logging.info('{} upload to {}: upload OK'.format(pdf.name, receiver.name))
            print 'Upload finished OK'
            #siteecho(pdf.name, receiver.name, 'Upload OK', machine, complects, html_data)
        finally:
            localfile.close()
    finally:
        ftp.close()

    return status, e


def error_text(status, e):
    if status:
        text = "OK"
    else:
        if e:
            text = e
        else:
            text = "Unknown error"
    return text


def reduce_image(infile, outfile, new_width):
    """
    Эта функция пропорционально уменьшает изображение до ширины width
    :param source: путь к исходному изображению
    :param target: путь к уменьшенному изображению
    :param width: до какой ширины уменьшать (в пикселах)
    :return:
    """
    from PIL import Image

    if infile != outfile:
        try:
            im = Image.open(infile)
            height, width = im.size
            new_height = new_width * height / width
            im = im.resize((new_height, new_width), Image.ANTIALIAS)
            im.save(outfile)
        except IOError, e:
            print("cannot create thumbnail for {} with exception: {}".format(infile, e))


def colorant_to_string(pdf_colors):
    """
    :param pdf_colors: Это словарь, ключ - номер страницы, значение - список из строк-названий красок
    :return: short_colors: строка, краткий список красок на первом пейдже
    """
    if not pdf_colors :
        return None

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


def get_jpeg_path():
    """
    Джипеги хранятся в директориях соответственно их году. Фунцкция убеждается, что эта директория существует,
    и возвращает путь на нее
    proof_subpath - путь от setting.MEDIA_ROOT - это значение сохраняется в базе
    proof_path - абсолютный путь
    :param pdf:
    :return:
    """
    current_year = str(datetime.now().year)
    proof_subpath = os.path.join('proof', current_year)
    proof_path = os.path.join(settings.MEDIA_ROOT, proof_subpath)
    if not os.path.exists(proof_path):
        os.makedirs(proof_path)
    return proof_subpath, proof_path


def get_bbox(fname):
    """
    Функция определяет координаты значимого изображения. С помощью этих координат можно обрезать белые поля.
    Функция возвращает словарь, где ключ - номер страницы, значения - список bbox [x1, y1, x2, y2] -
    координаты нижнего левого и верхнего правого углов изображения в пунктах.
    """
    args = ["gs"]
    args += ["-o", "%stdout%"]
    args += ["-dQUIET"]
    args += ["-sDEVICE=bbox"]
    args += ["-f", fname]

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout_data, stderr_data) = p.communicate(None)

    # remove %%BoundingBox, retain only %%HiResBoundingBox
    gs_result = stderr_data.splitlines()
    cleaned_result = [x for x in gs_result if '%%HiResBoundingBox' in x]

    bbox = {}
    for num, line in enumerate(cleaned_result, 1):
        data = line.split()
        if data[0] == "%%HiResBoundingBox:":
            bbox[num] = [ float(s) for s in data[1:5] ]

    return bbox