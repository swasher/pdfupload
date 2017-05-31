# coding: utf-8
import os
import tempfile
import shutil
import logging

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
from .analyze import analyze_date
from .analyze import analyze_ordername
from .signamarks import mark_extraction

logger = logging.getLogger(__name__)

class PDF:

    name = ''            # имя pdf-файла
    ordername = ''       # название работы
    created = ''         # дата (или now(), или дата создания файла, зависит от IMPORT_MODE)
    order = ''           # номер заказа
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
    compressed_file = '' # путь к кропленному, уменьшеному пдф
    jpeg_proof = ''      # абс. путь к джипегу от первой страницы пдф
    jpeg_thumb = ''      # абс. путь к джипегу от первой страницы пдф (совсем маленький)
    inks = ''            # словарь со значениями расхода краски
    upload_to_ctpbureau_status = '' # статус заливки выводильщику (для решения, отправлять ли смс)
    upload_to_ctpbureau_error = ''  # код ошибки
    upload_to_press_status = ''     # статус заливки на печ. машину
    upload_to_press_error = ''      # код ошибки


    def __init__(self, pdf_name):
        self.name = pdf_name.strip("'") # Remove quote added by incron. Through quotes whitespace-contained filenames are supported.
        self.ordername = analyze_ordername(self)
        self.created = analyze_date(os.path.join(inputpath, self.name))
        self.tmpdir = tempfile.mkdtemp(suffix='/', dir=tmppath)
        self.move_to_temp()
        self.is_pdf, self.filetype = detect_is_pdf(self)
        self.is_signastation, self.creator = detect_is_signastation(self)
        self.marks = mark_extraction(self)
        self.platesize = analyze_platesize(self)
        self.paper_sizes = analyze_papersize(self)
        self.machines = analyze_machine(self)
        self.plates, self.colors = analyze_colorant(self)
        self.ctpbureau = detect_ctpbureau(self)
        self.order = analyze_order(self)

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