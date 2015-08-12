# coding: utf-8

# ---------- TO-DO -----------
#TODO логирование действий пользователя
#TODO Проверить на пригодность использования The tiffsep device also prints the names of any spot colors
#       detected within a document to stderr. (stderr is also used for the output from the bbox device.)
#       For each spot color, the name of the color is printed preceded by '%%SeparationName: '. This provides a simple
#       mechanism for users and external applications to be informed about the names of spot colors within a document.
#TODO Что должно происходить, если форма не валидна?
#TODO Сделать кнопку 'перезалить на кинап'
#TODO Аналогично кнопка run
#TODO Ротация логов nginx
#TODO Разобраться с багом, когда в названии файла русские буквы. Но это уже при переходе на Python 3
#TODO Цена на пластины должна быть дробной
#TODO Переделать нумерацию страниц во всех analyze, чтобы начиналась не с первой, а с нулевой. Большая кропотливая работа. ХЗ надо ли вообще

import os
import sys
import logging
import datetime

from django.conf import settings
from django.shortcuts import RequestContext, Http404, redirect, render_to_response
from django_rq import job
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Sum

from forms import FilterForm
from models import Grid, PrintingPress
from classes import PDF

from analyze import analyze_inkcoverage

from action import remove_outputter_title
from action import crop
from action import compress
from action import generating_jpeg
from action import custom_operations
from action import upload_to_press
from action import upload_to_outputter
from action import send_sms
from action import save_bd_record
from action import cleaning_temps

logger = logging.getLogger(__name__)


def about(request):
    return render_to_response('about.html')


@login_required
def usersettings(request):
    return render_to_response('usersettings.html')


def printing(request):
    pass


def log(request):
    return render_to_response('log.html')


def grid(request, mode=''):

    try:
        sys.stdout = open(settings.TTY, 'w')
        sys.stderr = open(settings.TTY, 'w')
        #sys.stdout.write('filename'+'\n')
    except:
        pass

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

    # deleting jpegs linked to db record
    if os.path.isfile(row.proof.path):
        os.unlink(row.proof.path)
    if os.path.isfile(row.thumb.path):
        os.unlink(row.thumb.path)

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
    # socket.setdefaulttimeout(10.0)

    try:
        sys.stdout = open(settings.TTY, 'w')
        sys.stderr = open(settings.TTY, 'w')
        #sys.stdout.write('filename'+'\n')
    except:
        pass

    print '\n\n'
    print 'START PROCESSING {}'.format(pdfName)
    print '─' * (len(pdfName) + 17)

    pdf = PDF(pdfName)

    # Переименовываем - из названия PDF удаляется имя выводильщика
    remove_outputter_title(pdf)

    # Crop via PyPDF2 library
    crop(pdf)

    # Compress via Ghostscript
    compress(pdf)

    # Make JPEG preview for Grid (only first page)
    generating_jpeg(pdf)

    # Сalculating ink coverage
    pdf.inks = analyze_inkcoverage(pdf.cropped_file)

    # Custom operation depends on outputter
    custom_operations(pdf)

    # Send Preview PDF to printing press FTP
    upload_to_press(pdf)

    # Send Original PDF to Outputter
    upload_to_outputter(pdf)

    # Send SMS via http://smsc.ua/
    send_sms(pdf)

    # Запись в БД
    save_bd_record(pdf)

    # Удаление временных файлов
    cleaning_temps(pdf)
