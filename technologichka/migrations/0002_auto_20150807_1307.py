# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('technologichka', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractor',
            name='name',
            field=models.CharField(unique=True, max_length=100, verbose_name=b'\xd0\x9e\xd1\x80\xd0\xb3\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd1\x8f'),
        ),
    ]
