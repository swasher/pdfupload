#!/usr/bin/python
#coding: utf-8
from pprint import pprint
import logging

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfparser import PDFParser
from pdfminer.layout import LAParams
from pdfminer.layout import LTFigure, LTChar
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed

logger = logging.getLogger(__name__)

# XObject pssMO*_* - это сигновские метки (Mark Object)
# XObject pssPO*_* - это страницы вывода (Page Object)


def find_mo_objects(lt_objs):
    """
    Фильтруем все объекты и отсеиваем только Сигна-метки. Такие объекты содежат атрибут name='pssMOx_x'. Возвращаем
    список объектов-сигнаметок.
    :param lt_objs:
    :return:
    """
    # from pprint import pprint
    # for obj in lt_objs:
    #     print obj
    # exit('stop!')

    list_mo = {}
    for obj in lt_objs:
        try:
            if 'pssMO' in obj.name:
                #print 'FIND {}'.format(obj.name)
                list_mo[obj.name] = obj
        except AttributeError:
            # obj may not have attibute 'name'
            pass
    return list_mo


def recurse_iterate(lt_objs):
    """
    Функция принимает объект lt_obj из словаря list_mo. Рекурсивно итерируем их и возвращаем содержащийся в объекте текст.
    :param lt_objs:
    :return:
    """
    txt = ''
    for lt_obj in lt_objs:
        if isinstance(lt_obj, LTChar):
            txt += lt_obj.get_text()
        elif isinstance(lt_obj, LTFigure):
            # может быть, тут должно быть просто else?
            recurse_iterate(lt_obj)  # Recursive
    return txt


def parse_mo_dict(mo_dict):
    """
    mo_dict содержит словарь с ключами - имя XObject, занчения - объекты LT:
    {'pssMO6_1': <LTFigure(pssMO6_1) 198.425,70.866,1606.145,104.882 matrix=[1.00,0.00,0.00,1.00, (198.43,70.87)]>,
    'pssMO9_1': <LTFigure(pssMO9_1) 136.063,439.370,147.401,513.071 matrix=[1.00,0.00,0.00,1.00, (136.06,439.37)]>,...}
    """
    miner_dict = {}
    for name, obj in mo_dict.items():
        text = recurse_iterate(obj)
        miner_dict[name] = text
    return miner_dict


def mark_extraction___(pdf):
    """
    Возвращает словарь, где ключ - номер страницы, а значение - словарь.
    Во внутреннем словаре ключ - имя метки (как она названа в сигне), а
    значение - список (текст метки, имя XObject, Субтип). Например:

     {0: {'CutMark_2mm': ('', 'pssMO1_1', 'Default'),
         'tes_color': (u'Magenta Cyan Yellow ', 'pssMO4_1', 'TextMark'),
     1: {'CutMark_2mm': ('', 'pssMO1_1', 'Default'),
         'tes_color': (u'PANTONE Warm Red C PANTONE Green 0921 C Yellow ', 'pssMO4_1', 'TextMark')}}

    В нем ключи - это название меток, а значения -[0] - текст метки, [1] - имя xobject, а [2] - сигновский тип метки

    Если файл не сигновский, возвращается None

    usage:
    import mark_extraction
    m = mark_extraction(file)
    print m[page][signa-mark-name][(0|1|2)(mark_text|xobject|SubType)]

    """
    logger.info('')
    logger.info('――> Mark extraction')
    if pdf.is_signastation:

        fp = open(pdf.abspath, 'rb')

        # Create a PDF parser object associated with the file object.
        parser = PDFParser(fp)

        # Create a PDF document object that stores the document structure.
        # Password for initialization as 2nd parameter
        logger.info('start doc = PDFDocument(parser)')
        doc = PDFDocument(parser)
        logger.info('end doc = PDFDocument(parser)')

        # Check if the document allows text extraction. If not, abort.
        if not doc.is_extractable:
            raise PDFTextExtractionNotAllowed

        # Create a PDF resource manager object that stores shared resources.
        rsrcmgr = PDFResourceManager()

        # BEGIN LAYOUT ANALYSIS
        # Set parameters for analysis.
        laparams = LAParams()

        # Create a PDF page aggregator object.
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)

        # Create a PDF interpreter object.
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Это словарь, где ключ - номер страницы
        result = {}

        for n, page in enumerate(PDFPage.create_pages(doc)):

            # Вытаскиваем текст меток и составляем словарь:
            # {'pssMO10_1': u'\u0412\u044b\u0432\u0435\u0434\u0435\u043d\u043e: Admin     Dominant 640,0 x 450,0',
            #  'pssMO4_1': u'Magenta Cyan Yellow ',}

            # read the page into a layout object
            interpreter.process_page(page)
            layout = device.get_result()

            # Create a dict with (Signa) Mark Objects
            list_mo = find_mo_objects(layout)

            # Iterate the dict recursively and find text for each Mark Object
            text_dict = parse_mo_dict(list_mo)

            # Это словарь, где ключ - название метки
            current_page_mark_dict = {}

            # Определяем соответствие XObject<->Markname и составляем окончательный словарь *для текущей страницы (n)*
            resources = page.attrs['Resources'].resolve()['XObject']

            for xobject, value in resources.items():
                if 'pssMO' in xobject:
                    # logger.info('\n', key)
                    CreationName = value.resolve()['PieceInfo'].resolve()['HDAG_SignaMarkInfo']['Private'].resolve()['CreationName'].decode()
                    CreationType = repr(value.resolve()['PieceInfo'].resolve()['HDAG_SignaMarkInfo']['Private'].resolve()['CreationType']).strip("\/'")  # I don't use it
                    SubType = repr(value.resolve()['PieceInfo'].resolve()['HDAG_SignaMarkInfo']['Private'].resolve()['SubType']).strip("\/'")

                    current_page_mark_dict[CreationName] = (text_dict[xobject], xobject, SubType)

            result[n] = current_page_mark_dict
            logger.info('····ok, page {}'.format(n+1))

        fp.close()
        device.close()
    else:
        logger.info('····SKIP [non-signa file]')
        result = None

    return result



