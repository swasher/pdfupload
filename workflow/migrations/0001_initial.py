# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ftp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('ip', models.GenericIPAddressField()),
                ('port', models.IntegerField()),
                ('login', models.CharField(max_length=30)),
                ('passw', models.CharField(max_length=30)),
                ('todir', models.CharField(max_length=150, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Grid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField()),
                ('pdfname', models.CharField(max_length=100)),
                ('total_pages', models.IntegerField()),
                ('total_plates', models.IntegerField()),
                ('contractor_error', models.CharField(max_length=300)),
                ('preview_error', models.CharField(max_length=300)),
                ('colors', models.CharField(max_length=500, blank=True)),
                ('inks', models.CharField(max_length=500, blank=True)),
                ('bg', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Outputter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('ftp_account', models.ForeignKey(to='workflow.Ftp')),
            ],
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=13)),
            ],
        ),
        migrations.CreateModel(
            name='PrintingPress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('plate_w', models.IntegerField()),
                ('plate_h', models.IntegerField()),
                ('klapan', models.IntegerField()),
                ('cost', models.IntegerField(help_text=b'Cost of one plate', null=True, blank=True)),
                ('uploadtarget', models.ForeignKey(blank=True, to='workflow.Ftp', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='outputter',
            name='sms_receiver',
            field=models.ForeignKey(blank=True, to='workflow.Phone', null=True),
        ),
        migrations.AddField(
            model_name='grid',
            name='contractor',
            field=models.ForeignKey(to='workflow.Outputter', null=True),
        ),
        migrations.AddField(
            model_name='grid',
            name='machine',
            field=models.ForeignKey(to='workflow.PrintingPress', null=True),
        ),
    ]
