# coding: utf-8
__author__ = 'swasher'

from workflow.models import Grid
from django import forms
from workflow.models import Outputter, PrintingPress
from bootstrap3_datetime.widgets import DateTimePicker


class FilterForm(forms.ModelForm):

    from_date = forms.DateField(
        widget=DateTimePicker(options={"format": "DD.MM.YYYY",
                                       "locale": 'ru'
                                       },
                                attrs = {'class': 'form-control input-sm',
                                         'placeholder':'нач. дата'}
                              ),
        required=False
    )

    to_date = forms.DateField(
        widget=DateTimePicker(options={"format": "DD.MM.YYYY",
                                       "locale": 'ru'
                                       },
                              attrs = {'class': 'form-control input-sm',
                                       'placeholder':'кон. дата'
                                       }
                              ),
        required=False
    )

    contractor = forms.ModelChoiceField(
        #label="Подрядчик",
        queryset=Outputter.objects.all(),
        required=False,
        empty_label='Подрядчик',
        widget=forms.Select(attrs={'class': 'selectpicker col-sm'})
    )

    machine = forms.ModelChoiceField(
        #label="Машина",
        queryset=PrintingPress.objects.all(),
        required=False,
        empty_label='Машина',
        widget=forms.Select(attrs={'class': 'selectpicker col-sm'})
    )

    filename = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control input-sm', 'placeholder': 'фильтр по слову'}),
        required=False
    )

    class Meta:
        model = Grid
        fields = ['from_date', 'to_date', 'contractor', 'machine']
