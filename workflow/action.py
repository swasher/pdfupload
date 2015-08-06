#!/usr/bin/python
# -- coding: utf-8 --

import os
import sys
import tempfile
import subprocess
import shutil
import smsc_api
import logging
import time

from subprocess import call
from models import Outputter
from PyPDF2 import PdfFileWriter, PdfFileReader
from django.utils import timezone
from util import pt
from util import reduce_image
from util import get_jpeg_path
from util import colorant_to_string
from util import sendfile
from util import error_text
from util import dict_to_multiline
from util import inks_to_multiline

from models import Grid

def remove_outputter_title(pdf):
    """
    Функция убирает подрядчика из имени файла (0537_Technoyug_Flier_Leonov.pdf -> 0537_Technoyug_Flier.pdf),
    затем переименовывает сам файл, и возвращает новое имя
    :param pdf: объект pdf
    :return: none
    """

    #fpath, (fname, fext) = os.path.dirname(pdf.abspath), os.path.splitext(os.path.basename(pdf.abspath))

    # Тут нужен unicode, потому что имя файла может содержать русские буквы,
    # и будет лажа при сравнении типа str (fname) с типом unicode (Outputter.objects.all())
    name, ext = os.path.splitext(pdf.name)
    parts = name.decode('UTF-8').split("_")

    for outputter in Outputter.objects.all():
        if outputter.name in parts:
            parts.remove(outputter.name)

    newname = '_'.join(parts) + ext
    newpath = os.path.join(pdf.tmpdir, newname)

    # Если подрядчик в имени файла не обнаружен, то файл не переименовывается и не перемещается
    # Для этой проверки сравнивается старое название с новым
    if pdf.name != newname:
        #.decode('UTF-8')
        print('-->Rename:')
        print('····{} --> {}'.format(os.path.basename(pdf.name), os.path.basename(newpath)))
        os.rename(pdf.abspath, newpath)
        pdf.name = newname


def crop(pdf):
    """
    Кропит страницы pdf до размеров бумаги. Если размеры бумаги неизвестны, кропит пустые поля.
    Объект типа файл схраняется в свойство pdf.cropped_file.
    :param pdf: объект pdf
    :return: status
    """
    status = True
    pdf.cropped_file = tempfile.NamedTemporaryFile(mode='w+b', dir=pdf.tmpdir, suffix='.pdf', delete=False)

    print('\n-->Cropping:')

    if pdf.paper_sizes:
        input = PdfFileReader(file(pdf.abspath, "rb"))
        output = PdfFileWriter()

        for index in range(1, pdf.complects + 1):
            paper_machine = pdf.paper_sizes[index][0]
            paper_w = pdf.paper_sizes[index][1]
            paper_h = pdf.paper_sizes[index][2]

            plate_w = pdf.machines[index].plate_w
            plate_h = pdf.machines[index].plate_h

            page = input.getPage(index-1)

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

            print '····page {} to paper {}x{}'.format(index, paper_w, paper_h)
            page.mediaBox.lowerLeft = ((pt(plate_w - paper_w)/2), pt(pdf.machines[index].klapan))  # отступ слева, отступ снизу
            page.mediaBox.upperRight = (pt(paper_w + (plate_w - paper_w)/2), pt(paper_h + pdf.machines[index].klapan))  # ширина+отступ, высота+отступ

            output.addPage(page)

        outputstream = file(pdf.cropped_file.name, "wb")
        output.write(outputstream)
        outputstream.close()
        pdf.cropped_file.close()

    else:
        perl_crop = "perl pdfcrop.pl {} {}".format(pdf.abspath, pdf.cropped_file.name)
        status = os.system(perl_crop)

    if not status:
        print('Cropping failed with status: {}'.format(status))

    return status


def compress(pdf):
    """
    Функция берет кропленный файл и уменьшает разрешение картинок.
    Объект типа файл схраняется в свойство pdf.compressed_file.
    :param pdf:
    :return:
    """
    resolution = 150

    pdf.compressed_file = tempfile.NamedTemporaryFile(mode='w+b', dir=pdf.tmpdir, suffix='.pdf', delete=False)

    gs_compress = "gs -sDEVICE=pdfwrite -dDownsampleColorImages=true " \
                  "-dColorImageResolution={resolution} -dCompatibilityLevel=1.4 " \
                  "-dNOPAUSE -dBATCH -sOutputFile={output} {input} | grep 'Page'" \
                  .format(input=pdf.cropped_file.name, output=pdf.compressed_file.name, resolution=resolution)

    print '\n-->Starting PDF preview compression...'

    try:
        retcode = call(gs_compress, shell=True, stdout=subprocess.PIPE)
        if retcode > 0:
            print >>sys.stderr, "Compressing failed with error: {}".format(retcode)
    except OSError as e:
        print >>sys.stderr, "Compressing failed:", e

    print 'Compression ok.'


