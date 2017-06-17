#!/usr/bin/python
# -- coding: utf-8 --

import os
import tempfile
import subprocess
import shutil
import logging
import time
import math
import twx

from .smsc_api import SMSC
from PyPDF2 import PdfFileWriter, PdfFileReader
from django.conf import settings
from django.utils import timezone
from subprocess import call
from ftplib import FTP
from twx.botapi import TelegramBot

#from core.models import Employee
from workflow.models import Employee

from .models import Ctpbureau
from .models import Grid
from .util import pt, mm
from .util import reduce_image
from .util import get_jpeg_path
from .util import colorant_to_string
from .util import error_text
from .util import dict_to_multiline
from .util import inks_to_multiline
from .util import get_bbox
from .util import read_shelve


logger = logging.getLogger(__name__)

def remove_ctpbureau_from_pdfname(pdf):
    """
    Функция убирает подрядчика из имени файла (0537_Technoyug_Flier_Leonov.pdf -> 0537_Technoyug_Flier.pdf),
    затем переименовывает сам файл, и записывает новое имя в pdf.name
    :param pdf: объект pdf
    :return: none
    """

    # Тут нужен unicode, потому что имя файла может содержать русские буквы,
    # и будет лажа при сравнении типа str (fname) с типом unicode (Ctpbureau.objects.all())
    name, ext = os.path.splitext(pdf.name)
    parts = name.split("_")

    for bureau in Ctpbureau.objects.all():
        if bureau.name in parts:
            parts.remove(bureau.name)

    newname = '_'.join(parts) + ext
    newpath = os.path.join(pdf.tmpdir, newname)

    # Если подрядчик в имени файла не обнаружен, то файл не переименовывается и не перемещается
    if pdf.name != newname:
        logger.info('')
        logger.info('――> Rename:')
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

    f = open(pdf.abspath, "rb")
    input = PdfFileReader(f)
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
            logger.debug('{} {}'.format(mm(page.mediaBox.getUpperRight_x()), mm(page.mediaBox.getUpperRight_y())))
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

    outputstream = open(pdf.cropped_file.name, "wb")
    output.write(outputstream)
    outputstream.close()
    pdf.cropped_file.close()
    f.close()


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
    logger.info('――> Starting PDF preview compression...')

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
    if pdf.ctpbureau.name == 'Leonov':
        """
        Леонов хочет, чтобы файл попадал в разные папки на фтп, в зависимости от формата пластин.
        Проверку производим только для первого комплекта (хотя в пдф теоретически могут быть формы на разные машины)
        """
        if pdf.machines[1].name == 'Speedmaster':
            pdf.ctpbureau.ftp_account.todir = '_1030x770'
        elif pdf.machines[1].name == 'Planeta':
            pdf.ctpbureau.ftp_account.todir = '_1010x820'
        elif pdf.machines[1].name == 'Dominant':
            pdf.ctpbureau.ftp_account.todir = '_ADAST'
        else:
            pdf.ctpbureau.ftp_account.todir = ''


    if pdf.ctpbureau.name == 'Korol':
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

        logger.info('')
        logger.info('――> Renaming: {} ――> {}'.format(pdf.name, newname))
        shutil.move(pdf.abspath, os.path.join(pdf.tmpdir, newname))
        pdf.name = newname


# TODO Эти две функции - бесполезные обертки вокруг sendfile.
# TODO Это надо отрефакторить, чтобы sendfile принимал нужные аргуметны (в частности, фтп), и возвращал статус
# TODO и переписать код, чтобы статусы напрямую возвращалсиь из sendfile
# TODO Так же эти проверки на присутствие файла, присутствие фтп тоже внедрить в sendfile

# Или наоборот, убрать из sendfile абсолютно всю логику, и сделать разделение -
# sendfile - только умеет заливать на фтп, а логика в обертках. Так же подумать,
# может обертки стоит сделать как декораторы.

