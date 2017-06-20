from django import forms
from core.models import Customer

class MyForm(forms.ModelForm):
    pass

class FilterForm(forms.ModelForm):

    contractor = forms.ModelChoiceField(
        #label="Подрядчик",
        queryset=Customer.objects.filter(unc__isnull=False),
        required=True,
        empty_label='Заказчик',
        widget=forms.Select(attrs={'class': 'selectpicker'})   # work with Bootstrap 3 and bootstrap-select
    )

    class Meta:
        model = Customer
        fields = ['customer', 'filename', 'approved', 'approved_date']
