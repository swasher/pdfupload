#!/usr/bin/python
# -- coding: utf-8 --

import os
import tempfile
import subprocess
import shutil
import smsc_api
import logging
import shelve

from django.conf import settings
from subprocess import call
from models import Outputter
from models import Grid
from PyPDF2 import PdfFileWriter, PdfFileReader
from util import pt, mm
from util import reduce_image
from util import get_jpeg_path
from util import colorant_to_string
from util import sendfile
from util import error_text
from util import dict_to_multiline
from util import inks_to_multiline
from util import get_bbox

logger = logging.getLogger(__name__)

def remove_outputter_title(pdf):
    """
    Функция убирает подрядчика из имени файла (0537_Technoyug_Flier_Leonov.pdf -> 0537_Technoyug_Flier.pdf),
    затем переименовывает сам файл, и возвращает новое имя
    :param pdf: объект pdf
    :return: none
    """

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
    if pdf.name != newname:
        logger.info('')
        logger.info('――>Rename:')
        logger.info('····{} ――> {}'.format(os.path.basename(pdf.name), os.path.basename(newpath)))
        os.rename(pdf.abspath, newpath)
        pdf.name = newname


def crop(pdf):
    """
    Кропит страницы pdf до размеров бумаги. Если размеры бумаги неизвестны, то высчитывает поля с помощью
    ghostscript bbox. Объект типа файл схраняется в свойство pdf.cropped_file.
    :param pdf: объект pdf
    :return:
    """
    pdf.cropped_file = tempfile.NamedTemporaryFile(mode='w+b', dir=pdf.tmpdir, suffix='.pdf', delete=False)

    input = PdfFileReader(file(pdf.abspath, "rb"))
    output = PdfFileWriter()

    if pdf.paper_sizes:
        logger.info('')
        logger.info('――> Cropping [using signa paper]:')
        for index in range(1, pdf.complects + 1):
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

            x1 = pt((plate_w - paper_w)/2)                  # отступ слева
            y1 = pt(pdf.machines[index].klapan)             # отступ снизу
            x2 = pt(paper_w + (plate_w - paper_w)/2)        # ширина бумаги + отступ слева
            y2 = pt(paper_h + pdf.machines[index].klapan)   # высота бумаги + отступ снизу

            page.mediaBox.lowerLeft = (x1, y1)
            page.mediaBox.upperRight = (x2, y2)

            logger.info('····page {} to paper {}x{}'.format(index, paper_w, paper_h))

            output.addPage(page)

    else:
        logger.info('')
        logger.info('――> Cropping [using gs bbox]:')
        bbox = get_bbox(pdf.abspath)
        for index in range(1, pdf.complects + 1):

            page = input.getPage(index-1)

            page.mediaBox.lowerLeft = (bbox[index][0], bbox[index][1])
            page.mediaBox.upperRight = (bbox[index][2], bbox[index][3])

            paper_w = mm(bbox[index][2] - bbox[index][0])
            paper_h = mm(bbox[index][3] - bbox[index][1])
            logger.info('····page {} to paper {}x{}'.format(index, paper_w, paper_h))

            output.addPage(page)

    outputstream = file(pdf.cropped_file.name, "wb")
    output.write(outputstream)
    outputstream.close()
    pdf.cropped_file.close()


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

    logger.info('')
    logger.info('――>Starting PDF preview compression...')

    try:
        retcode = call(gs_compress, shell=True, stdout=subprocess.PIPE)
        if retcode > 0:
            logger.error('····Compressing FAILED: {}'.format(retcode))
    except OSError as e:
        logger.error('····Compressing FAILED:', e)
    else:
        logger.info('····done')


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
    PROOF_WIDTH = 2500
    THUMB_WIDTH = 175

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

    # если уже есть такие превьюхи - удаляем
    if os.path.exists(jpeg_thumb):
        os.unlink(jpeg_thumb)
    if os.path.exists(jpeg_proof):
        os.unlink(jpeg_proof)

    gs_compress = "gs -sDEVICE=jpeg -dFirstPage=1 -dLastPage=1 -dJPEGQ=80 -r{resolution}"\
                  "-dNOPAUSE -dBATCH -sOutputFile={output} {input} " \
                  .format(resolution='200', input=pdf.compressed_file.name, output=jpeg_file.name)

    logger.info('')
    logger.info('――> Starting Jpeg preview compression')
    logger.info('····make full resolution jpg')
    os.system(gs_compress)
    logger.info('····downsample to {}px'.format(PROOF_WIDTH))
    reduce_image(jpeg_file.name, jpeg_proof, PROOF_WIDTH)
    logger.info('····downsample to {}px'.format(THUMB_WIDTH))
    reduce_image(jpeg_file.name, jpeg_thumb, THUMB_WIDTH)
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
        colorstring = colorant_to_string(pdf.colors)
        name, ext = os.path.splitext(pdf.name)

        #если файл не сигновский, то colorstring=None, цвета не определяются
        # TODO Тут объеденяется string и unicode. Не будет работать для русских названий файлов.
        if colorstring:
            newname = name + '_' + str(pdf.machines[1].plate_w) + '_' + str(pdf.plates) + 'Plates' + colorstring + ext
        else:
            newname = name + '_' + str(pdf.machines[1].plate_w) + ext

        logger.info('\n――> Renaming: {} ――> {}'.format(pdf.name, newname))
        shutil.move(pdf.abspath, os.path.join(pdf.tmpdir, newname))
        pdf.name = newname


