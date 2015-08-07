# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('technologichka', '0002_auto_20150807_1307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractor',
            name='produce',
            field=models.CharField(blank=True, max_length=3, null=True, verbose_name=b'\xd0\x9f\xd1\x80\xd0\xbe\xd0\xb8\xd0\xb7\xd0\xb2\xd0\xbe\xd0\xb4\xd1\x81\xd1\x82\xd0\xb2\xd0\xbe', choices=[(b'ctp', b'\xd0\xa4\xd0\xbe\xd1\x80\xd0\xbc\xd1\x8b'), (b'kli', b'\xd0\x9a\xd0\xbb\xd0\xb8\xd1\x88\xd0\xb5'), (b'sta', b'\xd0\xa8\xd1\x82\xd0\xb0\xd0\xbd\xd1\x86\xd1\x8b'), (b'all', b'\xd0\xa0\xd0\xb0\xd0\xb7\xd0\xbd\xd0\xbe\xd0\xb5')]),
        ),
    ]