def generating_jpeg(pdf):
    """
    Функция создает два джипега из обрезанного PDF-а, большой (proof) и маленький (thumb)
    Сохраняет их в директории jpeg_path, которая основывается на settings.MEDIA_ROOT.
    Пути к файлам, которые сохранятся в базе, должны быть относительные от settings.MEDIA_ROOT.
    pdf.jpeg_file - полноразмерный jpg первой страницы, генерируется gs. Уничтожается в конце фунции.
    pdf.jpeg_proof - уменьшенный джипег, показывается по нажатию на "глаз" в интерфейсе
    pdf.jpeg_thumb - совсем маленький джипег, показывается по наведению на "глаз" в интерфейсе
    :param pdf:
    :return:
    """
    name, _ = os.path.splitext(pdf.name)

    # Относительный (от settings.MEDIA_ROOT) и абсулютный путь, куда сохранять джипеги
    jpeg_path_rel, jpeg_path_abs = get_jpeg_path()

    # для сохранения в базу нам нужно относительные пути
    pdf.jpeg_proof = os.path.join(jpeg_path_rel, name + '.jpg')
    pdf.jpeg_thumb = os.path.join(jpeg_path_rel, name + '_thumb.jpg')

    # а для дальнейших файловых операций - абсолютные
    jpeg_file = tempfile.NamedTemporaryFile(mode='w+b', dir=pdf.tmpdir, suffix='.jpg', delete=False)
    jpeg_proof = os.path.join(jpeg_path_abs, name + '.jpg')
    jpeg_thumb = os.path.join(jpeg_path_abs, name + '_thumb.jpg')

    gs_compress = "gs -sDEVICE=jpeg -dFirstPage=1 -dLastPage=1 -dJPEGQ=80 -r{resolution}"\
                  "-dNOPAUSE -dBATCH -sOutputFile={output} {input} " \
                  .format(resolution='200', input=pdf.compressed_file.name, output=jpeg_file.name)

    print '\n-->Starting Jpeg preview compression'
    print '····make full resolution jpg'
    os.system(gs_compress)
    print '····downsample to thumb'
    reduce_image(jpeg_file.name, jpeg_proof, 2500)
    print '····downsample to preview'
    reduce_image(jpeg_file.name, jpeg_thumb, 175)
    print 'compression finished.'
    os.unlink(jpeg_file.name)


def custom_operations(pdf):
    """
    У выводильщика могут быть особенные требования к файлу.
    :param pdf:
    :return:
    """
    if pdf.outputter.name == 'Leonov':
        """
        Леонов хочет, чтобы файл попадал в разные папки на фтп, в зависимости от формата пластин.
        Проверку производим только для первого комплекта (хотя в пдф теоретически могут быть формы на разные машины)
        """
        if pdf.machines[1].name == 'Speedmaster':
            pdf.outputter.ftp_account.todir = '_1030x770'
        elif pdf.machines[1].name == 'Planeta':
            pdf.outputter.ftp_account.todir = '_1010x820'
        elif pdf.machines[1].name == 'Dominant':
            pdf.outputter.ftp_account.todir = '_ADAST'
        else:
            pdf.outputter.ftp_account.todir = ''


    if pdf.outputter.name == 'Korol':
        # may be rotate90?
        """
        Король просит добавлять в имя файла названия красок.
        """

        # add numper of plates to pdf name
        colorstring = colorant_to_string(pdf.colors)

        print('colorstring=', colorstring)
        print('pdf.machines=', pdf.machines)

        #add label representing paper width for Korol
        #если файл не сигновский, то colorstring=None, цвета не определяются

        name, ext = os.path.splitext(pdf.name)

        # TODO Тут объеденяется string и unicode. Не будет работать для русских названий файлов.
        if colorstring:
            newname = name + '_' + str(pdf.machines[1].plate_w) + '_' + str(pdf.plates) + 'Plates' + colorstring + ext
        else:
            newname = name + '_' + str(pdf.machines[1].plate_w) + ext

        shutil.move(pdf.abspath, os.path.join(pdf.tmpdir, newname))
        pdf.name = newname


# TODO Эти две функции - бесполезные обертки вокруг sendfile.
# TODO Это надо отрефакторить, чтобы sendfile принимал нужные аргуметны (в частности, фтп), и возвращал статус
# TODO и переписать код, чтобы статусы напрямую возвращалсиь из sendfile