# TODO Эти две функции - бесполезные обертки вокруг sendfile.
# TODO Это надо отрефакторить, чтобы sendfile принимал нужные аргуметны (в частности, фтп), и возвращал статус
# TODO и переписать код, чтобы статусы напрямую возвращалсиь из sendfile
# TODO Так же эти проверки на присутствие файла, присутствие фтп тоже внедрить в sendfile

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
        logger.error('Uploading: compressed file not found')
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
        logger.error('Uploading: PDF file not found')
        pdf.upload_to_outputter_status, pdf.upload_to_outputter_error = False, 'PDF not found'


def send_sms(pdf):
    """
    Отсылается смс. Получатель определяется по полю outputter.sms_receiver
    :param pdf:
    :return:
    """
    d = shelve.open('shelve.db')
    import_mode = d['IMPORT_MODE']
    d.close()

    logger.info('')
    logger.info('――> SMS:')
    if pdf.upload_to_outputter_status:
        smsc = smsc_api.SMSC()
        try:
            phone = pdf.outputter.sms_receiver.phone
        except:
            logger.info('····skip send sms due no phone for outputter')
        else:
            message = '{} {} {}->{} {}'.format(pdf.order, pdf.ordername, str(pdf.plates), pdf.machines[1].name, pdf.outputter.name)

            # smsc.send_sms возвращает массив (<id>, <количество sms>, <стоимость>, <баланс>) в случае успешной
            # отправки, либо массив (<id>, -<код ошибки>) в случае ошибки

            # Тут небольшое нарушение логики. Если был включен import mode, то значит, аплоад не производился.
            # Следовательно, upload_to_outputter_status будет False и в эту ветку выполнение уже не попадет.
            # Пока, на всякий пожарный, оставлю
            if not import_mode:
                status = smsc.send_sms(phone, message)
            else:
                status = []

            if len(status) == 4:
                logger.info('····sms status: ok, cost: {}, balance: {}'.format(status[2], status[3]))
                logger.info('····sms text: {}'.format(message))
            elif len(status) == 2:
                logger.error('····sms FAILED with error: {}'.format(status[1]))
                logger.error('····more info: https://smsc.ru/api/http/#answer')
            else:
                logger.warning('····skip send sms [possible import mode on]')
    else:
        # если по какой-то причине у нас не софрмирован upload_to_outputter_status
        logger.warning('····skip send sms due failed uploading')


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

    logger.info('')
    logger.info('――> Save into database:')

    try:
        row = Grid()
        row.order = pdf.order
        row.datetime = pdf.created
        row.pdfname = pdf.ordername
        row.machine = pdf.machines[1]
        row.total_pages = pdf.complects
        row.total_plates = pdf.plates
        row.contractor = pdf.outputter
        row.contractor_error = contractor_error
        row.preview_error = preview_error
        row.colors = dict_to_multiline(pdf.colors)[:500]
        row.inks = inks_to_multiline(pdf.inks)[:500]
        row.bg = bg
        row.proof = pdf.jpeg_proof
        row.thumb = pdf.jpeg_thumb
        # logger.info('row.order', row.order)
        # logger.info('row.datetime', row.datetime)
        # logger.info('row.pdfname', row.pdfname)
        # logger.info('row.machine', row.machine)
        # logger.info('row.total_pages', row.total_pages)
        # logger.info('row.total_plates', row.total_plates)
        # logger.info('row.contractor', row.contractor)
        # logger.info('row.contractor_error', row.contractor_error)
        # logger.info('row.preview_error', row.preview_error)
        # logger.info('row.colors', row.colors)
        # logger.info('row.inks', row.inks)
        # logger.info('row.bg', row.bg)
        # logger.info('row.proof', row.proof)
        # logger.info('row.thumb', row.thumb)
        row.save()
        logger.info('····done')
    except Exception, e:
        logger.error('····FAILED: {}'.format(e))


def cleaning_temps(pdf):
    """
    Очистка временных файлов
    :param pdf:
    :return:
    """
    logger.info('')
    logger.info('――> Cleaning up:')
    try:
        os.unlink(pdf.abspath)
        os.unlink(pdf.cropped_file.name)
        os.unlink(pdf.compressed_file.name)
        shutil.rmtree(pdf.tmpdir)
        logger.info('····done')
    except Exception, e:
        logger.error('····FAILED: {}'.format(e))