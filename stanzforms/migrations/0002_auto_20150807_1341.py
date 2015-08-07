# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stanzforms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doska',
            name='customer',
            field=models.TextField(help_text=b'\xd0\x9a\xd1\x82\xd0\xbe \xd0\xbf\xd0\xbb\xd0\xb0\xd1\x82\xd0\xb8\xd0\xbb, \xd0\xb8\xd0\xbb\xd0\xb8 \xd1\x82\xd0\xb8\xd0\xbf\xd0\xb8\xd1\x87\xd0\xbd\xd1\x8b\xd0\xb5 \xd0\xb7\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7\xd1\x87\xd0\xb8\xd0\xba\xd0\xb8.', verbose_name=b'\xd0\x97\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7\xd1\x87\xd0\xb8\xd0\xba', blank=True),
        ),
        migrations.AlterField(
            model_name='knife',
            name='gabarit_a',
            field=models.PositiveSmallIntegerField(help_text=b'\xd0\x93\xd0\xb0\xd0\xb1\xd0\xb0\xd1\x80\xd0\xb8\xd1\x82 \xd1\x88\xd0\xb8\xd1\x80\xd0\xb8\xd0\xbd\xd0\xb0', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='knife',
            name='gabarit_b',
            field=models.PositiveSmallIntegerField(help_text=b'\xd0\x93\xd0\xb0\xd0\xb1\xd0\xb0\xd1\x80\xd0\xb8\xd1\x82 \xd0\xb2\xd1\x8b\xd1\x81\xd0\xbe\xd1\x82\xd0\xb0', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='knife',
            name='gabarit_c',
            field=models.PositiveSmallIntegerField(help_text=b'\xd0\x93\xd0\xb0\xd0\xb1\xd0\xb0\xd1\x80\xd0\xb8\xd1\x82 \xd0\xb3\xd0\xbb\xd1\x83\xd0\xb1\xd0\xb8\xd0\xbd\xd0\xb0', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='knife',
            name='razvertka_h',
            field=models.PositiveSmallIntegerField(help_text=b'\xd0\xa0\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb5\xd1\x80\xd1\x82\xd0\xba\xd0\xb0, \xd0\xb2\xd1\x8b\xd1\x81\xd0\xbe\xd1\x82\xd0\xb0', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='knife',
            name='razvertka_w',
            field=models.PositiveSmallIntegerField(help_text=b'\xd0\xa0\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb5\xd1\x80\xd1\x82\xd0\xba\xd0\xb0, \xd1\x88\xd0\xb8\xd1\x80\xd0\xb8\xd0\xbd\xd0\xb0', null=True, blank=True),
        ),
    ]
