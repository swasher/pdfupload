# coding: utf-8

# ---------- TO-DO -----------
#TODO логирование действий пользователя
#TODO Проверить на пригодность использования The tiffsep device also prints the names of any spot colors
#       detected within a document to stderr. (stderr is also used for the output from the bbox device.)
#       For each spot color, the name of the color is printed preceded by '%%SeparationName: '. This provides a simple
#       mechanism for users and external applications to be informed about the names of spot colors within a document.
#TODO Что должно происходить, если форма не валидна? line 123
#TODO Сделать отчеты по годам и месяцам
#TODO Сделать кнопку 'перезалить на кинап'
#TODO Аналогично кнопка run
#TODO Ротация логов nginx
#TODO Разобраться с джипегами при выполнении collectstatic. Они должны находится в $BASE_DIR/pdfupload/static_root/jpg
#TODO Регулярный бекап базы кроном. Продумать куда, возможно мылом на dropbox: https://sendtodropbox.com
#TODO Разобраться с багом, когда в названии файла русские буквы
#TODO Есть такой интересный баг, при котором может произойти непрвильное определение MachinePress, если в пдф содержатся
#    слова как названия печатных машин. Пример файла - 2012/0926_Mig, фраза 'Planetary Science от 17 января.'

#import socket
#from datetime import datetime

import sys
import os
import shutil
import tempfile
import logging
import datetime

from os.path import dirname, splitext
from django.conf import settings
from django.shortcuts import RequestContext, HttpResponseRedirect, Http404, redirect, render_to_response
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib import messages
from django_rq import job
from django.contrib.auth.decorators import login_required
from subprocess import Popen, PIPE

import smsc_api

from forms import FilterForm
from django.db.models import Q
from django.db.models import Sum
from pdfupload.settings import BASE_DIR
from models import Grid, PrintingPress
from django.utils import timezone

from analyze import analyze_machine, analyze_complects, analyze_colorant, analyze_papersize, detect_outputter, \
    analyze_inkcoverage, detect_preview_ftp, colorant_to_string, analyze_signastation
from util import inks_to_multiline, dict_to_multiline, remove_outputter_title, crop, \
    sendfile, error_text, fail

logger = logging.getLogger(__name__)


def log(request):
    return render_to_response('log.html')


def login_redirect(request):
    messages.add_message(request, messages.INFO, 'Вы должны быть зарегистрированны для выполнения этой операции.')
    return redirect('grid')


def login(request):
    #TTY = '/dev/tty1'
    #sys.stdout = open(TTY, 'w')
    context = RequestContext(request)
    if request.method == 'POST':
        username, password = request.POST['username'], request.POST['password']
        print 'username', username
        print 'pass', password
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                django_login(request, user)
            else:
                #context['error'] = 'Non active user'
                messages.add_message(request, messages.INFO, 'Non active user')
        else:
            messages.add_message(request, messages.INFO, 'Wrong username or password')

    return redirect('grid')


def logout(request):
    django_logout(request)
    return redirect('/')

@login_required
def usersettings(request):
    return render_to_response('usersettings.html')


def printing(request):
    pass


