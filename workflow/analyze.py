# -- coding: utf-8 --
import os
import logging
import re

from subprocess import Popen, PIPE
from django.conf import settings
from PyPDF2 import PdfFileReader

from .util import mm
from .signamarks import detect_mark
from .models import PrintingPress
from core.models import Contractor

logger = logging.getLogger(__name__)

def detect_is_pdf(pdf):
    """
    Проверяет, является ли файл типом PDF
    :return: True, если входной файл имеет расширение pdf и внутренний тип pdf, иначе False
    """
    pdfcheck_command = "file {} | tr -s ':' | cut -f 2 -d ':'".format(pdf.abspath)
    result_strings = Popen(pdfcheck_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().decode().split(',')[0].strip()

    file_is_pdf_document = result_strings == 'PDF document'
    filetype = result_strings

    extension = pdf.name.split('.')[-1]
    if extension.lower() == "pdf" and file_is_pdf_document:
        logger.info("File type: {}".format(filetype))
        return True, filetype
    else:
        os.unlink(pdf.abspath)
        os.removedirs(pdf.tmpdir)
        logger.error('File [{0}] is NOT PDF - exiting...'.format(pdf.name))
        exit()
        # return False, filetype


def detect_is_signastation(pdf):
    """
    :return: Возвращиет True, если файл создан в Heidelberg Signastation
    """
    pdfinfo_command = "pdfinfo '{}' | grep Creator | tr -s ' ' | cut -f 2 -d ':'".format(pdf.abspath)
    creator = Popen(pdfinfo_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().decode().strip()
    if 'PrinectSignaStation' in creator:
        valid_signa = True
        logger.info('File creator: {}'.format(creator))
    else:
        valid_signa = False
        logger.warning('File is NOT a valid PrinectSignaStation file. Creator: {}'.format(creator))
    return valid_signa, creator


def analyze_platesize(pdf):
    """
    Функция принимает на входе имя файла, и на выходе выдает словарь, в котором ключ - номер страницы (начиная с 1), а
    значение - список (ширина, высота) в мм
    :param pdf: объект pdf
    :return: dict
    """
    from PyPDF2 import PdfFileReader

    pdffile = PdfFileReader(open(pdf.abspath, "rb"))
    pages = pdffile.pages

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


def analyze_machine(pdf):
    """
    Функция определяет печатную машину. Возвращиет словарь, в котором ключ - номер страницы,
    значение - объект типа PrintingPress
    :param pdf: объект pdf
    :return: machine - словарь или None, если не удалось определить
    """

    logger.info('')
    logger.info('――> Detect machine')
    machines = {}
    if pdf.marks:
        logger.info('····method: by signa mark')
        machine_mark_name, machine_mark_regex = detect_mark(settings.MARKS_MACHINE, pdf.marks)

        for page, piece_info in pdf.marks.items():
            page_number = page + 1

            # `piece_info['Machine']` возвращает список: (u'Выведено: Speedmaster', 'pssMO14_1', 'TextMark')
            # далее regex извлекает нужную нам часть метки

            try:
                machine_mark_text = re.findall(machine_mark_regex, piece_info[machine_mark_name][0])[0]
            except KeyError:
                logger.warning('····Страница {} не содержит cигновской метки {}'.format(page_number, machine_mark_name))
                machine = None

            if 'machine_mark_text' in locals():
                for press in PrintingPress.objects.all():
                    if press.name == machine_mark_text:
                        machine = press

            if 'machine' in locals():
                machines[page_number] = machine
            else:
                machines[page_number] = None
    else:
        logger.info('····method: signa marks missed, trying detect by plate size')
        # Если первый способ провалился, пробуем определить машину, основываясь на размере пластины.

        # Тут есть проблема - что делать с двумя машинами с одинаковыми форматами, например Speedmaster и FS_Speedmaster?
        # Пока в голову приходит только прибить гвоздями определенные машины, по одной для каждого формата пластин.
        # В будущем можно добавить поле какое-то в базу, типа приоритета.
        # TODO прибито гвоздями. Хотя, это все равно обходное решение в отсутствии сигна-метки.
        primary_machines = PrintingPress.objects.filter(name__in=['Speedmaster', 'Dominant', 'Planeta'])

        # Теперь сравниваем полученные размеры с известными, для каждой странцы
        for page, plate in pdf.platesize.items():
            for press in primary_machines:
                #logger.debug('press.plate_w={}, pdf.platesize[page][0]={}, press.plate_h={}, pdf.platesize[page][1]={}'.format(press.plate_w, pdf.platesize[page][0], press.plate_h, pdf.platesize[page][1] ))
                if (press.plate_w == pdf.platesize[page][0]) and (press.plate_h == pdf.platesize[page][1]):
                    machines[page] = press

    #Check if machine detected
    #-----------------------------------------------------------------
    if machines:
        logger.info('····detected [by 1st page]: {}'.format(machines[1].name))
    else:
        os.unlink(pdf.abspath)
        os.removedirs(pdf.tmpdir)
        logger.error('Cant detect machine for {}'.format(pdf.name))
        exit()

    return machines


def analyze_papersize(pdf):
    """
    Функция возвращает словарь: {номер страницы: машина, ширина листа, высота листа}
    Если файл не Сигновский, нет инфы о страницах, - то возвращается None
    :param pdf: объект pdf
    :return papersizes: dict
    """

    if pdf.marks:
        machine_mark_name, machine_mark_regex = detect_mark(settings.MARKS_MACHINE, pdf.marks)
        paper_mark_name, paper_mark_regex = detect_mark(settings.MARKS_PAPER, pdf.marks)

        papersizes = {}
        for page, piece_info in pdf.marks.items():
            page_number = page + 1

            # `piece_info['Machine']` возвращает список: (u'Выведено: Speedmaster', 'pssMO14_1', 'TextMark')
            # далее regex извлекает нужную нам часть метки, - имя машины или размеры бумаги

            try:
                machine = re.findall(machine_mark_regex, piece_info[machine_mark_name][0])[0]
            except KeyError:
                logger.warning('Страница {} не содержит cигновской метки {}'.format(page_number, machine_mark_name))
                machine = None

            try:
                paper = re.findall(paper_mark_regex, piece_info[paper_mark_name][0])[0]
                paper_w = int(round(float(paper[0].replace(',', '.'))))
                paper_h = int(round(float(paper[1].replace(',', '.'))))
            except KeyError:
                logger.warning('Страница {} не содержит cигновской метки {}'.format(page_number, paper_mark_name))
                paper_w, paper_h = None, None

            #logger.info(page_number, machine.encode('utf-8'), paper)
            papersizes[page_number] = (machine, paper_w, paper_h)

    else:
        papersizes = None

    return papersizes


def analyze_colorant(pdf):
    """
    plates(int) - общее количество плит
    colors(dict) - словарь, где ключ - номер страницы (начиная с 1), значение - список сепараций
    :param pdf: объект pdf
    :return plates, colors: int, dict
    """
    logger.info('')
    logger.info('――> Analyze colorant')
    if pdf.is_signastation:
        fileobj = PdfFileReader(open(pdf.abspath, "rb"))
        pages = list(fileobj.pages)

        plates = 0
        colors = {}

        for page, content in enumerate(pages, 1):
            color = content['/PieceInfo']['/HDAG_COLORANT']['/Private']['/HDAG_ColorantOrder']

            #colors contain string for one page:
            #['/Magenta', '/Cyan', '/Yellow']
            #['/PANTONE#20Warm#20Red#20C', '/PANTONE#20Green#200921#20C', '/Yellow']

            #remove slash and fix pantone names
            color = [s.replace('#20', '_') for s in color]
            color = [s.replace('/', '') for s in color]

            colors[page] = color
            plates += len(color)

            logger.info('····page {}, colors: {}'.format(page, ', '.join(colors[page])))
    else:
        plates, colors = 0, None

    return plates, colors


def detect_ctpbureau(pdf):
    """
    Возвращает объект, соответствующий подрядчику вывода форм.
    :param pdf: объект pdf
    :return: outputter (instance of FTP_server)
    """
    logger.info('')
    logger.info('――> Detect ctp bureau')
    try:
        #
        # Try detect via signa marks
        #
        outputter_mark_name, outputter_mark_regex = detect_mark(settings.MARKS_OUTPUTTER, pdf.marks)
        extracted_text = pdf.marks[0][outputter_mark_name][0]
        mark_content = re.findall(outputter_mark_regex, extracted_text)[0]

        # Может быть такое, что файл содержит сигна-метку, но она пустая, или по какой-то причине
        # выводильщика не удалось определить. Тогда возникает IndexError и выводильщик определяется по имени файла

        # if not mark_content:
        #     raise TypeError

        for ctpbureau in Contractor.objects.filter(produce__exact='ctp'):
            if ctpbureau.name.lower() == mark_content.lower():
                outputter = ctpbureau
    except (TypeError, IndexError):
        #
        # try detect via filename
        #
        fname, fext = os.path.splitext(pdf.name)

        # Тут нужен unicode, потому что имя файла может содержать русские буквы,
        # и будет лажа при сравнении типа str (fname) с типом unicode (Outputter.objects.all())
        parts = fname.decode('UTF-8').lower().split("_")

        for ctpbureau in Contractor.objects.filter(produce__exact='ctp'):
            if ctpbureau.name.lower() in parts:
                outputter = ctpbureau

    if 'outputter' in locals():
        logger.info('····detected: {}'.format(outputter))
    else:
        logger.error('····FAILED: Outputter cant be detected.\nExit!')
        exit()

    return outputter


def analyze_inkcoverage(pdf):
    """
    Анализ заполнения краски. Возвращает словарь, в котором
    ключ - номер страницы, значение - список из четырех float
    цифр, в процентах
    :param pdf: объект pdf
    :return: inks(dict)
    """
    logger.info('')
    logger.info('――> Starting ink coverage calculating')
    gs_command = r"gs -q -o - -sProcessColorModel=DeviceCMYK -sDEVICE=ink_cov {}".format(pdf.name)
    result = Popen(gs_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().splitlines()

    inks = {}
    try:
        for index, s in enumerate(result, 1):
            args = s.split()[0:4]
            args = [float(x) for x in args]
            inks[index] = args
    except:
        # Except can be raise when ghostscript fall into error
        logger.warning('····failed [possibly ghostscript error]')
    else:
        logger.info('····done')

    return inks


def analyze_order(pdf):
    """
    Извлекает номер заказа из названия файла
    :param pdf: объект pdf
    :return:
    """
    name = os.path.basename(pdf.name)
    order = re.findall("^(\d+)", name)
    order = order[0] if order else None
    return order


def analyze_ordername(pdf):
    """
    Извлекает название заказа
    :param pdf: 
    :return: 
    """
    name, ext = os.path.splitext(pdf.name)
    parts = name.split("_")

    for bureau in Contractor.objects.filter(produce__exact='ctp'):
        if bureau.name in parts:
            parts.remove(bureau.name)

    if parts[0].isdigit():
        del parts[0]

    ordername = '_'.join(parts)
    return ordername