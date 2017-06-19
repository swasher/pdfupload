from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=13, blank=True)
    telegram_id = models.IntegerField(blank=True, null=True)
    telegram_notify = models.BooleanField(default=False)
    sms_notify = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return ' '.join(self.user.username)


# class Customer(models.Model):
#     name = models.CharField(max_length=150)
#     address = models.CharField(max_length=250, blank=True)
#     fio = models.CharField(max_length=150, blank=True, verbose_name='ФИО', help_text='ФИО и должность контактного лица')
#     phone = models.CharField(max_length=50, blank=True, help_text='Телефон контактного лица')
#     remarks = models.TextField(blank=True, verbose_name='Примечания')
#     allow_access = models.BooleanField(blank=False, default=False) # customer allow access to their Products
#     unc = models.CharField(max_length=150, blank=True, null=True) # path to source products \\Server\SharedFolder\Customer\Files
#
#     def __str__(self):
#         if self.fio:
#             return u'{} ({} {})'.format(self.name, self.fio, self.phone)
#         else:
#             return u'{}'.format(self.name)
#
#     class Meta:
#         verbose_name = 'Заказчик'
#         verbose_name_plural = 'Заказчики'
#
#
# class Contractor(models.Model):
#     PRODUCE = (
#         ('ctp', 'Формы'),
#         ('kli', 'Клише'),
#         ('sta', 'Штанцы'),
#         ('all', 'Разное'),
#     )
#     name = models.CharField(max_length=100, verbose_name='Организация', unique=True)
#     produce = models.CharField(blank=True, null=True, max_length=3, choices=PRODUCE, verbose_name='Производство')
#     phone = models.CharField(max_length=50, blank=True, verbose_name='Телефон')
#     remarks = models.TextField(blank=True, verbose_name='Примечания')
#
#     def __str__(self):
#         return u'{}'.format(self.name)
#
#     class Meta:
#         verbose_name = 'Подрядчик'
#         verbose_name_plural = 'Подрядчики'