def upload_to_press(pdf):
    """
    Отсылает обрезанный и сжатый файл на фтп печатной машины
    :param pdf:
    :return: upload_to_ctpbureau_status, upload_to_ctpbureau_error
    """
    import_mode = read_shelve()

    if import_mode:
        logger.info('····skip upload to [{}] due import mode'.format(pdf.machines[1].uploadtarget.name))
        return False, 'Skipping upload due import mode'

    if not os.path.isfile(pdf.compressed_file.name):
        logger.error('Uploading: Preview PDF file not found')
        return False, 'Preview PDF not found'

    if pdf.machines[1].uploadtarget:
        status, e = sendfile(pdf, pdf.machines[1].uploadtarget)
        return status, e
    else:
        logger.error("Missing ftp credentials")
        return False, "Missing ftp credentials"


def upload_to_ctpbureau(pdf):
    """
    Отсылает оригинальный файл на вывод
    :param pdf:
    :return: upload_to_ctpbureau_status, upload_to_ctpbureau_error
    """
    import_mode = read_shelve()

    if import_mode:
        logger.info('····skip upload to [{}] due import mode'.format(pdf.machines[1].uploadtarget.name))
        return False, 'Skipping upload due import mode'

    if not os.path.isfile(pdf.abspath):
        logger.error('Uploading: PDF file not found')
        return False, 'PDF not found'

    if pdf.ctpbureau.ftp_account:
        status, e = sendfile(pdf, pdf.ctpbureau.ftp_account)
        return status, e
    else:
        logger.error("Missing ftp credentials")
        return False, "Missing ftp credentials"


def send_sms(pdf):
    """
    Отсылается смс. Получатель определяется по полю user.employee.sms_notify
    :param pdf:
    :return:
    """
    import_mode = read_shelve()

    logger.info('')
    logger.info('――> SMS:')

    if import_mode:
        logger.info('····skip due import mode')
        return None

    if pdf.ctpbureau.name == 'Admin':
        logger.info('····skip due admin mode')
        return None

    if pdf.upload_to_ctpbureau_status:

        receivers = Employee.objects.filter(sms_notify=True)

        for each in receivers:
            smsc = SMSC()
            phone = each.phone
            message = '{} {} {}->{} {}'.format(pdf.order, pdf.ordername, str(pdf.plates), pdf.machines[1].name, pdf.ctpbureau.name)

            # smsc.send_sms возвращает массив (<id>, <количество sms>, <стоимость>, <баланс>) в случае успешной
            # отправки, либо массив (<id>, -<код ошибки>) в случае ошибки

            status = smsc.send_sms(phone, message)
            # for debugging
            #status = ['0000', 0, 'dry-run', '0' ]

            if len(status) == 4:
                logger.info('····status: ok, cost: {}, balance: {}'.format(status[2], status[3]))
                logger.info(u'····receiver: {} {}'.format(each.user.first_name, each.user.last_name))
                logger.info('····text: {}'.format(message))
                logger.info('')
            elif len(status) == 2:
                logger.error('····FAILED with error: {}'.format(status[1]))
                logger.error('····more info: https://smsc.ru/api/http/#answer')
            else:
                logger.warning('····skip send sms [possible import mode on]')
    else:
        # если по какой-то причине у нас не софрмирован upload_to_ctpbureau_status
        logger.warning('····sms NOT sent. Reason: failed upload')