def upload_to_press(pdf):
    """
    Отсылает обрезанный и сжатый файл на фтп печатной машины
    :param pdf:
    :return:
    """
    if os.path.isfile(pdf.compressed_file.name):
        if pdf.machines[1].uploadtarget:
            pdf.upload_to_machine_status, pdf.upload_to_machine_error = sendfile(pdf, pdf.machines[1].uploadtarget)
        else:
            pdf.upload_to_machine_status, pdf.upload_to_machine_error = False, "Unknown press or missing ftp credentials"
    else:
        print 'Uploading: compressed file not found'
        pdf.upload_to_machine_status, pdf.upload_to_machine_error = False, 'Preview not found'


def upload_to_outputter(pdf):
    """
    Отсылает файл на вывод
    :param pdf:
    :return:
    """
    if os.path.isfile(pdf.abspath):
        if pdf.outputter.ftp_account:
            pdf.upload_to_outputter_status, pdf.upload_to_outputter_error = sendfile(pdf, pdf.outputter.ftp_account)
        else:
            pdf.upload_to_outputter_status, pdf.upload_to_outputter_error = False, "Missing ftp credentials"
    else:
        print 'Uploading: PDF file not found'
        pdf.upload_to_outputter_status, pdf.upload_to_outputter_error = False, 'PDF not found'


def send_sms(pdf):
    """
    Отсылается смс. Получатель определяется по полю outputter.sms_receiver
    :param pdf:
    :return:
    """
    print('\n--> SMS:')
    try:
        if pdf.upload_to_outputter_status:
            smsc = smsc_api.SMSC()
            phone = pdf.outputter.sms_receiver.phone
            message = '{} {} вывод {} пл.{}'.format(pdf.name, pdf.machine[1].name, pdf.outputter.name, str(pdf.plates))
            status = smsc.send_sms(phone, message)
            #TODO вываливается эксепшн, если нет status'а. Временно тупо обернул в try
            try:

                print('····send to {} with status: {}'.format(pdf.outputter.sms_receiver.name, status))
                print('····text: {}'.format(message))
            except Exception, e:
                print 'error:', e
    except Exception, e:
        logging.error('Send sms exception: {0}'.format(e))
        print '····FAILED. probably, no phone number'


def save_bd_record(pdf):
    """
    Данные, собранные о pdf, сохраняются в базу данных
    :param pdf:
    :return:
    """
    contractor_error = error_text(pdf.upload_to_outputter_status, pdf.upload_to_outputter_error)
    preview_error = error_text(pdf.upload_to_machine_status, pdf.upload_to_machine_error)
    if not pdf.upload_to_outputter_status:
        bg = 'danger'
    elif not pdf.upload_to_machine_status:
        bg = 'warning'
    else:
        bg = 'default'

    # a = timezone.now()
    # print a
    # print type(a)
    # exit('stop')

    print('\n--> Save into database:')

    try:
        row = Grid()
        row.order = pdf.order
        row.datetime = timezone.now()
        row.pdfname = os.path.splitext(pdf.name)[0]
        row.machine = pdf.machines[1]
        row.total_pages = pdf.complects
        row.total_plates = pdf.plates
        row.contractor = pdf.outputter
        row.contractor_error = contractor_error
        row.preview_error = preview_error
        row.colors = dict_to_multiline(pdf.colors)
        row.inks = inks_to_multiline(pdf.inks)
        row.bg = bg
        row.proof = pdf.jpeg_proof
        row.thumb = pdf.jpeg_thumb
        # print 'row.order', row.order
        # print 'row.datetime', row.datetime
        # print 'row.pdfname', row.pdfname
        # print 'row.machine', row.machine
        # print 'row.total_pages', row.total_pages
        # print 'row.total_plates', row.total_plates
        # print 'row.contractor', row.contractor
        # print 'row.contractor_error', row.contractor_error
        # print 'row.preview_error', row.preview_error
        # print 'row.colors', row.colors
        # print 'row.inks', row.inks
        # print 'row.bg', row.bg
        # print 'row.proof', row.proof
        # print 'row.thumb', row.thumb
        row.save()
        print '····ok'
    except Exception, e:
        print('····FAILED: {}'.format(e))


def cleaning_temps(pdf):
    """
    Очистка временных файлов
    :param pdf:
    :return:
    """
    print('\n--> Cleaning up:')
    try:
        os.unlink(pdf.abspath)
        os.unlink(pdf.cropped_file.name)
        os.unlink(pdf.compressed_file.name)
        shutil.rmtree(pdf.tmpdir)
        print '····ok'
    except Exception, e:
        print '····FAILED: {}'.format(e)