def mark_extraction(pdf):
    """
    Возвращает словарь, где ключ - номер страницы, а значение - словарь.
    Во внутреннем словаре ключ - имя метки (как она названа в сигне), а
    значение - список (текст метки, имя XObject, Субтип). Например:

     {0: {'CutMark_2mm': ('', 'pssMO1_1', 'Default'),
         'tes_color': (u'Magenta Cyan Yellow ', 'pssMO4_1', 'TextMark'),
     1: {'CutMark_2mm': ('', 'pssMO1_1', 'Default'),
         'tes_color': (u'PANTONE Warm Red C PANTONE Green 0921 C Yellow ', 'pssMO4_1', 'TextMark')}}

    В нем ключи - это название меток, а значения -[0] - текст метки, [1] - имя xobject, а [2] - сигновский тип метки

    Если файл не сигновский, возвращается None

    usage:
    import mark_extraction
    m = mark_extraction(file)
    print m[page][signa-mark-name][(0|1|2)(mark_text|xobject|SubType)]

    """
    logger.info('')
    logger.info('――> Mark extraction')
    if pdf.is_signastation:

        fp = open(pdf.abspath, 'rb')

        # Create a PDF parser object associated with the file object.
        parser = PDFParser(fp)

        # Create a PDF document object that stores the document structure.
        # Password for initialization as 2nd parameter
        #logger.info('start doc = PDFDocument(parser)')
        #doc = PDFDocument(parser)
        #logger.info('end doc = PDFDocument(parser)')

        # Check if the document allows text extraction. If not, abort.
        #if not doc.is_extractable:
        #    raise PDFTextExtractionNotAllowed

        # Create a PDF resource manager object that stores shared resources.
        rsrcmgr = PDFResourceManager()

        # BEGIN LAYOUT ANALYSIS
        # Set parameters for analysis.
        laparams = LAParams()

        # Create a PDF page aggregator object.
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)

        # Create a PDF interpreter object.
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Это словарь, где ключ - номер страницы
        result = {}

        pagenos=set()
        maxpages = 0 #is for all
        password = None
        caching = True

        #for n, page in enumerate(PDFPage.create_pages(doc)):
        n = 0
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                          password=password,
                                          caching=caching,
                                          check_extractable=True):


            # Вытаскиваем текст меток и составляем словарь:
            # {'pssMO10_1': u'\u0412\u044b\u0432\u0435\u0434\u0435\u043d\u043e: Admin     Dominant 640,0 x 450,0',
            #  'pssMO4_1': u'Magenta Cyan Yellow ',}

            # read the page into a layout object
            interpreter.process_page(page)
            layout = device.get_result()

            # Create a dict with (Signa) Mark Objects
            list_mo = find_mo_objects(layout)

            # Iterate the dict recursively and find text for each Mark Object
            text_dict = parse_mo_dict(list_mo)

            # Это словарь, где ключ - название метки
            current_page_mark_dict = {}

            # Определяем соответствие XObject<->Markname и составляем окончательный словарь *для текущей страницы (n)*
            resources = page.attrs['Resources'].resolve()['XObject']

            for xobject, value in resources.items():
                if 'pssMO' in xobject:
                    # logger.info('\n', key)
                    CreationName = value.resolve()['PieceInfo'].resolve()['HDAG_SignaMarkInfo']['Private'].resolve()['CreationName'].decode()
                    CreationType = repr(value.resolve()['PieceInfo'].resolve()['HDAG_SignaMarkInfo']['Private'].resolve()['CreationType']).strip("\/'")  # I don't use it
                    SubType = repr(value.resolve()['PieceInfo'].resolve()['HDAG_SignaMarkInfo']['Private'].resolve()['SubType']).strip("\/'")

                    current_page_mark_dict[CreationName] = (text_dict[xobject], xobject, SubType)

            result[n] = current_page_mark_dict
            logger.info('····ok, page {}'.format(n+1))

            n = n+1

        fp.close()
        device.close()
    else:
        logger.info('····SKIP [non-signa file]')
        result = None

    return result



