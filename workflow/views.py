# coding: utf-8

# ####### TO-DO ###############################
#TODO превьюхи
#TODO кнопка run
#TODO перевести supervisor в low-priv юзера
#TODO переделать даты, чтобы работали без range, и сделать дефолтную дату 'от', например, -60 от now() или текущий пнд.
#TODO если незалогиненный юзер жмет "удалить", редиректить его не на login, а на grid, и выводить красный warning
#TODO логирование действий пользователя
#TODO Проверить на пригодность использования The tiffsep device also prints the names of any spot colors detected within a document to stderr. (stderr is also used for the output from the bbox device.) For each spot color, the name of the color is printed preceded by '%%SeparationName: '. This provides a simple mechanism for users and external applications to be informed about the names of spot colors within a document.
#####

import sys
import os
#import socket
import shutil
import tempfile
import logging
import datetime

from os.path import dirname, splitext
from django.conf import settings
from django.shortcuts import render_to_response, RequestContext,  HttpResponseRedirect, Http404, redirect
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

from analyze import analyze, analyze_colorant, analyze_papersize, detect_outputter, \
    analyze_inkcoverage, detect_preview_ftp, analyze_colorant_korol
from util import inks_to_multiline, dict_to_multiline, remove_outputter_title, crop, \
    sendfile, error_text


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


def grid(request):
    context = RequestContext(request)
    # по умолчанию таблица фильтруется за последние days дней
    # table = Grid.objects\
    #     .filter(datetime__gte=(datetime.datetime.now()-datetime.timedelta(days=1)))\
    #     .order_by('datetime')\
    #     .reverse()
    table = Grid.objects.all().order_by('datetime').reverse()


    TTY = '/dev/tty1'
    sys.stdout = open(TTY, 'w')
    sys.stderr = open(TTY, 'w')
    #sys.stdout.write('filename'+'\n')

    if request.method == 'POST':  # If the form has been submitted...
        form = FilterForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            myquery = Q()
            if form.cleaned_data['from_date'] and form.cleaned_data['to_date']:
                start = form.cleaned_data['from_date']
                end = form.cleaned_data['to_date'] + datetime.timedelta(days=1)
                myquery &= Q(datetime__range=(start, end))
            if form.cleaned_data['contractor']:
                myquery &= Q(contractor__exact=form.cleaned_data['contractor'])
            if form.cleaned_data['machine']:
                myquery &= Q(machine__exact=form.cleaned_data['machine'])
            if form.cleaned_data['filename']:
                myquery &= Q(pdfname__icontains=form.cleaned_data['filename'])
            #table = Grid.objects.filter(Q(contractor=contractor), Q(machine=machine), myquery)
            table = Grid.objects.filter(myquery).order_by('datetime').reverse()
    else:
        form = FilterForm()

    sum_plates = {}
    for m in PrintingPress.objects.all():
        total = table.filter(machine__name=m.name).aggregate(Sum('total_plates'))
        if total['total_plates__sum']:
            sum_plates[m.name] = total['total_plates__sum']

    return render_to_response('grid.html', {'table': table, 'form': form, 'sum_plate': sum_plates}, context)


@login_required
def delete(request, rowid):
    #TODO сделать, чтобы после удаления не сбрасывался фильтр
    context = RequestContext(request)

    try:
        row = Grid.objects.get(pk=rowid)
    except row.DoesNotExist:
        raise Http404

    Grid.objects.get(pk=rowid).delete()

    # context = RequestContext(request)
    # table = Grid.objects.all().order_by('datetime').reverse()
    # form = FilterForm()
    # return render_to_response('grid.html', {'table': table, 'form': form}, context)
    return redirect('grid', context)