def grid(request, mode=''):

    context = RequestContext(request)
    #table = Grid.objects.all().order_by('datetime').reverse()

    logger.debug("this is a debug message!")
    logger.error("this is an error message!!")

    # Фильтр по умолчанию - за последние n дней.
    myquery = Q()
    n = 60
    start = datetime.datetime.now() - datetime.timedelta(days=n)
    end = datetime.datetime.now()
    defaultfilter = Q(datetime__range=(start, end))

    # Если не указано иное, то по умолчанию используется темплайт grid
    shablon = 'grid.html'

    if request.method == 'POST':
        # В эту ветку мы можем попасть, если нажато Filter или Print или Clear
        form = FilterForm(request.POST)
        if form.is_valid():
            # Логика по датам: первый if - введены обе даты, elif - если введена только начальная дата -
            # с нее по сегодня, иначе - за последние n дней.
            if form.cleaned_data['from_date'] and form.cleaned_data['to_date']:
                start = form.cleaned_data['from_date']
                end = form.cleaned_data['to_date'] + datetime.timedelta(days=1)
                myquery &= Q(datetime__range=(start, end))
            elif form.cleaned_data['from_date']:
                start = form.cleaned_data['from_date']
                end = datetime.datetime.now() + datetime.timedelta(days=1)
                myquery &= Q(datetime__range=(start, end))
            else:
                myquery &= defaultfilter
            if form.cleaned_data['contractor']:
                myquery &= Q(contractor__exact=form.cleaned_data['contractor'])
            if form.cleaned_data['machine']:
                myquery &= Q(machine__exact=form.cleaned_data['machine'])
            if form.cleaned_data['filename']:
                if form.cleaned_data['filename'][0] == '-':
                    myquery &= ~Q(pdfname__icontains=form.cleaned_data['filename'][1:])
                else:
                    myquery &= Q(pdfname__icontains=form.cleaned_data['filename'])

            if mode == 'clear':
                myquery = defaultfilter
                form = FilterForm()

            table = Grid.objects.filter(myquery).order_by('datetime').reverse()

            if mode == 'printing':
                table = table.reverse()
                shablon = 'printing.html'
            if mode == 'filter':
                pass
    else:
        # В эту ветку попадаем, если пользователем перед этим не был применен фильтр.
        # Например, после Delete или первый заход на страницу
        # Например, после Delete или первый заход на страницу
        table = Grid.objects.filter(defaultfilter).order_by('datetime').reverse()
        form = FilterForm()

    sum_plates = {}
    for m in PrintingPress.objects.all():
        total = table.filter(machine__name=m.name).aggregate(Sum('total_plates'))
        if total['total_plates__sum']:
            sum_plates[m.name] = total['total_plates__sum']

    return render_to_response(shablon, {'table': table, 'form': form, 'sum_plate': sum_plates}, context)


@login_required
def delete(request, rowid):
    #TODO сделать, чтобы после удаления не сбрасывался фильтр
    context = RequestContext(request)

    try:
        row = Grid.objects.get(pk=rowid)
    except row.DoesNotExist:
        raise Http404

    Grid.objects.get(pk=rowid).delete()

    '''
    # context = RequestContext(request)
    # table = Grid.objects.all().order_by('datetime').reverse()
    # form = FilterForm()
    # return render_to_response('grid.html', {'table': table, 'form': form}, context)
    '''
    return redirect('grid')


