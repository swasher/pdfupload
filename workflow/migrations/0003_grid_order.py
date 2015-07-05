# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0002_auto_20150704_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='grid',
            name='order',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]
