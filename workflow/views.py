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
#TODO Разобраться с багом, когда в названии файла русские буквы И пробелы. Но это уже при переходе на Python 3
#TODO Цена на пластины должна быть дробной
#TODO Переделать нумерацию страниц во всех analyze, чтобы начиналась не с первой, а с нулевой. Большая кропотливая работа. ХЗ надо ли вообще
#TODO В функции crop() используется метод рассчета размера изображения bbox, его надо перенести в analyze_paper()

import os
import logging
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import Http404
from django.shortcuts import render
from django.http import JsonResponse
from django_rq import job
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Sum
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import FilterForm
from .models import Grid, PrintingPress
from .classes import PDF

from .analyze import analyze_inkcoverage
from .action import remove_ctpbureau_from_pdfname
from .action import crop
from .action import compress
from .action import generating_jpeg
from .action import custom_operations
from .action import upload_to_press
from .action import upload_to_ctpbureau
from .action import send_sms
from .action import send_telegram
from .action import save_bd_record
from .action import cleaning_temps
from .util import read_shelve
from .util import write_shelve

logger = logging.getLogger(__name__)


def about(request):
    with open('timestamp', 'r') as f:
        timestamp = f.read()
    return render(request, 'about.html', {'timestamp': timestamp})


@ensure_csrf_cookie
def change_import(request):
    import_mode = read_shelve()

    if request.is_ajax():
        import_mode = not import_mode
        write_shelve(import_mode)

    results = {'import_mode': import_mode}

    return JsonResponse(results)


def grid(request, mode=''):

    import_mode = read_shelve()

    myquery = Q()
    # Фильтр по умолчанию - за последние n дней.
    n = 60
    start = datetime.datetime.now() - datetime.timedelta(days=n)
    end = datetime.datetime.now()
    defaultfilter = Q(datetime__range=(start, end))

    # Если не указано иное, то по умолчанию используется темплайт grid
    shablon = 'grid.html'

    if request.method == 'GET':
        # В эту ветку мы можем попасть, если нажато Filter или Print или Clear
        form = FilterForm(request.GET)
        if form.is_valid():
            """
            DEPRECATED
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
            """

            #### НОВАЯ ЛОГИКА ####

            # Если пользователь задал хотя бы один фильтр, то применяем только явно заданные фильтры. Иначе применяем фильтр "за последние два месяца".
            if form.cleaned_data['from_date'] or form.cleaned_data['to_date'] or form.cleaned_data['contractor'] or form.cleaned_data['machine'] or form.cleaned_data['filename']:

                # Если заданы обе даты, то делаем выборку между ними, иначе проверяем, задана ли начальная дата, и делаем выборку от нее по today
                if form.cleaned_data['from_date'] and form.cleaned_data['to_date']:
                    start = form.cleaned_data['from_date']
                    end = form.cleaned_data['to_date'] + datetime.timedelta(days=1)
                    myquery &= Q(datetime__range=(start, end))
                elif form.cleaned_data['from_date']:
                    start = form.cleaned_data['from_date']
                    end = datetime.datetime.now() + datetime.timedelta(days=1)
                    myquery &= Q(datetime__range=(start, end))

                if form.cleaned_data['contractor']:
                    myquery &= Q(contractor__exact=form.cleaned_data['contractor'])
                if form.cleaned_data['machine']:
                    myquery &= Q(machine__exact=form.cleaned_data['machine'])

                # Если предварить фильтр по имени файла дефисом, то это исключит имена, вместо добавления
                if form.cleaned_data['filename']:
                    if form.cleaned_data['filename'][0] == '-':
                        myquery &= ~Q(pdfname__icontains=form.cleaned_data['filename'][1:])
                    else:
                        myquery &= Q(pdfname__icontains=form.cleaned_data['filename'])
            else:
                myquery &= defaultfilter

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

    return render(request, shablon, {'table': table, 'form': form, 'sum_plate': sum_plates, 'import_mode': import_mode})


@login_required
@ensure_csrf_cookie
def delete_row_ajax(request):
    if request.is_ajax() and request.method == u'POST':
        POST = request.POST
        if 'pk' in POST:
            pk = int(POST['pk'])

            try:
                row = Grid.objects.get(pk=pk)
            except ObjectDoesNotExist:
                raise Http404

            # deleting jpegs linked to db record
            if os.path.isfile(row.proof.path):
                os.unlink(row.proof.path)
            if os.path.isfile(row.thumb.path):
                os.unlink(row.thumb.path)

            order = "{0:0>4}".format(row.order) # add leading zeros for 4-signed format, ex: 0021, 0003
            Grid.objects.get(pk=pk).delete()

    # deprecated: jquery function do not wait for result now
    json = {'order': order}
    return JsonResponse(json)

from decouple import config

@job
def processing(pdfName):
    # socket.setdefaulttimeout(10.0)

    pdf = PDF(pdfName)

    # Переименовываем - из названия PDF удаляется имя выводильщика
    remove_ctpbureau_from_pdfname(pdf)

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

    # Send Preview PDF to press FTP
    pdf.upload_to_press_status, pdf.upload_to_press_error = upload_to_press(pdf)

    # Send Original PDF to Outputter
    pdf.upload_to_ctpbureau_status, pdf.upload_to_ctpbureau_error = upload_to_ctpbureau(pdf)

    # Send SMS via http://smsc.ua/
    send_sms(pdf)
    send_telegram(pdf)

    # Запись в БД
    save_bd_record(pdf)

    # Удаление временных файлов
    cleaning_temps(pdf)
