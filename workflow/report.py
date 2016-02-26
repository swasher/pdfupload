# coding: utf-8

import calendar

from django.shortcuts import render_to_response
from django.db.models import Sum, Min, Max
from django.contrib.auth.decorators import login_required
from django.shortcuts import RequestContext

from models import Grid
from models import PrintingPress

# Какие хочу графики:
# - всего плит/месяц и м2/месяц
# - денег в месяц
# - по машинам плит в месяц

@login_required()
def report(request):

    context = RequestContext(request)

    class chart():
        def __init__(self, year, chartdata, charttype, chartcontainer, extra):
            self.year = year
            self.chartdata = chartdata
            self.charttype = charttype
            self.chartcontainer = chartcontainer
            self.extra = extra

    # минимальный и максимальный года
    min_year = Grid.objects.all().aggregate(Min('datetime'))['datetime__min'].year
    max_year = Grid.objects.all().aggregate(Max('datetime'))['datetime__max'].year

    # выборка только по этим машинам
    primary_machines = PrintingPress.objects.filter(name__in=['Speedmaster', 'Dominant', 'Planeta'])

    # Создаем список для оси x - двенадцать месяцов. Используется во всех графиках.
    x_axis_month = []
    for month in range(1, 13):
        x_axis_month.append(calendar.month_name[month])


    """
    ### График - всего плит за месяц
    chart1 = []
    for year in range(min_year, max_year+1):
        plates_per_month = []
        for month in range(1, 13):
            plates = Grid.objects.filter(datetime__year=year, datetime__month=month).aggregate(Sum('total_plates'))['total_plates__sum']
            # debug print 'month', calendar.month_name[month], 'plates', plates
            plates_per_month.append(plates)

        chartdata = {'x': x_axis_month, 'y': plates_per_month}
        charttype = 'discreteBarChart'
        chartcontainer = 'discretebarchart_container{}'.format(year)
        extra = {
            #'name': 'chart{}'.format(year),
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
            }
        chart1.append(chart(year, chartdata, charttype, chartcontainer, extra))
    """

    ### График - всего плит за месяц VERSION2
    chart1 = []
    print '\n'
    for year in range(min_year, max_year+1):
        plates_array = []
        area_array = []
        chartdata = {}

        print 'YEAR', year

        for month in range(1, 13):
            plates = Grid.objects.filter(datetime__year=year, datetime__month=month).aggregate(Sum('total_plates'))['total_plates__sum']
            plates_array.append(plates)

            area = 0
            for machine in PrintingPress.objects.all():
                plates_per_machine = Grid.objects.filter(machine=machine, datetime__year=year, datetime__month=month).aggregate(Sum('total_plates'))['total_plates__sum']
                plates_per_machine = int(plates_per_machine or 0)
                area += (plates_per_machine * machine.plate_w * machine.plate_h)/1000000
            area_array.append(area)

        chartdata['x'] = x_axis_month
        chartdata['name1'] = 'Total plates'
        chartdata['name2'] = 'Total m2'
        chartdata['y1'] = plates_array
        chartdata['y2'] = area_array

        charttype = 'multiBarChart'
        chartcontainer = 'total_multibarchart_container{}'.format(year)
        extra = {
            #'name': 'chart{}'.format(year),
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
            }
        chart1.append(chart(year, chartdata, charttype, chartcontainer, extra))


    ### Мультибар график - всего плит за месяц по каждой машине
    chart2 = []
    for year in range(min_year, max_year+1):
        chartdata = {}
        chartdata['x'] = x_axis_month
        for i, machine in enumerate(primary_machines, 1):
            ydata = []
            for month in range(1, 13):
                plates = Grid.objects.filter(machine=machine, datetime__year=year, datetime__month=month).aggregate(Sum('total_plates'))['total_plates__sum']
                #print 'machine', machine, 'month', calendar.month_name[month], 'plates', plates
                ydata.append(plates)
            chartdata['name{}'.format(i)] = machine.name
            chartdata['y{}'.format(i)] = ydata
            #print 'I=', i, 'YEAR', year, 'machine', machine.name, 'DATA', ydata, '\r'


        """
        ydata1 = [12, 16, 8, 8, 16, 14, 12, 20, 8, 2]
        ydata2 = [18, 24, 12, 12, 24, 21, 18, 30, 12, 3]
        ydata3 = [6, 8, 4, 4, 8, 7, 6, 10, 4, 1]

        chartdata = {
            'x': x_axis_month,
            'name1': 'series 1', 'y1': ydata1,
            'name2': 'series 2', 'y2': ydata2,
            'name3': 'series 3', 'y3': ydata3}
        """

        charttype = "multiBarChart"
        chartcontainer = 'plates_multibarchart_container{}'.format(year)
        extra = {
            #'name': 'chart{}'.format(year),
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
            }

        chart2.append(chart(year, chartdata, charttype, chartcontainer, extra))


    ### График денег в месяц
    chart3 = []
    for year in range(min_year, max_year+1):
        dollars_per_month = []
        for month in range(1, 13):
            dollars = 0
            for machine in primary_machines:
                plates = Grid.objects.filter(machine=machine, datetime__year=year, datetime__month=month).aggregate(Sum('total_plates'))['total_plates__sum']
                dollars += (plates or 0) * machine.cost  #Becouse plates can be None
            dollars_per_month.append(dollars)

        chartdata = {'x': x_axis_month, 'y': dollars_per_month}
        charttype = 'discreteBarChart'
        chartcontainer = 'money_discretebarchart_container{}'.format(year)
        extra = {
            #'name': 'chart{}'.format(year),
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
            }
        chart3.append(chart(year, chartdata, charttype, chartcontainer, extra))


    ### This is very useful for test chart data
    #import pprintpp
    # print 'CHART1', len(chart1)
    # for k in chart1:
    #     print 'YEAR', k.year
    #     print k.chartcontainer
    #     pprintpp.pprint(k.chartdata, width=150)
    #
    # print 'CHART2', len(chart2)
    # for k in chart2:
    #     print 'YEAR', k.year
    #     print k.chartcontainer
    #     pprintpp.pprint(k.chartdata, width=150)

    #print 'CHART3', len(chart3)

    # for k in chart3:
    #     print 'YEAR', k.year
    #     print k.chartcontainer
    #     pprintpp.pprint(k.chartdata, width=150)

    return render_to_response('report.html', {'chart1':chart1, 'chart2':chart2, 'chart3':chart3}, context)
