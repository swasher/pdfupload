# coding: utf-8

from django.db import models
# from django.db.models import Max
from django.contrib.auth.models import User
from workflow.models import PrintingPress



class Customer(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=250, blank=True)
    fio = models.CharField(max_length=150, blank=True, verbose_name='ФИО', help_text='ФИО и должность контактного лица')
    phone = models.CharField(max_length=50, blank=True, help_text='Телефон контактного лица')
    remarks = models.TextField(blank=True, verbose_name='Примечания')

    def __unicode__(self):
        if self.fio:
            return u'{} ({} {})'.format(self.name, self.fio, self.phone)
        else:
            return u'{}'.format(self.name)

    class Meta:
        verbose_name = 'Заказчик'
        verbose_name_plural = 'Заказчики'


class Contractor(models.Model):
    PRODUCE = (
        ('ctp', 'Формы'),
        ('kli', 'Клише'),
        ('sta', 'Штанцы'),
        ('all', 'Разное'),
    )
    name = models.CharField(max_length=100, verbose_name='Организация', unique=True)
    produce = models.CharField(blank=True, null=True, max_length=3, choices=PRODUCE, verbose_name='Производство')
    phone = models.CharField(max_length=50, blank=True, verbose_name='Телефон')
    remarks = models.TextField(blank=True, verbose_name='Примечания')

    def __unicode__(self):
        return u'{}'.format(self.name)

    class Meta:
        verbose_name = 'Подрядчик'
        verbose_name_plural = 'Подрядчики'


class Order(models.Model):
    is_production = models.BooleanField(default=True, help_text='Заказ находится в производстве')
    order = models.IntegerField(unique=True, verbose_name='Номер заказа', help_text='Max order')
    customer = models.ForeignKey(Customer, verbose_name='Заказчик')
    name = models.CharField(max_length=100, verbose_name='Наименование заказа')
    quantity = models.IntegerField(verbose_name='Тираж', help_text='Общее кол-во заказанных изделий')
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Стоимость, грн.')
    start_date = models.DateField(verbose_name='Дата оформления', help_text='Дата оформления заказа')
    end_date = models.DateField(blank=True, null=True, verbose_name='Сдать до', help_text='Предполагаемая дата сдачи заказа')
    remarks = models.TextField(blank=True, verbose_name='Описание заказа')
    status_ready = models.BooleanField(default=False, help_text='True когда заказ готов к выдаче заказчику.')
    status_ready_user = models.ForeignKey(User, blank=True, null=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def calc_field(self):
        try:
            unit_price = '{:.2f}'.format(self.price / self.quantity)
        except TypeError:
            unit_price = '0'
        return unit_price
    calc_field.short_description = 'unit_price'

    def __unicode__(self):
        return u'Заказ {} от {} [{}]'.format(self.name, self.customer.name, self.quantity)


class PrintSheet(models.Model):
    TURNOVER = (
        ('SingleSide', 'Без оборота'),
        ('WorkAndTurn', 'Свой оборот'),
        ('WorkAndThumble', 'Хвост-на-голову'),
        ('Perfecting', 'Чужой оборот'),
    )
    PAPER_UNIT = (
        ('leaf', 'Листы'),
        ('kg', 'Кг'),
    )
    name = models.CharField(max_length=150, null=False, verbose_name='Название листа')
    order = models.ForeignKey(Order)
    printingpress = models.ForeignKey(PrintingPress, blank=True, null=True, verbose_name='Печатная машина')
    pressrun = models.IntegerField(blank=True, null=True, verbose_name='Тираж', help_text='Технологический тираж одного листа')
    plates = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Пластины', help_text='Кол-во пластин на один лист')
    outputter = models.ForeignKey(Contractor, blank=True, null=True, verbose_name='Вывод пластин')
    colors = models.CharField(max_length=10, blank=True, null=False, verbose_name='Цветность')
    quantity = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Кол-во', help_text='Кол-во одинаковых печатных листов')
    turnover = models.CharField(blank=True, null=True, max_length=20, choices=TURNOVER, verbose_name='Оборот')
    paper = models.CharField(blank=True, null=True, max_length=300, verbose_name='Граммаж и тип бумаги')
    paper_warehouse_unit = models.CharField(blank=True, null=True, max_length=4, choices=PAPER_UNIT, verbose_name='Ед.:', help_text='Единица бумаги (СКЛАД)')
    paper_warehouse_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Кол-во', help_text='Количество единиц, выданных со склада')
    paper_warehouse_format = models.CharField(max_length=20, blank=True, verbose_name='Ф-т размотки', help_text='Формат размотки ИЛИ формат листовой бумаги')
    paper_printing_amount = models.CharField(max_length=20, blank=True, verbose_name='Печать, кол-во', help_text='Общее кол-во выданных листов')
    paper_printing_format = models.CharField(max_length=20, blank=True, verbose_name='Печать, ф-т', help_text='Формат бумаги в печать')

    class Meta:
        verbose_name = 'Печатный лист'
        verbose_name_plural = 'Печатные листы'

    def __unicode__(self):
        return u'{} [{} {}]'.format(self.name, self.printingpress, self.colors)


class OperationList(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return u'{}'.format(self.name)

    class Meta:
        verbose_name = 'Словарь технологических операций'
        verbose_name_plural = 'Словарь технологических операций'


class Operation(models.Model):
    order = models.ForeignKey(Order)
    name = models.ForeignKey(OperationList, verbose_name='Операция', help_text='')
    printsheet = models.ForeignKey(PrintSheet, blank=True, null=True, verbose_name='Печатный лист', help_text='Если оперция не относится к конкретному печатному листу, оставьте это поле пустым')
    contractor = models.ForeignKey(Contractor, blank=True, null=True, verbose_name='Подрядчик')
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Стоимость, грн.')
    remarks = models.CharField(max_length=500, blank=True)

    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'

    def __unicode__(self):
        return u'{}'.format(self.name)


class Detal(models.Model):
    printsheet = models.ForeignKey(PrintSheet)
    name = models.CharField(max_length=50, verbose_name='Название детали')
    size = models.CharField(max_length=20, blank=True, null=False, verbose_name='Размер, мм')
    amount = models.PositiveIntegerField(blank=True, null=True, verbose_name='Тираж')

    class Meta:
        verbose_name = 'Деталь'
        verbose_name_plural = 'Детали'

    def __unicode__(self):
        if self.size:
            return u'{} [{}]'.format(self.name, self.size)
        else:
            return u'{}'.format(self.name)


