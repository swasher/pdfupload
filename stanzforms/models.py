# coding: utf-8

import uuid
import os
from django.db import models
from technologichka.models import Contractor


def get_spusk_file_path(instance, filename):
    f, ext = os.path.splitext(filename)
    filename = "{}_{}.{}".format(f, uuid.uuid4(), ext)
    return os.path.join(instance.directory_spusk, filename)

def get_doska_file_path(instance, filename):
    f, ext = os.path.splitext(filename)
    filename = "{}_{}.{}".format(f, uuid.uuid4(), ext)
    return os.path.join(instance.directory_doska, filename)


class Doska(models.Model):
    articul = models.CharField(max_length=20, unique=True, verbose_name='Артикул')
    make_date = models.DateField(blank=True, null=True, verbose_name='Дата изг.')
    name = models.CharField(max_length=100, verbose_name='Наименование')
    contractor = models.ForeignKey(Contractor, verbose_name='Изготовитель')
    price = models.DecimalField(blank=True, max_digits=12, decimal_places=2, null=True, verbose_name='Стоимость, уе.')
    description = models.TextField(blank=True, verbose_name='Описание')
    maintenance = models.TextField(blank=True, verbose_name='Обслуживание', help_text='Тут должны быть описаны любые работы, проведенные с доской.')
    customer = models.TextField(blank=True, verbose_name='Заказчик', help_text='Кто платил, или типичные заказчики.')
    #spusk = models.ImageField(blank=True, null=True, upload_to='stanz/spusk', verbose_name='Спуск', help_text='Изображение печатного листа')
    spusk = models.ImageField(blank=True, null=True, upload_to=get_spusk_file_path, verbose_name='Спуск', help_text='Изображение печатного листа')
    directory_spusk = 'stanz/spusk'
    #doska = models.ImageField(blank=True, null=True, upload_to='stanz/doska', verbose_name='Доска', help_text='Изображение доски')
    doska = models.ImageField(blank=True, null=True, upload_to=get_doska_file_path, verbose_name='Доска', help_text='Изображение доски')
    directory_doska = 'stanz/doska'

    class Meta:
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'

    def __unicode__(self):
        return u'[{}] {}'.format(self.articul, self.name)


class Knife(models.Model):
    doska = models.ForeignKey(Doska)
    name = models.CharField(max_length=50)
    razvertka_w = models.PositiveSmallIntegerField(blank=True, null=True, help_text='Развертка, ширина')
    razvertka_h = models.PositiveSmallIntegerField(blank=True, null=True, help_text='Развертка, высота')
    gabarit_a = models.PositiveSmallIntegerField(blank=True, null=True, help_text='Габарит ширина')
    gabarit_b = models.PositiveSmallIntegerField(blank=True, null=True, help_text='Габарит высота')
    gabarit_c = models.PositiveSmallIntegerField(blank=True, null=True, help_text='Габарит глубина')
    knife = models.ImageField(blank=True, null=True, upload_to='stanz/knife', verbose_name='Нож, изобр.', help_text='Изображение ножа')
    drawing = models.FileField(blank=True, null=True, upload_to='stanz/drawing', verbose_name='Чертеж, PDF', help_text='Файл чертежа (PDF)')

    class Meta:
        verbose_name = 'Штанц'
        verbose_name_plural = 'Штанцы'

    def __unicode__(self):
        return u'{}'.format(self.name)