def send_telegram(pdf):
    """
    Отсылается сообщение через telegram bot. Получатель определяется по полю user.employee.telegram_id
    
    Пользователь должен первый написать боту, иначе он не будет получать сообщения (даже если знать его id). 
    После этого можно увидеть id пользователя, если зайти по https://api.telegram.org/bot<TOKEN>/getUpdates
    
    Алгоритм такой:
    - посылаем ВСЕМ Пользователям, у которых стоит галка telegram_notify
    - проверяем Заказчика в ПДФ файле. Если есть галка telegram_notify - посылаем. Тут вопрос такой, что у нас не связана таблица Заказчиков
      с тем, что мы пишем в пзф. Надо как-то прилинковать (можно в Заказчиках сделать поле signaname и там писать, как я его называю в сигне)
    - проверяем Выводильщика в ПДФ файле. Если есть галка telegram_notify - посылаем (создать в таблице Ctpbureau поля telegram_id и telegram_notify) 
    
    :param pdf:
    :return:
    """
    import_mode = read_shelve()

    logger.info('')
    logger.info('――> Telegram:')

    if import_mode:
        logger.info('····skip due import mode')
        return None

    if pdf.upload_to_ctpbureau_status:

        if pdf.ctpbureau.name == 'Admin':
            # TODO прибито гвоздями; можно сделать в настройках что-то вроде, - пропускать, если есть стоп-слова в названии. Но опять таки - что пропускать? Аплоад? Смс? Нотификации? Если все пропускать, тогда дебажить не получится
            # debugging purpose; if outputter is Admin then telegram send only to first superuser
            receivers = Employee.objects.filter(user__is_superuser=True)
        else:
            receivers = Employee.objects.filter(telegram_notify=True)

        for each in receivers:

            telegram_id = each.telegram_id
            bot = TelegramBot(settings.TELEGRAM_API_KEY)

            message = """
№{} {}
Плит: {}, Машина: {}, Вывод: {}
""".format(pdf.order, pdf.ordername, str(pdf.plates),pdf.machines[1].name, pdf.ctpbureau.name)

            # logger.debug('telegram_id={}'.format(telegram_id))
            # logger.debug('username={}'.format(each.user.username))

            responce = bot.send_message(chat_id=telegram_id, text=message).wait()

            if isinstance(responce, twx.botapi.botapi.Message):
                logger.info('··· {} receive notify'.format(responce.chat.username))
            elif isinstance(responce, twx.botapi.botapi.Error):
                logger.error(responce)
            else:
                logger.error('Critical telegram twx bug:')
                logger.error(responce)

    else:
        # если по какой-то причине у нас не софрмирован upload_to_ctpbureau_status
        logger.warning('····telegram NOT sent. Reason: failed upload')


def send_telegram_group_or_channel(pdf):
    """
    CURRENTLY NOT USED
    
    Эта функция посылает сообщения от имени бота в группу или канал, таким образом нам не нужно знать ID пользователей.
    Недостаток в том, что
    1 - каждое сообщение подписано именем бота
    2 - если я сделаю несколько групп (менеджеры, клиенты-какие-то, подрядчики), то я буду получать МНОГО (по кол-ву групп)
        сообщение при каждом аплоаде
        
    Примечание: много ботов создавать не нужно, один бот может выборочно слать месаги в разные группы 
    
    Полезная инфа:
    How to get an id to use on Telegram Messenger - https://github.com/GabrielRF/telegram-id#web-channel-id
    
    Процедура создание канала:
    - создаем приватный канал (channel)
    - добавляем в администраторы канала наш бот (right-click -> View channel info -> Administrators, далее в строке поиска нужно вручную вбить имя бота)
    - идем в веб-интерфейс телеграма и находим там наш канал
    - смотрим URL: https://web.telegram.org/#/im?p=s1041843721_16434430556517118330
    - находим то, что после `s`: 1041843721.
    - добавляем префикс -100: -1001041843721, получаем id канала.
    - отправляем сообщение в приватный канал: bot.send_message(chat_id='-1001041843721', text=message).wait()
    
    :param pdf:
    :return:
    """
    import_mode = read_shelve()

    logger.info('')
    logger.info('――> Telegram:')

    if import_mode:
        logger.info('····skip due import mode')
        return None

    if pdf.upload_to_ctpbureau_status:

        bot = TelegramBot(settings.TELEGRAM_API_KEY)

        message = """
№{} {}
Плит: {}, Машина: {}, Вывод: {}
""".format(pdf.order, pdf.ordername, str(pdf.plates),pdf.machines[1].name, pdf.ctpbureau.name)

        #responce = bot.send_message(chat_id='-1001136373510', text=message).wait()  # приватный канал pdf_upload_private
        responce = bot.send_message(chat_id='-238392573', text=message).wait()       # открытая группа pdf_upload_dev

        if isinstance(responce, twx.botapi.botapi.Message):
            logger.info('··· Sent to channel: {}'.format(responce.chat.title))
        elif isinstance(responce, twx.botapi.botapi.Error):
            logger.error(responce)
        else:
            logger.error('Critical telegram twx bug:')
            logger.error(responce)

    else:
        # если по какой-то причине у нас не софрмирован upload_to_ctpbureau_status
        logger.warning('····telegram NOT sent. Reason: failed upload')


