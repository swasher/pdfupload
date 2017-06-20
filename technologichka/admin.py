# coding: utf-8

from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.db.models import Max
from django.forms import Textarea, TextInput

from technologichka.models import Order, PrintSheet, OperationList, Operation, Detal
from core.models import Contractor


#from nested_inline.admin import NestedStackedInline, NestedTabularInline, NestedModelAdmin



# START ##############################################################################################################
# Декоратор для добавление поля-линка
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned
from django.utils.safestring import mark_safe


def add_link_field(target_model=None, field='', app='', field_name='link', link_text=str, short_description=None):
    """
    decorator that automatically links to a model instance in the admin;
    inspired by http://stackoverflow.com/questions/9919780/how-do-i-add-a-link-from-the-django-admin-page-of-one-object-
    to-the-admin-page-o
    :param target_model: modelname.lower or model
    :param field: fieldname
    :param app: appname
    :param field_name: resulting field name
    :param link_text: callback to link text function
    :param short_description: list header
    :return:
    """
    def add_link(cls):
        reverse_name = target_model or cls.model.__name__.lower()

        def link(self, instance):
            app_name = app or instance._meta.app_label
            reverse_path = "admin:%s_%s_change" % (app_name, reverse_name)
            link_obj = getattr(instance, field, None) or instance

            # manyrelatedmanager with one result?
            if link_obj.__class__.__name__ == "RelatedManager":
                try:
                    link_obj = link_obj.get()
                except MultipleObjectsReturned:
                    return u"multiple, can't link"
                except link_obj.model.DoesNotExist:
                    return u""

            url = reverse(reverse_path, args=(link_obj.id,))
            return mark_safe(u"<a href='%s'>%s</a>" % (url, link_text(link_obj)))

        link.allow_tags = True
        link.short_description = short_description or (reverse_name + ' link')
        setattr(cls, field_name, link)
        cls.readonly_fields = list(getattr(cls, 'readonly_fields', [])) + [field_name]
        return cls
    return add_link

# END ################################################################################################################




# TODO перенести это в формы может быть?
class OrderAdminForm(forms.ModelForm):
    class Meta:
        #model = Author
        #fields = ('name', 'title', 'birth_date')
        widgets = {
            'remarks': Textarea(attrs={'cols': 80, 'rows': 5}),
        }

    # макс. заказ === ЭТО РАБОТАЕТ === но только для help_text, для verbose не пашет почему-то
    def __init__(self, *args, **kwargs):
        """
        Выдает подсказку - последний зарегистрированный номер, и сразу производит автозаполнение номера.
        """
        super(OrderAdminForm, self).__init__(*args, **kwargs)
        last_number = Order.objects.all().aggregate(Max('order'))['order__max']

        # Если база пуста, last_number будет None, меняем на ноль
        if not last_number:
            last_number = 0

        self.fields['order'].help_text = 'Последний зарег. номер: {}'.format(last_number)
        self.fields['order'].initial = int(last_number) + 1


class OperationAdminForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = ['name', 'printsheet', 'contractor', 'price', 'remarks']

    def __init__(self, *args, **kwargs):
        """
        Суть этого метода в том, что в инлайне "Технологические операции" в поле "Печатный лист" выводятся только
        принадлежащие к текущему заказу печатные листы. Иначе Джанго пофиг на них - вываливает всю существующие printingsheet's
        """
        super(OperationAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['printsheet'].queryset = PrintSheet.objects.filter(order=self.instance.order_id)


class PrintSheetAdminForm(forms.ModelForm):
    class Meta:
        model = PrintSheet
        fields = ['name', 'printingpress', 'turnover', 'pressrun', 'plates', 'outputter', 'colors', 'quantity', 'paper']
        widgets = {
            'colors': TextInput(attrs={'size': 10})
        }


class DetalAdminInLine(admin.TabularInline):
    model = Detal
    extra = 0
    list_display = ('name', 'size', 'amount')


class OperationInLine(admin.TabularInline):
    model = Operation
    extra = 0
    verbose_name = 'Технологическая операция'
    verbose_name_plural = 'Технологические операции'

    form = OperationAdminForm


@add_link_field(target_model='printsheet', field='detal', field_name='link')
class PrintSheetInLine(admin.TabularInline):
    model = PrintSheet
    extra = 0

    fields = ['name', 'printingpress', 'turnover', 'pressrun', 'plates', 'outputter', 'colors', 'quantity', 'paper', 'link']

    save_on_top = True
    verbose_name = 'Печатный лист'
    verbose_name_plural = 'Печатные листы'
    show_change_link = True

    # inlines = [DetalAdminInLine]
    form = PrintSheetAdminForm


class OrderAdmin(admin.ModelAdmin):
    # поля, которые будут являться ссылками для перехода в редактирование "заказа"
    list_display_links = ['order', 'customer']
    # поля, видимые в таблице (не редакторе записи)
    list_display = ('order', 'customer', 'name', 'quantity', 'start_date', 'end_date', 'remarks', 'calc_field', 'is_production')
    # list_editable = ('order', 'customer', 'name')
    # фильтры - о дате и по заказчику
    list_filter = ['customer', 'start_date']

    # В 1.8 возникает ексепшн Non-relational field given in select_related: 'start_date'. Choices are: customer, status_ready_user
    #### SWASHER list_select_related = ['customer', 'start_date']

    # поле поиска. можно искать сразу по нескольким полям. foreignkey указывается как
    search_fields = ['name']
    # что-то типа крошек для поля даты (только для одного поля)
    date_hierarchy = 'start_date'
    # поля, которые исключаются из формы редактирования. Поля можно исключить как атрибутом exclude, так и атрибутом fields
    exclude = ['status_ready', 'status_ready_user']
    # сортировка по умолчанию
    ordering = ['order']
    # порядок и наличие полей в форме
    #fields = ('is_production', 'order', 'customer', 'price', 'name', 'quantity', 'start_date', 'end_date', 'remarks')
    fieldsets = (
        (None, {
            'fields': ('is_production', ('order', 'customer', 'price'), 'name', 'quantity', ('start_date', 'end_date'), 'remarks',),
        }),
    )

    inlines = [PrintSheetInLine, OperationInLine]
    save_as = True

    # В форме редактирование возле "плюсика" появляется "карандашик" (Django 1.8)
    show_change_link = True

    form = OrderAdminForm


class PrintSheetAdmin(admin.ModelAdmin):
    fields = ('name', ('printingpress', 'pressrun', 'quantity', 'colors'), 'turnover', ('plates', 'outputter'),
              'paper',
              ('paper_warehouse_unit', 'paper_warehouse_amount', 'paper_warehouse_format'),
              ('paper_printing_amount', 'paper_printing_format'))
    inlines = [DetalAdminInLine]


class ContractorAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'remarks')


admin.site.register(Order, OrderAdmin)
admin.site.register(Contractor, ContractorAdmin)
admin.site.register(OperationList)
admin.site.register(PrintSheet, PrintSheetAdmin)