@job
def processing(pdfName):

    # socket.setdefaulttimeout(10.0)

    TTY = '/dev/tty1'
    sys.stdout = open(TTY, 'w')
    sys.stderr = open(TTY, 'w')  # Теперь print пишет в назначенный TTY

    tmppath = BASE_DIR + '/tmp/'
    inputpath = BASE_DIR + '/input_django/'

    print '\n\n'
    print 'START PROCESSING {}'.format(pdfName)
    print '─'*(len(pdfName)+17)

    #Move pdf to temp
    #-----------------------------------------------------------------

    tempdir = tempfile.mkdtemp(suffix='/', dir=tmppath)
    try:
        shutil.move(inputpath+pdfName, tempdir+pdfName)
    except Exception, e:
        logging.error('{0}: Cant move to temp: {1}'.format(pdfName, e))
        print e
        exit()
    pdf_abs_path = tempdir+pdfName

    #Check if file is PDF
    #-----------------------------------------------------------------
    pdfcheck_command = "file {} | tr -s ':' | cut -f 2 -d ':'".format(pdf_abs_path)
    result_strings = Popen(pdfcheck_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split(',')[0].strip()
    file_is_not_pdf_document = result_strings != 'PDF document'
    print "File is a", result_strings

    pdfExtension = splitext(pdf_abs_path)[1]
    if pdfExtension != ".pdf" or file_is_not_pdf_document:
        logging.error('{0} File is NOT PDF - exiting...'.format(pdfName))
        print('{0} File is NOT PDF - exiting...'.format(pdfName))
        os.unlink(pdf_abs_path)
        os.removedirs(tempdir)
        exit()


    #Check if file created with Signa
    #-----------------------------------------------------------------
    pdfinfo_command = "pdfinfo {} | grep Creator | tr -s ' ' | cut -f 2 -d ' '".format(pdf_abs_path)
    result_strings = Popen(pdfinfo_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().strip()
    if result_strings == 'PrinectSignaStation':
        print 'File is a valid PrinectSignaStation file.'
    else:
        print 'File is NOT a valid PrinectSignaStation file.'
        logging.warning('{} created with {}, not Signastation!'.format(pdfName, result_strings))
        #TODO продумать, что делать, если файл не сигновский

    #Detect properties
    ##----------------------------------------------------------------
    # machine: plate for machine, it's an INSTANCE of PrintingPress class (AD, SM or PL)
    # plates: number of plates
    # outputter: Кто выводит - leonov, korol, etc. - это объект типа FTP_server
    # total_pages, total_plates, pdf_colors - страниц, плит, текстовый блок о красочности

    machine, complects = analyze(pdf_abs_path)

    if machine is None:
        logging.error('Cant detect machine for {}'.format(pdfName))
        print 'Cant detect machine for {}'.format(pdfName)
        print 'Exiting...'
        os.unlink(pdf_abs_path)
        os.removedirs(tempdir)
        exit()

    # total_pages тут определяется по кол-ву строк, содержащих тэг HDAG_ColorantNames
    total_plates, pdf_colors = analyze_colorant(pdf_abs_path)

    paper_size = analyze_papersize(pdf_abs_path)

    outputter = detect_outputter(pdfName)
    outputter_ftp = outputter.ftp_account
    preview_ftp = detect_preview_ftp(machine)

    # Переименовываем - из названия PDF удаляется имя выводильщика.
    pdf_abs_path = remove_outputter_title(pdf_abs_path)

    pdfPath, (pdfName, pdfExtension) = dirname(pdf_abs_path), splitext(os.path.basename(pdf_abs_path))


    # Проверка, соответствует ли PDF известному формату пластины
    # #----------------------------------------------------------------
    # TODO Проверка, соответствует ли PDF известному формату пластины


    # Compress via Ghostscript and crop via PyPDF2 library.
    #----------------------------------------------------------------
    previewname = pdfName + '.' + outputter.name + pdfExtension
    croppedtempname = tempdir + pdfName + '.' + outputter.name + '.temp' + pdfExtension
    preview_abs_path = tempdir + pdfName + '.' + outputter.name + pdfExtension

    crop(pdf_abs_path, croppedtempname)

    gs_compress = "gs -sDEVICE=pdfwrite -dDownsampleColorImages=true " \
                  "-dColorImageResolution=120 -dCompatibilityLevel=1.4 " \
                  "-dNOPAUSE -dBATCH -sOutputFile={output} {input} | grep 'Page'" \
                  .format(input=croppedtempname, output=preview_abs_path)

    print '\n-->Staring PDF preview compression...'
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

    print '\n-->Staring Jpeg preview compression...'

    import time

    class Profiler(object):
        def __enter__(self):
            self._startTime = time.time()

        def __exit__(self, type, value, traceback):
            print "Elapsed time: {:.3f} sec".format(time.time() - self._startTime)

    with Profiler() as p:
        os.system(gs_compress)
    with Profiler() as p:
        os.system(make_thumb)
    with Profiler() as p:
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
        if machine.name == 'Speedmaster':
            outputter_ftp.todir = '_1030x770'
        elif machine.name == 'Planeta':
            outputter_ftp.todir = '_1010x820'
        elif machine.name == 'Dominant':
            outputter_ftp.todir = '_ADAST'
        else:
            outputter_ftp.todir = ''

    if outputter.name == 'Korol':
        # may be rotate90?

        # add numper of plates to pdf name
        colorstring = analyze_colorant_korol(pdf_abs_path)

        ###add label representing paper width for Korol
        newname = pdfName + '_' + str(machine.plate_w) + '_' + str(total_plates) + 'Plates' + colorstring + pdfExtension
        shutil.move(pdf_abs_path, tempdir + newname)
        pdfname = newname
        pdf_abs_path = tempdir + newname


    # Send Preview PDF to printing press FTP
    ##----------------------------------------------------------------
    if os.path.isfile(preview_abs_path):
        if preview_ftp:
            status_kinap, e_kinap = sendfile(preview_abs_path, preview_ftp)
        else:
            status_kinap, e_kinap = False, "Machine can't be detected or don't have ftp"
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
            print '--> SMS send to {} with status: {}'.format(outputter.sms_receiver.name, status)
    except Exception, e:
        logging.error('Send sms exception: {0}'.format(e))
        print 'Send sms exception: {0}'.format(e)


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

    row = Grid()
    #row.datetime = now
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
    row.save()

    # Очистка и окончание выполнения
    ##----------------------------------------------------------------
    try:
        os.unlink(pdf_abs_path)
        os.unlink(preview_abs_path)
        shutil.rmtree(tempdir)
        print '\nSUCCESSFULLY finish.'
    except Exception, e:
        print 'SUCCESSFULLY finish, but problem with cleaning:', e