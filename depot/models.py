# coding: utf-8
from django.db import models
from core.models import Customer
from stanzforms.models import Knife

# class Product(models.Model):
#     """
#     This model describe a box or a label and his relation to Customer.
#     """
#     customer = models.ForeignKey(Customer)
#     remote_filename = models.CharField(max_length=256) # Название файла этикетки или коробки. Абсолютный путь - os.path.join(customer.unc, filename)
#     name = models.CharField(max_length=150)
#     last_change = models.DateField() # нужно ли указывать время изменения или достачто только даты?
#     approved = models.BooleanField(help_text='Заказчик утвердил макет')
#     approved_date = models.DateField(help_text='Дата утверждения') # Если макет изменился со времени последнего подтверждения, что галка Approved снимается
#     thumb = models.ImageField() # small image for grid, about 100x100 px
#     preview = models.ImageField() # big image about screen width
#     size = models.CharField(max_length=20) # Размеры изделия в мм, наверное удобнее всего хранить в Char... Не знаю, зачем может понадобится INTxINT
#     is_cutting = models.BooleanField() # Если изделие высекается, то можно связать с ним Нож
#     knife = models.ForeignKey(Knife, blank=True)

"""
Во-первых, что непонятно - это как логинится Кастомеру. Ибо любой прилогинившейся сразу видил все аплоады.

Второй момент, как я думаю сделать.
Форма Depot. Менеджер выбирает Кастомера из дроп-спикска и тут же вводит предполагаемый тираж.
Далее он напротив каждой позиции проставляет кол-во на листе и жмет Save. Эти данные сохраняются либо в
shelve, либо прямо в таблице Depot, и напротив каждой позиции появляется тираж. 

Далее менеджер нажимает кнопку `SAVE PDF` и сохраняет пдф с картинками, названиями изделий, кол-вом на листе и тиражом.
Ту же самую процедуру может проделать заказчик самостоятельно

Можно так-же предусмотреть кнопку APPROVED типа заказчик "подтвердил" макет. После скана, если макет изменился,
подтвердить нужно заново. 

MD5 или FILESIZE - как быстрее и надежнее отслеживать изменение макета? Проверка показала, что filesize меняется
при малейшем изменении макета, типа подвинуть объект на миллиметр. 

"""

