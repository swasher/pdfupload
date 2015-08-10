# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stanzforms', '0002_auto_20150807_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doska',
            name='doska',
            field=models.ImageField(help_text=b'\xd0\x98\xd0\xb7\xd0\xbe\xd0\xb1\xd1\x80\xd0\xb0\xd0\xb6\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xb4\xd0\xbe\xd1\x81\xd0\xba\xd0\xb8', upload_to=b'stanz/doska', null=True, verbose_name=b'\xd0\x94\xd0\xbe\xd1\x81\xd0\xba\xd0\xb0', blank=True),
        ),
        migrations.AlterField(
            model_name='doska',
            name='spusk',
            field=models.ImageField(help_text=b'\xd0\x98\xd0\xb7\xd0\xbe\xd0\xb1\xd1\x80\xd0\xb0\xd0\xb6\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xbf\xd0\xb5\xd1\x87\xd0\xb0\xd1\x82\xd0\xbd\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xbb\xd0\xb8\xd1\x81\xd1\x82\xd0\xb0', upload_to=b'stanz/spusk', null=True, verbose_name=b'\xd0\xa1\xd0\xbf\xd1\x83\xd1\x81\xd0\xba', blank=True),
        ),
        migrations.AlterField(
            model_name='knife',
            name='drawing',
            field=models.FileField(help_text=b'\xd0\xa4\xd0\xb0\xd0\xb9\xd0\xbb \xd1\x87\xd0\xb5\xd1\x80\xd1\x82\xd0\xb5\xd0\xb6\xd0\xb0 (PDF)', upload_to=b'stanz/drawing', null=True, verbose_name=b'\xd0\xa7\xd0\xb5\xd1\x80\xd1\x82\xd0\xb5\xd0\xb6, PDF', blank=True),
        ),
        migrations.AlterField(
            model_name='knife',
            name='knife',
            field=models.ImageField(help_text=b'\xd0\x98\xd0\xb7\xd0\xbe\xd0\xb1\xd1\x80\xd0\xb0\xd0\xb6\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xbd\xd0\xbe\xd0\xb6\xd0\xb0', upload_to=b'stanz/knife', null=True, verbose_name=b'\xd0\x9d\xd0\xbe\xd0\xb6, \xd0\xb8\xd0\xb7\xd0\xbe\xd0\xb1\xd1\x80.', blank=True),
        ),
    ]
