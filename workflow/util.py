#!/usr/bin/python
#coding: utf-8
# __author__ = 'Алексей'

import os
import shutil
import sys
import logging
import time

from ftplib import FTP
from os.path import join
from PyPDF2 import PdfFileWriter, PdfFileReader

from models import Outputter
from models import PrintingPress


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


def fail(txt):
    """
    Help function to emergency exit with txt message
    :param txt:
    :return: none
    """
    print 'FAILED: {}'.format(txt)
    exit()


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


def error_text(status, e):
    if status:
        text = "OK"
    else:
        if e:
            text = e
        else:
            text = "Unknown error"
    return text


def crop(pdf_in, pdf_out, papers):
    """
    Параметры
    pdf_in - абсолютный путь к пдф
    pdf_out - абсолютный путь для исходящего пдф
    papers - Словарь с размерами бумаги для каждой страницы: {1: ('Speedmaster', 900, 640), 2: ('Dominant', 640, 450)}
    :return: status
    """

    status = True

    if papers == {}:
        perl_crop = "perl pdfcrop.pl {} {}".format(pdf_in, pdf_out)
        os.system(perl_crop)
        return status

    input = PdfFileReader(file(pdf_in, "rb"))
    output = PdfFileWriter()

    # Количество страниц
    pages_qty = input.getNumPages()

    for index in range(pages_qty):
        paper_machine = papers[index+1][0]
        paper_w = papers[index+1][1]
        paper_h = papers[index+1][2]

        # for m in PrintingPress._registry:
        #     if paper_machine == m.name:
        #         machine = m

        machine = None
        for i in PrintingPress.objects.all():
            if paper_machine == i.name:
                machine = i

        plate_w = machine.plate_w
        plate_h = machine.plate_h

        page = input.getPage(index)

        """ EXAMLE
        # The resulting document has a trim box that is 200x200 points
        # and starts at 25,25 points inside the media box.
        # The crop box is 25 points inside the trim box.
        print mm(page.mediaBox.getUpperRight_x()), mm(page.mediaBox.getUpperRight_y())
        page.trimBox.lowerLeft = (25, 25)
        page.trimBox.upperRight = (225, 225)
        page.cropBox.lowerLeft = (50, 50)
        page.cropBox.upperRight = (200, 200)
        """

        print 'Crop page {} to paper {}x{}'.format(index+1, paper_w, paper_h)
        page.mediaBox.lowerLeft = ((pt(plate_w - paper_w)/2), pt(machine.klapan))  # отступ слева, отступ снизу
        page.mediaBox.upperRight = (pt(paper_w + (plate_w - paper_w)/2), pt(paper_h + machine.klapan))  # ширина+отступ, высота+отступ

        output.addPage(page)

    outputstream = file(pdf_out, "wb")
    output.write(outputstream)
    outputstream.close()

    return status


def remove_outputter_title(pdfname):
    """
    Функция убирает подрядчика из имени файла (0537_Technoyug_Flier_Leonov.pdf -> 0537_Technoyug_Flier.pdf),
    затем переименовывает сам файл, и возвращает:
    :param pdfname: абсолютный путь к файлу
    :return: pdfname(string) абсолютный путь к переименованному файлу
    """

    fpath, (fname, fext) = os.path.dirname(pdfname), os.path.splitext(os.path.basename(pdfname))

    # Тут нужен unicode, потому что имя файла может содержать русские буквы,
    # и будет лажа при сравнении типа str (fname) с типом unicode (Outputter.objects.all())
    parts = unicode(fname).split("_")

    #for outputter in classes.FTP_server._dic.keys():
    #    if outputter in parts:
    #        parts.remove(outputter)

    for outputter in Outputter.objects.all():
        if outputter.name in parts:
            parts.remove(outputter.name)

    newname = join(fpath, '_'.join(parts)) + fext

    # Если подрядчик не определен, то файл не переименовывается и не перемещается
    #Для этой проверки сравнивается старое название с новым
    if pdfname != newname:
        shutil.move(pdfname, newname)

    return newname


def handle(block):
    global sizeWritten, totalSize
    sizeWritten += 1024
    percentComplete = sizeWritten * 100 / totalSize
    sys.stdout.write("{0} percent complete \r".format(percentComplete))


def sendfile(pdf_abs_path, receiver):
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

    pdfname = os.path.basename(pdf_abs_path)

    sizeWritten = 0
    totalSize = os.path.getsize(pdf_abs_path)
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
        logging.error('{} upload to {}: {}'.format(pdfname, receiver.name, e))
        print '···connect FAILED with error: {}'.format(e)
        status = False
        return status, e
    else:
        print '···connect passed'
        localfile = open(pdf_abs_path, "rb")
        try:
            ftp.set_pasv(True)
            ftp.cwd(receiver.todir)
            print 'Start uploading {} to {} ...'.format(pdfname, receiver.name)
            start = time.time()
            ftp.storbinary("STOR " + pdfname, localfile, 1024, handle)
            #print 'Size in kb ', totalSize/1024
            #print 'Time in s ', (time.time()-start)
            speed = totalSize / (time.time() - start) / 1024
            print 'Speed: {0:.1f} kB/s equivalent to {1:.2f} MBit/s'.format(speed,
                                                                            speed * 8 / 1024)
        except Exception, e:
            logging.error('{} upload to {}: {}'.format(pdfname, receiver.name, e))
            print 'upload FAILED with error: {}'.format(e)
            status = False
            return status, e
            #siteecho(pdfname, receiver.name, 'FAILED', machine, complects, html_data)
        else:
            logging.info('{} upload to {}: upload OK'.format(pdfname, receiver.name))
            print 'Upload finished OK'
            #siteecho(pdfname, receiver.name, 'Upload OK', machine, complects, html_data)
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