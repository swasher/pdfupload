# coding: utf-8
import os
import tempfile
import shutil
import logging
import datetime

from decouple import config
from django.utils import timezone

from pdfupload.settings import INPUT_PATH as inputpath
from pdfupload.settings import TEMP_PATH as tmppath

from .analyze import analyze_machine
from .analyze import analyze_platesize
from .analyze import detect_is_pdf
from .analyze import detect_is_signastation
from .analyze import analyze_colorant
from .analyze import analyze_papersize
from .analyze import detect_ctpbureau
from .analyze import analyze_order
from .analyze import analyze_ordername
from .signamarks import mark_extraction
from .util import humansize
from .util import read_shelve
from .util import error_text
from .util import inks_to_multiline
from .util import dict_to_multiline
from .action import sendfile
from .models import Grid

logger = logging.getLogger(__name__)

class PDF:

    starttime = None     # время начала обработки
    endtime = None       # время окончания обработки
    name = None          # имя pdf-файла
    ordername = None     # название работы
    created = None       # дата (или now(), или дата создания файла, зависит от IMPORT_MODE)
    order = None         # номер заказа
    tmpdir = ''          # абс. путь к временной директории
    abspath = ''         # @property aбс. путь к pdf во временной директории
    is_pdf = ''          # True если файл - pdf
    filetype = ''        # тип файла. Можно определить, pdf это или нет.
    is_signastation = '' # True если pdf был создан в сигне
    creator = ''         # creator из pdfinfo
    marks = ''           # словарь извлеченных сигна-меток
    platesize = ''       # словарь c размерами пдф-страниц
    machines = ''        # словарь, ключ - № стр., значение - объект типа PrintingPress (или None)
    complects = ''       # кол-во страниц (комплектов вывода)
    paper_sizes =''      # словарь с размерами бумаги (не путать с размерами плит!)
    plates = ''          # кол-во плит
    colors = ''          # словарь с цветностью страниц
    ctpbureau = ''       # объект, соответствующий подрядчику вывода форм
    cropped_file = ''    # объект типа файл. Имя доступно в свойстве name.
    compressed_file = '' # объект типа tempfile, кропленный, уменьшеный пдф
    jpeg_proof = ''      # абс. путь к джипегу от первой страницы пдф
    jpeg_thumb = ''      # абс. путь к джипегу от первой страницы пдф (совсем маленький)
    inks = ''            # словарь со значениями расхода краски
    ctpbureau_status = '' # статус заливки выводильщику
    ctpbureau_error = ''  # код ошибки
    press_status = ''     # статус заливки на печатную машину
    press_error = ''      # код ошибки


    def __init__(self, pdf_name):
        self.starttime = datetime.datetime.now()
        self.tmpdir = tempfile.mkdtemp(suffix='/', dir=tmppath)
        self.name = pdf_name.strip("'") # Remove quotes which added by incron. Through quotes whitespace-contained filenames are supported.
        self.move_to_temp()
        self.welcome()
        self.import_mode = read_shelve()
        self.ordername = analyze_ordername(self)
        self.created = self.analyze_date()
        self.is_pdf, self.filetype = detect_is_pdf(self)
        self.is_signastation, self.creator = detect_is_signastation(self)
        self.marks = mark_extraction(self)
        self.platesize = analyze_platesize(self)
        self.paper_sizes = analyze_papersize(self)
        self.machines = analyze_machine(self)
        self.plates, self.colors = analyze_colorant(self)
        self.ctpbureau = detect_ctpbureau(self)
        self.order = analyze_order(self)


    def welcome(self):
        server = config('SERVER')   #TEST
        welcome = 'START PROCESSING {}'.format(self.name)

        logger.info('')
        logger.info('')
        logger.info(welcome)
        logger.info('-' * (len(welcome)))
        logger.info('SERVER_TYPE={}'.format(server))   #TEST
        logger.info('Start time: {}'.format(self.starttime.strftime("%b %d, %Y %H:%M:%S")))
        logger.info('File size: {}'.format(self.filesize()))

    @property
    def abspath(self):
        return os.path.join(self.tmpdir, self.name)

    @property
    def complects(self):
        return len(self.platesize)

    def move_to_temp(self):
        """
        Move PDF from hotfolder to temp dir
        :return: absolute path to pdf in tempdir
        """

        try:
            shutil.move(os.path.join(inputpath, self.name), os.path.join(self.tmpdir, self.name))
        except Exception as e:
            logger.error('{}: Can`t move to temp: {}'.format(self.name, e))
            exit()

    def filesize(self):
        """
        Print filesize in Welcome
        :return: 
        """
        size = os.path.getsize(self.abspath)
        return humansize(size)


    def analyze_date(self):
        """
        Если установлен режим импорта, то дата берется как дата создания файла, иначе - now()
        :param pdf: объект pdf
        :return: объект datetime
        """
        import_mode = self.import_mode

        if import_mode:
            modified = os.path.getmtime(self.abspath)
            dt = datetime.datetime.fromtimestamp(modified)
        else:
            dt = timezone.now()
        return dt


    def upload_to_press(self):
        """
        Отсылает обрезанный и сжатый файл на фтп печатной машины
        :param pdf:
        :return: none. Result store in self.press_status, self.press_error
        """
        import_mode = self.import_mode

        if import_mode:
            logger.info('····skip upload to [{}] due import mode'.format(self.machines[1].uploadtarget.name))
            self.press_status, self.press_error = False, 'skip, import mode'
        else:
            self.press_status, self.press_error = \
                sendfile(self.compressed_file.name, self.machines[1].uploadtarget)


    def upload_to_ctpbureau(self):
        """
        Отсылает оригинальный файл на вывод
        :param pdf:
        :return: none. Result store in self.ctpbureau_status, self.ctpbureau_error
        """
        import_mode = self.import_mode

        if import_mode:
            logger.info('····skip upload to [{}] due import mode'.format(self.machines[1].uploadtarget.name))
            self.ctpbureau_status, self.ctpbureau_error = False, 'skip, import mode'
        else:
            self.ctpbureau_status, self.ctpbureau_error = \
                sendfile(self.abspath, self.ctpbureau.ftp_account)


    def save_bd_record(self):
        """
        Данные, собранные о pdf, сохраняются в базу данных
        :param pdf:
        :return:
        """
        contractor_error = error_text(self.ctpbureau_status, self.ctpbureau_error)
        preview_error = error_text(self.press_status, self.press_error)
        if not self.ctpbureau_status:
            bg = 'danger'
        elif not self.press_status:
            bg = 'warning'
        else:
            bg = 'default'

        logger.info('')
        logger.info('――> Save into database:')

        try:
            row = Grid()
            row.order = self.order
            row.datetime = self.created
            row.pdfname = self.ordername
            row.machine = self.machines[1]
            row.total_pages = self.complects
            row.total_plates = self.plates
            row.contractor = self.ctpbureau
            row.contractor_error = contractor_error
            row.preview_error = preview_error
            row.colors = dict_to_multiline(self.colors)[:500]
            row.inks = inks_to_multiline(self.inks)[:500]
            row.bg = bg
            row.proof = self.jpeg_proof
            row.thumb = self.jpeg_thumb
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
        except Exception as e:
            logger.error('····FAILED: {}'.format(e))


    def cleaning_temps(self):
        """
        Очистка временных файлов
        :param pdf:
        :return:
        """
        logger.info('')
        logger.info('――> Cleaning up:')
        end_time = timezone.now()
        duration = end_time - self.starttime
        try:
            os.unlink(self.abspath)
            os.unlink(self.cropped_file.name)
            os.unlink(self.compressed_file.name)
            shutil.rmtree(self.tmpdir)
            logger.info('····done [in {}]'.format(str(duration).split('.')[0]))
        except Exception as e:
            logger.error('····FAILED: {}'.format(e))