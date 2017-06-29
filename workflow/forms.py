# coding: utf-8
__author__ = 'swasher'

from workflow.models import Grid
from django import forms
from workflow.models import PrintingPress
from core.models import Contractor
from bootstrap3_datetime.widgets import DateTimePicker


class FilterForm(forms.ModelForm):

    from_date = forms.DateField(
        widget=DateTimePicker(options={"format": "DD.MM.YYYY",
                                       "locale": 'ru'
                                       },
                              attrs={'class': 'form-control input-sm',
                                     'placeholder':'начальная дата'}
                              ),
        required=False
    )

    to_date = forms.DateField(
        widget=DateTimePicker(options={"format": "DD.MM.YYYY",
                                       "locale": 'ru'
                                       },
                              attrs={'class': 'form-control input-sm',
                                       'placeholder':'конечная дата'
                                       }
                              ),
        required=False
    )

    contractor = forms.ModelChoiceField(
        #label="Подрядчик",
        queryset=Contractor.objects.all().filter(produce__exact='ctp'),
        required=False,
        empty_label='Подрядчик',
        widget=forms.Select(attrs={'class': 'selectpicker col-sm'})   # work with Bootstrap 3 and bootstrap-select
    )

    machine = forms.ModelChoiceField(
        #label="Машина",
        queryset=PrintingPress.objects.all(),
        required=False,
        empty_label='Машина',
        widget=forms.Select(attrs={'class': 'selectpicker col-sm'})   # work with Bootstrap 3 and bootstrap-select
    )

    filename = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'фильтр по слову'}),
        required=False
    )

    class Meta:
        model = Grid
        fields = ['from_date', 'to_date', 'contractor', 'machine']