@job
def processing(pdfName):
    from pdfupload.settings import INPUT_PATH as inputpath
    from pdfupload.settings import TEMP_PATH as tmppath

    # socket.setdefaulttimeout(10.0)

    try:
        tty = '/dev/tty1'
        sys.stdout = open(tty, 'w')
        sys.stderr = open(tty, 'w')
        #sys.stdout.write('filename'+'\n')
    except:
        pass

    print '\n\n'
    print 'START PROCESSING {}'.format(pdfName)
    print '─' * (len(pdfName) + 17)

    #Move pdf to temp
    #-----------------------------------------------------------------

    print(tmppath)
    tempdir = tempfile.mkdtemp(suffix='/', dir=tmppath)
    try:
        shutil.move(inputpath + pdfName, tempdir + pdfName)
    except Exception, e:
        logging.error('{0}: Cant move to temp: {1}'.format(pdfName, e))
        print e
        exit()
    pdf_abs_path = tempdir + pdfName


    #Check if file is PDF
    #-----------------------------------------------------------------
    pdfcheck_command = "file {} | tr -s ':' | cut -f 2 -d ':'".format(pdf_abs_path)
    result_strings = Popen(pdfcheck_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split(',')[0].strip()
    file_is_not_pdf_document = result_strings != 'PDF document'
    print "File is a", result_strings

    pdfExtension = splitext(pdf_abs_path)[1]
    if pdfExtension != ".pdf" or file_is_not_pdf_document:
        logging.error('{0} File is NOT PDF - exiting...'.format(pdfName))
        os.unlink(pdf_abs_path)
        os.removedirs(tempdir)
        fail('{0} File is NOT PDF - exiting...'.format(pdfName))


    #Check if file created with Signa
    #-----------------------------------------------------------------
    valid_signa = analyze_signastation(pdf_abs_path)

    if valid_signa:
        print 'File is a valid PrinectSignaStation file.'
    else:
        print 'File is NOT a valid PrinectSignaStation file.'
        logging.warning('{} created with {}, not Signastation!'.format(pdfName, result_strings))

    #Detect properties
    ##----------------------------------------------------------------
    # machine: plate for machine, it's an INSTANCE of PrintingPress class (AD, SM or PL)
    # complects: number of complects
    # plates: number of plates
    # outputter: Кто выводит - leonov, korol, etc. - это объект типа FTP_server
    # total_pages, total_plates, pdf_colors - страниц, плит, текстовый блок о красочности

    machine = analyze_machine(pdf_abs_path)
    if machine is None:
        logging.error('Cant detect machine for {}'.format(pdfName))
        os.unlink(pdf_abs_path)
        os.removedirs(tempdir)
        fail("Can't detect machine for {}".format(pdfName))
    else:
        print 'Machine sucessfully detected: {}'.format(machine.name)

    complects = analyze_complects(pdf_abs_path)

    # total_pages тут определяется по кол-ву строк, содержащих тэг HDAG_ColorantNames
    if valid_signa:
        total_plates, pdf_colors = analyze_colorant(pdf_abs_path)
    else:
        total_plates, pdf_colors = 0, ''

    paper_sizes = analyze_papersize(pdf_abs_path)

    outputter = detect_outputter(pdfName)
    outputter_ftp = outputter.ftp_account
    preview_ftp = detect_preview_ftp(machine)

    # Переименовываем - из названия PDF удаляется имя выводильщика.
    pdf_abs_path = remove_outputter_title(pdf_abs_path)

    pdfPath, (pdfName, pdfExtension) = dirname(pdf_abs_path), splitext(os.path.basename(pdf_abs_path))


    # Compress via Ghostscript and crop via PyPDF2 library.
    #----------------------------------------------------------------
    croppedtempname = tempdir + pdfName + '.' + outputter.name + '.temp' + pdfExtension
    preview_abs_path = tempdir + pdfName + '.' + outputter.name + pdfExtension

    crop(pdf_abs_path, croppedtempname, paper_sizes)

    gs_compress = "gs -sDEVICE=pdfwrite -dDownsampleColorImages=true " \
                  "-dColorImageResolution=150 -dCompatibilityLevel=1.4 " \
                  "-dNOPAUSE -dBATCH -sOutputFile={output} {input} | grep 'Page'" \
                  .format(input=croppedtempname, output=preview_abs_path)

    print '\n-->Starting PDF preview compression...'
    os.system(gs_compress)
    print 'Compression finished.'


    # Make JPEG preview for Grid (only first page)
    # #----------------------------------------------------------------
    #  Для этой операции используется созданный на предыдущем шаге кропленый документ
    jpeg = os.path.join(settings.STATIC_ROOT, 'jpg', pdfName + '.jpg')
    thumb = os.path.join(settings.STATIC_ROOT, 'jpg', pdfName + '_thumb' + '.jpg')
    gs_compress = "gs -sDEVICE=jpeg -dFirstPage=1 -dLastPage=1 -dJPEGQ=80 -r{resolution}"\
                  "-dNOPAUSE -dBATCH -sOutputFile={output} {input} " \
                  .format(resolution='200', input=croppedtempname, output=jpeg)

    make_thumb = "convert {input} -resize 175 {output}".format(input=jpeg, output=thumb)
    make_jpeg = "convert {input} -resize 2500 {output}".format(input=jpeg, output=jpeg)

    print '\n-->Starting Jpeg preview compression...'
    os.system(gs_compress)
    os.system(make_thumb)
    os.system(make_jpeg)
    print 'Compression finished.'


    # Сalculating ink coverage
    # #----------------------------------------------------------------
    #  Снова используется созданный на предыдущем шаге кропленый документ, здесь он уничтожается.
    inks = analyze_inkcoverage(croppedtempname)
    os.unlink(croppedtempname)


    ### CUSTOM OPERATION DEPENDS ON OUTPUTTER
    ##----------------------------------------------------------------
    if outputter.name == 'Leonov':
        if (machine.plate_w, machine.plate_h) == (1030, 770):
            outputter_ftp.todir = '_1030x770'
        elif (machine.plate_w, machine.plate_h) == (1010, 820):
            outputter_ftp.todir = '_1010x820'
        elif (machine.plate_w, machine.plate_h) == (740, 575):
            outputter_ftp.todir = '_ADAST'
        else:
            outputter_ftp.todir = ''

    if outputter.name == 'Korol':
        # may be rotate90?

        # add numper of plates to pdf name
        colorstring = colorant_to_string(pdf_colors)

        #add label representing paper width for Korol
        #если файл не сигновский, то colorstring="", цвета не определяются
        if colorstring:
            newname = pdfName + '_' + str(machine.plate_w) + '_' + str(total_plates) + 'Plates' + colorstring + pdfExtension
        else:
            newname = pdfName + '_' + str(machine.plate_w) + pdfExtension

        shutil.move(pdf_abs_path, tempdir + newname)
        pdfname = newname
        pdf_abs_path = tempdir + newname


    # Send Preview PDF to printing press FTP
    ##----------------------------------------------------------------
    if os.path.isfile(preview_abs_path):
        if preview_ftp:
            status_kinap, e_kinap = sendfile(preview_abs_path, preview_ftp)
        else:
            status_kinap, e_kinap = False, "Unknown press or no ftp"
    else:
        print 'Preview not found and not upload'
        status_kinap, e_kinap = False, 'Preview not found'


    # Send Original PDF to Outputter
    ##----------------------------------------------------------------
    status_outputter, e_outputter = sendfile(pdf_abs_path, outputter_ftp)


    # Send SMS via http://smsc.ua/
    ##----------------------------------------------------------------
    try:
        if status_outputter:
            smsc = smsc_api.SMSC()
            phone = outputter.sms_receiver.phone
            message = '{} {} вывод {} пл.{}'.format(pdfName, machine.name, outputter.name, str(total_plates))
            status = smsc.send_sms(phone, message)
            #TODO вываливается эксепшн, если нет status'а. Временно тупо обернул в try
            try:
                print '\n--> SMS send to {} with status: {}'.format(outputter.sms_receiver.name, status)
                print 'SMS text: {}'.format(message)
            except Exception, e:
                print 'error:', e
    except Exception, e:
        logging.error('Send sms exception: {0}'.format(e))
        print '\nSend sms: probably, no phone number'

    # Запись в БД
    ##----------------------------------------------------------------
    contractor_error = error_text(status_outputter, e_outputter)
    preview_error = error_text(status_kinap, e_kinap)
    if not status_outputter:
        bg = 'danger'
    elif not status_kinap:
        bg = 'warning'
    else:
        bg = 'default'

    try:
        row = Grid()
        row.datetime = timezone.now()
        row.pdfname = pdfName
        row.machine = machine
        row.total_pages = complects
        row.total_plates = total_plates
        row.contractor = outputter
        row.contractor_error = contractor_error
        row.preview_error = preview_error
        row.colors = dict_to_multiline(pdf_colors)
        row.inks = inks_to_multiline(inks)
        row.bg = bg
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
        row.save()
    except Exception, e:
        print 'ERROR row.save:', e

    # Очистка и окончание выполнения
    ##----------------------------------------------------------------
    try:
        os.unlink(pdf_abs_path)
        os.unlink(preview_abs_path)
        shutil.rmtree(tempdir)
        print 'SUCCESSFULLY finish.'
    except Exception, e:
        print 'SUCCESSFULLY finish, but problem with cleaning:', e