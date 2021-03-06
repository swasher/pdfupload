# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0003_grid_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='printingpress',
            options={'verbose_name': '\u041c\u0430\u0448\u0438\u043d\u0430', 'verbose_name_plural': '\u041c\u0430\u0448\u0438\u043d\u044b'},
        ),
        migrations.AlterField(
            model_name='printingpress',
            name='klapan',
            field=models.IntegerField(help_text=b'\xd0\xa0\xd0\xb0\xd1\x81\xd1\x81\xd1\x82\xd0\xbe\xd1\x8f\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xbe\xd1\x82 \xd0\xbd\xd0\xb8\xd0\xb6\xd0\xbd\xd0\xb5\xd0\xb3\xd0\xbe \xd0\xba\xd1\x80\xd0\xb0\xd1\x8f \xd0\xbf\xd0\xbb\xd0\xb0\xd1\x81\xd1\x82\xd0\xb8\xd0\xbd\xd1\x8b \xd0\xb4\xd0\xbe \xd0\xba\xd1\x80\xd0\xb0\xd1\x8f \xd0\xb1\xd1\x83\xd0\xbc\xd0\xb0\xd0\xb3\xd0\xb8', verbose_name=b'\xd0\x9a\xd0\xbb\xd0\xb0\xd0\xbf\xd0\xb0\xd0\xbd'),
        ),
        migrations.AlterField(
            model_name='printingpress',
            name='name',
            field=models.CharField(help_text=b'\xd0\x9d\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xbf\xd0\xb5\xd1\x87\xd0\xb0\xd1\x82\xd0\xbd\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xbf\xd1\x80\xd0\xb5\xd1\x81\xd1\x81\xd0\xb0', max_length=150, verbose_name=b'\xd0\x9d\xd0\xb0\xd0\xb8\xd0\xbc\xd0\xb5\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5'),
        ),
        migrations.AlterField(
            model_name='printingpress',
            name='plate_h',
            field=models.IntegerField(verbose_name=b'\xd0\x92\xd1\x8b\xd1\x81\xd0\xbe\xd1\x82\xd0\xb0 \xd0\xbf\xd0\xbb\xd0\xb0\xd1\x81\xd1\x82\xd0\xb8\xd0\xbd\xd1\x8b, \xd0\xbc\xd0\xbc'),
        ),
        migrations.AlterField(
            model_name='printingpress',
            name='plate_w',
            field=models.IntegerField(verbose_name=b'\xd0\xa8\xd0\xb8\xd1\x80\xd0\xb8\xd0\xbd\xd0\xb0 \xd0\xbf\xd0\xbb\xd0\xb0\xd1\x81\xd1\x82\xd0\xb8\xd0\xbd\xd1\x8b, \xd0\xbc\xd0\xbc'),
        ),
    ]