def save_bd_record(pdf):
    """
    Данные, собранные о pdf, сохраняются в базу данных
    :param pdf:
    :return:
    """
    contractor_error = error_text(pdf.upload_to_ctpbureau_status, pdf.upload_to_ctpbureau_error)
    preview_error = error_text(pdf.upload_to_press_status, pdf.upload_to_press_error)
    if not pdf.upload_to_ctpbureau_status:
        bg = 'danger'
    elif not pdf.upload_to_press_status:
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
        row.contractor = pdf.ctpbureau
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
    except Exception as e:
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

        end_time = timezone.now()
        duration = end_time - pdf.starttime
        logger.info('····done [{}]'.format(str(duration).split('.')[0]))
    except Exception as e:
        logger.error('····FAILED: {}'.format(e))


def sendfile(pdf, receiver):
    """
    Функция выполняет заливку на фтп
    :param pdf_abs_path:str Путь к файлу (абсолютный)
    :param receiver:Ftp Объект получателя, список получателей в файле ftps, объекты
    формируются из файла функцией -==-
    :return: status:boolean - флаг удачного завершения
                e:exception - код ошибки
    """

    # bracket is a packet of `blocksize` bytes

    blocksize = 8192 # it's default python value

    global current_bracket, notify_brackets

    def handle(block):
        global current_bracket, notify_brackets
        current_bracket += 1
        if current_bracket in notify_brackets.keys():
            logger.info('···· progress {}%'.format(notify_brackets[current_bracket]))

    status = True
    e = None

    #sizeWritten = 0
    current_bracket = 0
    total_size = os.path.getsize(pdf.abspath)
    total_brackets = math.ceil(total_size / float(blocksize)) # becouse int round

    # list of percentages, when uploading progress rich percentage in
    # notify_percents, performed write to log
    notify_percents= [20, 40, 60, 80]

    # Заливка производится кусками по 1024 байта. Брекет - это один кусок.
    # Словарь определяет номер брекета, который соответствует например 20%
    notify_brackets = {}
    for b in notify_percents:
        notify_bracket = int(total_brackets / 100 * b)
        notify_brackets[notify_bracket] = b

    try:
        logger.info('')
        logger.info('――> Try connect to {}'.format(receiver.name))
        ftp = FTP()
        ftp.set_pasv(receiver.passive_mode) #<-- This puts connection into ACTIVE mode when receiver.passive_mode == False
        ftp.connect(receiver.ip, port=receiver.port, timeout=20)  # timeout is 15 seconds
        ftp.login(receiver.login, receiver.passw)
    except Exception as e:
        logger.error('···connect to {} FAILED with error: {}'.format(receiver.name, e))
        status = False
        return status, e
    else:
        # если коннект и логин прошли удачно, выполняется эта секция
        connection_mode = 'passive' if receiver.passive_mode else 'active'
        logger.info('···connect passed [{} mode]'.format(connection_mode))
        localfile = open(pdf.abspath, "rb")
        try:
            ftp.cwd(receiver.todir)
            logger.info('···Start uploading {} to {} ...'.format(pdf.name, receiver.name))
            start = time.time()
            ftp.storbinary("STOR " + pdf.name, localfile, blocksize, handle)
            #print 'Size in kb ', totalSize/1024
            #print 'Time in s ', (time.time()-start)
            speed_kb = total_size / (time.time() - start) / 1024
            speed_mb = speed_kb * 8 / 1024
            logger.info('···Speed: {0:.1f} kB/s equivalent to {1:.2f} MBit/s'.format(speed_kb, speed_mb))
        except Exception as e:
            logger.error('···upload to {} FAILED with error: {}'.format(receiver.name, e))
            status = False
            # DEPRECATED return status, e
        else:
            logger.info('···Upload finished OK')
        finally:
            localfile.close()
    finally:
        ftp.close()

    return status, e