def detect_mark(list_of_available_marks, pdf_extracted_marks):
    """
    Со временем названия и содержания сигна-меток, содержащих нужную информацию, могут измениться. Но программа должна 
    корректно работать со всеми версиями файлов, поэтому каждый тип информации (например, название машины) прописан 
    в marks.py и имеет несколько кортежей метка-регулярка, которые описывают метки, применявшиеся в разное время.
     
    Эта функция перебирает все варианты, определяет, какой именно формат используется в PDF файле, и возвращает два 
    значения - имя марки и regexp.

    Так же предполагается, что название марки одинаково для всех страниц, и поэтому производится анализ только первой.

    :param list_of_available_marks: Список всех возможных меток. Каждая метка - кортеж [название, регулярка]
    :param pdf_extracted_marks: Извлеченные данные при помощи 'mark_extraction'
    :return: Кортеж из двух значений - имя марки и regex для ее извлечения
    """

    # Создаем кортеж, содержащий имена всех меток на первой странице
    pdf_marks = pdf_extracted_marks[0]
    pdf_mark_names = []
    for item in pdf_marks.keys():
        pdf_mark_names.append(item)

    # Проверяем, какой из доступных шаблонов присутствует в кортеже pdf_mark_names. Он и будет результатом поиска.
    for mark in list_of_available_marks:
        if mark[0] in pdf_mark_names:
            detected_mark = mark

    # Если подходящей метки не нашлось, возвращаем None
    try:
        detected_mark
    except NameError:
        detected_mark = None, None

    return detected_mark


if __name__ == '__main__':
    import os
    import sys
    import django

    # Setup argument parser
    #
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("absolute_path", help='Тестируем только один файл', default='00000')
    args = parser.parse_args()
    print(args.absolute_path)

    # Initialize django
    #
    sys.path.append("/home/vagrant/pdfupload")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pdfupload.settings'
    django.setup()
    from workflow.classes import PDF

    test_path = '/home/vagrant/!!print/pdf_for_testing'

    pdf_files = []
    print(args.absolute_path)
    print(2)

    if len(sys.argv) == 1:
        # Если аргумент не указан, то тестируем все файлы в test_path
        f = os.path.join(test_path, '0007_Operniy_Afihsa_S16_NEWMARKS_Admin.pdf')
        #f = '../test/pdf_for_testing/test_search_dominant_mark.pdf'
        #f = '../test/pdf_for_testing/0059_Mig_Gazeta_Leonov.pdf'
    else:
        f = sys.argv[1]

    print(f)
    if not os.path.exists(f):
        sys.exit('ERROR: PDF "{}" was not found!'.format(sys.argv[1]))

    pdf = PDF(os.path.basename(f))
    pdf.is_signastation = True

    pdf_marks = mark_extraction(pdf)
    pprint(pdf_marks)

    print('Выведено:')
    print(pdf_marks[0]['Outputter'][0])

    #print '\n'
    #pprint(pdf_marks[0])