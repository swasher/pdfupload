# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stanzforms.models


class Migration(migrations.Migration):

    dependencies = [
        ('stanzforms', '0004_auto_20150807_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knife',
            name='drawing',
            field=models.FileField(help_text=b'\xd0\xa4\xd0\xb0\xd0\xb9\xd0\xbb \xd1\x87\xd0\xb5\xd1\x80\xd1\x82\xd0\xb5\xd0\xb6\xd0\xb0 (PDF)', upload_to=stanzforms.models.get_drawing_file_path, null=True, verbose_name=b'\xd0\xa7\xd0\xb5\xd1\x80\xd1\x82\xd0\xb5\xd0\xb6, PDF', blank=True),
        ),
        migrations.AlterField(
            model_name='knife',
            name='knife',
            field=models.ImageField(help_text=b'\xd0\x98\xd0\xb7\xd0\xbe\xd0\xb1\xd1\x80\xd0\xb0\xd0\xb6\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xbd\xd0\xbe\xd0\xb6\xd0\xb0', upload_to=stanzforms.models.get_knife_file_path, null=True, verbose_name=b'\xd0\x9d\xd0\xbe\xd0\xb6, \xd0\xb8\xd0\xb7\xd0\xbe\xd0\xb1\xd1\x80.', blank=True),
        ),
    ]
