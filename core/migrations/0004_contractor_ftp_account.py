# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-29 16:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0015_auto_20170629_1609'),
        ('core', '0003_contractor'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractor',
            name='ftp_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='workflow.Ftp'),
        ),
    ]
