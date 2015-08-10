# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stanzforms.models


class Migration(migrations.Migration):

    dependencies = [
        ('stanzforms', '0003_auto_20150807_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doska',
            name='doska',
            field=models.ImageField(help_text=b'\xd0\x98\xd0\xb7\xd0\xbe\xd0\xb1\xd1\x80\xd0\xb0\xd0\xb6\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xb4\xd0\xbe\xd1\x81\xd0\xba\xd0\xb8', upload_to=stanzforms.models.get_doska_file_path, null=True, verbose_name=b'\xd0\x94\xd0\xbe\xd1\x81\xd0\xba\xd0\xb0', blank=True),
        ),
        migrations.AlterField(
            model_name='doska',
            name='spusk',
            field=models.ImageField(help_text=b'\xd0\x98\xd0\xb7\xd0\xbe\xd0\xb1\xd1\x80\xd0\xb0\xd0\xb6\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xbf\xd0\xb5\xd1\x87\xd0\xb0\xd1\x82\xd0\xbd\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xbb\xd0\xb8\xd1\x81\xd1\x82\xd0\xb0', upload_to=stanzforms.models.get_spusk_file_path, null=True, verbose_name=b'\xd0\xa1\xd0\xbf\xd1\x83\xd1\x81\xd0\xba', blank=True),
        ),
    ]
