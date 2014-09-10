# coding: utf-8
__author__ = 'swasher'

from workflow.models import Grid

from django import forms
from workflow.models import Outputter, PrintingPress
from datetimewidget.widgets import DateWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, ButtonHolder, Layout, Field
from crispy_forms.bootstrap import StrictButton, FormActions


class FilterForm(forms.ModelForm):

    #def __init__(self, *args, **kwargs):
        #self.fields['machine'].widget.attrs['class'] = 'selectpicker'
        # self.machine.widget.attrs['class'] = 'selectpicker'
        # self.helper = FormHelper()
        # self.helper.form_method = 'post'
        # self.helper.form_action = 'grid'
        # # self.helper.add_input(Submit('submit', 'Filter'))
        # self.helper.form_class = 'form-inline'
        # self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        # self.helper.layout = Layout(Field('from_date'),
        #                             Field('contractor', css_class="input"),
        #                             ButtonHolder(Submit('submit',
        #                                                 'Submit',
        #                                                 css_class='button white')),
        #                     FormActions(Submit('submit', "Submit", css_class='btn'),
        #                                 Submit('cancel', "Cancel", css_class='btn')))
        # super(FilterForm, self).__init__(*args, **kwargs)


    from_date = forms.DateField(
        widget=DateWidget(attrs={'weekStart': '3', 'autoclose': 'false'},
                          usel10n=True,
                          bootstrap_version=3),
        required=False
    )

    to_date = forms.DateField(
        widget=DateWidget(attrs={'weekStart': '4'}, usel10n=True, bootstrap_version=3),
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
            'autoclose': 'true',
            'showMeridian': 'false',
            'weekStart': '4',
        }

        # (attrs={'id': "id_datetime"},
        #                            usel10n=True,
        #                            bootstrap_version=3)

        widgets = {
            'datetime': DateWidget(options=dateOptions)
        }
