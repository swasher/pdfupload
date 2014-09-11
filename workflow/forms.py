# coding: utf-8
__author__ = 'swasher'

from workflow.models import Grid

from django import forms
from workflow.models import Outputter, PrintingPress
from datetimewidget.widgets import DateWidget


class FilterForm(forms.ModelForm):

    from_date = forms.DateField(
        #widget=DateWidget(attrs={'weekStart': '3', 'autoclose': 'false'}, usel10n=True, bootstrap_version=3),
        widget=DateWidget(usel10n=True, bootstrap_version=3),
        required=False
    )

    to_date = forms.DateField(
        #widget=DateWidget(attrs={'weekStart': '4'}, usel10n=True, bootstrap_version=3),
        widget=DateWidget(usel10n=False, bootstrap_version=3),
        required=False
    )

    contractor = forms.ModelChoiceField(
        #label="Подрядчик",
        queryset=Outputter.objects.all(),
        required=False,
        empty_label='Подрядчик',
        widget=forms.Select(attrs={'class': 'selectpicker span1'})
    )

    machine = forms.ModelChoiceField(
        #label="Машина",
        queryset=PrintingPress.objects.all(),
        required=False,
        empty_label='Машина',
        widget=forms.Select(attrs={'class': 'selectpicker'})
    )

    class Meta:
        model = Grid
        fields = ['from_date', 'to_date', 'contractor', 'machine']

        dateOptions = {
            'format': 'dd/mm/yyyy HH:ii P',
            'autoclose': 'false',
            'showMeridian': 'false',
            'weekStart': '4',
            'todayBtn': 'true',
        }

        widgets = {
            'from_date': DateWidget(options=dateOptions),
            'to_date': DateWidget(options=dateOptions)
        }
