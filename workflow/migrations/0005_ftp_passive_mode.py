# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-21 11:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0004_auto_20150807_1146'),
    ]

    operations = [
        migrations.AddField(
            model_name='ftp',
            name='passive_mode',
            field=models.BooleanField(default=True),
        ),
    ]