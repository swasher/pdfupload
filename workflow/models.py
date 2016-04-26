# coding: utf-8

from django.db import models
from django.contrib.auth.models import User

# deprecated; use User class instead
#
# class Phone(models.Model):
#     name = models.CharField(max_length=50)
#     phone = models.CharField(max_length=13)
#
#     def __unicode__(self):
#         return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=13, blank=True)
    telegram_id = models.IntegerField(blank=True, null=True)
    telegram_notify = models.BooleanField(default=False)
    sms_notify = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __unicode__(self):
        return ' '.join(self.user.username)


class Ftp(models.Model):
    name = models.CharField(max_length=50)
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    login = models.CharField(max_length=30)
    passw = models.CharField(max_length=30)     # пароль хранится в открытом виде
    todir = models.CharField(max_length=150, blank=True, null=True)    # папка для заливки
    passive_mode = models.BooleanField(blank=True, default=True)

    class Meta:
        verbose_name = 'ФТП'
        verbose_name_plural = 'ФТП'

    def __unicode__(self):
        return self.name


class PrintingPress(models.Model):
    name = models.CharField(max_length=150, verbose_name='Наименование', help_text='Название печатного пресса')
    uploadtarget = models.ForeignKey('Ftp', blank=True, null=True)
    plate_w = models.IntegerField(verbose_name='Ширина пластины, мм')
    plate_h = models.IntegerField(verbose_name='Высота пластины, мм')
    klapan = models.IntegerField(verbose_name='Клапан', help_text='Расстояние от нижнего края пластины до края бумаги')
    cost = models.IntegerField(blank=True, null=True, help_text='Cost of one plate')

    class Meta:
        verbose_name = 'Машина'
        verbose_name_plural = 'Машины'

    def __unicode__(self):
        return self.name


class Ctpbureau(models.Model):
    name = models.CharField(max_length=50)
    ftp_account = models.ForeignKey('Ftp')
    # deprecated;
    # use `sms_notify` filed in employer model instead
    # sms_receiver = models.ForeignKey('Phone', blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'CTP бюро'
        verbose_name_plural = 'CTP бюро'


class Grid(models.Model):
    order = models.PositiveSmallIntegerField()
    datetime = models.DateTimeField()
    pdfname = models.CharField(max_length=100)
    machine = models.ForeignKey(PrintingPress, null=True)
    total_pages = models.IntegerField()
    total_plates = models.IntegerField()
    contractor = models.ForeignKey(Ctpbureau, null=True)   # подрядчик
    contractor_error = models.CharField(max_length=300)    # код ошибки заливки файла на вывод
    preview_error = models.CharField(max_length=300)       # код ошибки заливки превьюхи на кинап
    colors = models.CharField(max_length=500, blank=True)  # мультилайн текст - инфа о колористике
    inks = models.CharField(max_length=500, blank=True)    # мультилайн текст - инфа о заполнении краской
    bg = models.CharField(max_length=50)                   # цвет строки
    proof = models.ImageField(blank=True, null=True)
    thumb = models.ImageField(blank=True, null=True)

    def __unicode__(self):
        return self.pdfname

    class Meta:
        verbose_name = 'Заливка'
        verbose_name_plural = 'Заливки'