# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-20 11:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('technologichka', '0007_auto_20170620_1119'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('address', models.CharField(blank=True, max_length=250)),
                ('fio', models.CharField(blank=True, help_text='ФИО и должность контактного лица', max_length=150, verbose_name='ФИО')),
                ('phone', models.CharField(blank=True, help_text='Телефон контактного лица', max_length=50)),
                ('remarks', models.TextField(blank=True, verbose_name='Примечания')),
                ('allow_access', models.BooleanField(default=False)),
                ('unc', models.CharField(blank=True, max_length=150, null=True)),
            ],
            options={
                'verbose_name_plural': 'Заказчики',
                'verbose_name': 'Заказчик',
            },
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]