# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-20 11:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('technologichka', '0006_auto_20170617_1808'),
    ]

    database_operations = [
        # здесь указываем исходное имя модели ('Car') и конечное (newapp_Car'),
        # обычно в формате app_model. Внимание! Case sensetive!
        migrations.AlterModelTable('customer', 'core_customer')
    ]

    state_operations = [
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]