# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0004_auto_20150807_1146'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contractor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'\xd0\x9e\xd1\x80\xd0\xb3\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd1\x8f')),
                ('produce', models.CharField(blank=True, max_length=3, null=True, verbose_name=b'\xd0\x9f\xd1\x80\xd0\xbe\xd0\xb8\xd0\xb7\xd0\xb2\xd0\xbe\xd0\xb4\xd1\x81\xd1\x82\xd0\xb2\xd0\xbe', choices=[(b'ctp', b'\xd0\xa4\xd0\xbe\xd1\x80\xd0\xbc\xd1\x8b'), (b'kli', b'\xd0\x9a\xd0\xbb\xd0\xb8\xd1\x88\xd0\xb5'), (b'sta', b'\xd0\xa8\xd1\x82\xd0\xb0\xd0\xbd\xd1\x86\xd1\x8b')])),
                ('phone', models.CharField(max_length=50, verbose_name=b'\xd0\xa2\xd0\xb5\xd0\xbb\xd0\xb5\xd1\x84\xd0\xbe\xd0\xbd', blank=True)),
                ('remarks', models.TextField(verbose_name=b'\xd0\x9f\xd1\x80\xd0\xb8\xd0\xbc\xd0\xb5\xd1\x87\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x8f', blank=True)),
            ],
            options={
                'verbose_name': '\u041f\u043e\u0434\u0440\u044f\u0434\u0447\u0438\u043a',
                'verbose_name_plural': '\u041f\u043e\u0434\u0440\u044f\u0434\u0447\u0438\u043a\u0438',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('address', models.CharField(max_length=250, blank=True)),
                ('fio', models.CharField(help_text=b'\xd0\xa4\xd0\x98\xd0\x9e \xd0\xb8 \xd0\xb4\xd0\xbe\xd0\xbb\xd0\xb6\xd0\xbd\xd0\xbe\xd1\x81\xd1\x82\xd1\x8c \xd0\xba\xd0\xbe\xd0\xbd\xd1\x82\xd0\xb0\xd0\xba\xd1\x82\xd0\xbd\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xbb\xd0\xb8\xd1\x86\xd0\xb0', max_length=150, verbose_name=b'\xd0\xa4\xd0\x98\xd0\x9e', blank=True)),
                ('phone', models.CharField(help_text=b'\xd0\xa2\xd0\xb5\xd0\xbb\xd0\xb5\xd1\x84\xd0\xbe\xd0\xbd \xd0\xba\xd0\xbe\xd0\xbd\xd1\x82\xd0\xb0\xd0\xba\xd1\x82\xd0\xbd\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xbb\xd0\xb8\xd1\x86\xd0\xb0', max_length=50, blank=True)),
                ('remarks', models.TextField(verbose_name=b'\xd0\x9f\xd1\x80\xd0\xb8\xd0\xbc\xd0\xb5\xd1\x87\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x8f', blank=True)),
            ],
            options={
                'verbose_name': '\u0417\u0430\u043a\u0430\u0437\u0447\u0438\u043a',
                'verbose_name_plural': '\u0417\u0430\u043a\u0430\u0437\u0447\u0438\u043a\u0438',
            },
        ),
        migrations.CreateModel(
            name='Detal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'\xd0\x9d\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xb4\xd0\xb5\xd1\x82\xd0\xb0\xd0\xbb\xd0\xb8')),
                ('size', models.CharField(max_length=20, verbose_name=b'\xd0\xa0\xd0\xb0\xd0\xb7\xd0\xbc\xd0\xb5\xd1\x80, \xd0\xbc\xd0\xbc', blank=True)),
                ('amount', models.PositiveIntegerField(null=True, verbose_name=b'\xd0\xa2\xd0\xb8\xd1\x80\xd0\xb0\xd0\xb6', blank=True)),
            ],
            options={
                'verbose_name': '\u0414\u0435\u0442\u0430\u043b\u044c',
                'verbose_name_plural': '\u0414\u0435\u0442\u0430\u043b\u0438',
            },
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(null=True, verbose_name=b'\xd0\xa1\xd1\x82\xd0\xbe\xd0\xb8\xd0\xbc\xd0\xbe\xd1\x81\xd1\x82\xd1\x8c, \xd0\xb3\xd1\x80\xd0\xbd.', max_digits=12, decimal_places=2, blank=True)),
                ('remarks', models.CharField(max_length=500, blank=True)),
                ('contractor', models.ForeignKey(verbose_name=b'\xd0\x9f\xd0\xbe\xd0\xb4\xd1\x80\xd1\x8f\xd0\xb4\xd1\x87\xd0\xb8\xd0\xba', blank=True, to='technologichka.Contractor', null=True)),
            ],
            options={
                'verbose_name': '\u041e\u043f\u0435\u0440\u0430\u0446\u0438\u044f',
                'verbose_name_plural': '\u041e\u043f\u0435\u0440\u0430\u0446\u0438\u0438',
            },
        ),
        migrations.CreateModel(
            name='OperationList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': '\u0421\u043b\u043e\u0432\u0430\u0440\u044c \u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0447\u0435\u0441\u043a\u0438\u0445 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0439',
                'verbose_name_plural': '\u0421\u043b\u043e\u0432\u0430\u0440\u044c \u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0447\u0435\u0441\u043a\u0438\u0445 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0439',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_production', models.BooleanField(default=True, help_text=b'\xd0\x97\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7 \xd0\xbd\xd0\xb0\xd1\x85\xd0\xbe\xd0\xb4\xd0\xb8\xd1\x82\xd1\x81\xd1\x8f \xd0\xb2 \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb8\xd0\xb7\xd0\xb2\xd0\xbe\xd0\xb4\xd1\x81\xd1\x82\xd0\xb2\xd0\xb5')),
                ('order', models.IntegerField(help_text=b'Max order', unique=True, verbose_name=b'\xd0\x9d\xd0\xbe\xd0\xbc\xd0\xb5\xd1\x80 \xd0\xb7\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7\xd0\xb0')),
                ('name', models.CharField(max_length=100, verbose_name=b'\xd0\x9d\xd0\xb0\xd0\xb8\xd0\xbc\xd0\xb5\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xb7\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7\xd0\xb0')),
                ('quantity', models.IntegerField(help_text=b'\xd0\x9e\xd0\xb1\xd1\x89\xd0\xb5\xd0\xb5 \xd0\xba\xd0\xbe\xd0\xbb-\xd0\xb2\xd0\xbe \xd0\xb7\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7\xd0\xb0\xd0\xbd\xd0\xbd\xd1\x8b\xd1\x85 \xd0\xb8\xd0\xb7\xd0\xb4\xd0\xb5\xd0\xbb\xd0\xb8\xd0\xb9', verbose_name=b'\xd0\xa2\xd0\xb8\xd1\x80\xd0\xb0\xd0\xb6')),
                ('price', models.DecimalField(null=True, verbose_name=b'\xd0\xa1\xd1\x82\xd0\xbe\xd0\xb8\xd0\xbc\xd0\xbe\xd1\x81\xd1\x82\xd1\x8c, \xd0\xb3\xd1\x80\xd0\xbd.', max_digits=12, decimal_places=2, blank=True)),
                ('start_date', models.DateField(help_text=b'\xd0\x94\xd0\xb0\xd1\x82\xd0\xb0 \xd0\xbe\xd1\x84\xd0\xbe\xd1\x80\xd0\xbc\xd0\xbb\xd0\xb5\xd0\xbd\xd0\xb8\xd1\x8f \xd0\xb7\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7\xd0\xb0', verbose_name=b'\xd0\x94\xd0\xb0\xd1\x82\xd0\xb0 \xd0\xbe\xd1\x84\xd0\xbe\xd1\x80\xd0\xbc\xd0\xbb\xd0\xb5\xd0\xbd\xd0\xb8\xd1\x8f')),
                ('end_date', models.DateField(help_text=b'\xd0\x9f\xd1\x80\xd0\xb5\xd0\xb4\xd0\xbf\xd0\xbe\xd0\xbb\xd0\xb0\xd0\xb3\xd0\xb0\xd0\xb5\xd0\xbc\xd0\xb0\xd1\x8f \xd0\xb4\xd0\xb0\xd1\x82\xd0\xb0 \xd1\x81\xd0\xb4\xd0\xb0\xd1\x87\xd0\xb8 \xd0\xb7\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7\xd0\xb0', null=True, verbose_name=b'\xd0\xa1\xd0\xb4\xd0\xb0\xd1\x82\xd1\x8c \xd0\xb4\xd0\xbe', blank=True)),
                ('remarks', models.TextField(verbose_name=b'\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xb7\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7\xd0\xb0', blank=True)),
                ('status_ready', models.BooleanField(default=False, help_text=b'True \xd0\xba\xd0\xbe\xd0\xb3\xd0\xb4\xd0\xb0 \xd0\xb7\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7 \xd0\xb3\xd0\xbe\xd1\x82\xd0\xbe\xd0\xb2 \xd0\xba \xd0\xb2\xd1\x8b\xd0\xb4\xd0\xb0\xd1\x87\xd0\xb5 \xd0\xb7\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7\xd1\x87\xd0\xb8\xd0\xba\xd1\x83.')),
                ('customer', models.ForeignKey(verbose_name=b'\xd0\x97\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7\xd1\x87\xd0\xb8\xd0\xba', to='technologichka.Customer')),
                ('status_ready_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': '\u0417\u0430\u043a\u0430\u0437',
                'verbose_name_plural': '\u0417\u0430\u043a\u0430\u0437\u044b',
            },
        ),
        migrations.CreateModel(
            name='PrintSheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name=b'\xd0\x9d\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xbb\xd0\xb8\xd1\x81\xd1\x82\xd0\xb0')),
                ('pressrun', models.IntegerField(help_text=b'\xd0\xa2\xd0\xb5\xd1\x85\xd0\xbd\xd0\xbe\xd0\xbb\xd0\xbe\xd0\xb3\xd0\xb8\xd1\x87\xd0\xb5\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9 \xd1\x82\xd0\xb8\xd1\x80\xd0\xb0\xd0\xb6 \xd0\xbe\xd0\xb4\xd0\xbd\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xbb\xd0\xb8\xd1\x81\xd1\x82\xd0\xb0', null=True, verbose_name=b'\xd0\xa2\xd0\xb8\xd1\x80\xd0\xb0\xd0\xb6', blank=True)),
                ('plates', models.PositiveSmallIntegerField(help_text=b'\xd0\x9a\xd0\xbe\xd0\xbb-\xd0\xb2\xd0\xbe \xd0\xbf\xd0\xbb\xd0\xb0\xd1\x81\xd1\x82\xd0\xb8\xd0\xbd \xd0\xbd\xd0\xb0 \xd0\xbe\xd0\xb4\xd0\xb8\xd0\xbd \xd0\xbb\xd0\xb8\xd1\x81\xd1\x82', null=True, verbose_name=b'\xd0\x9f\xd0\xbb\xd0\xb0\xd1\x81\xd1\x82\xd0\xb8\xd0\xbd\xd1\x8b', blank=True)),
                ('colors', models.CharField(max_length=10, verbose_name=b'\xd0\xa6\xd0\xb2\xd0\xb5\xd1\x82\xd0\xbd\xd0\xbe\xd1\x81\xd1\x82\xd1\x8c', blank=True)),
                ('quantity', models.PositiveSmallIntegerField(help_text=b'\xd0\x9a\xd0\xbe\xd0\xbb-\xd0\xb2\xd0\xbe \xd0\xbe\xd0\xb4\xd0\xb8\xd0\xbd\xd0\xb0\xd0\xba\xd0\xbe\xd0\xb2\xd1\x8b\xd1\x85 \xd0\xbf\xd0\xb5\xd1\x87\xd0\xb0\xd1\x82\xd0\xbd\xd1\x8b\xd1\x85 \xd0\xbb\xd0\xb8\xd1\x81\xd1\x82\xd0\xbe\xd0\xb2', null=True, verbose_name=b'\xd0\x9a\xd0\xbe\xd0\xbb-\xd0\xb2\xd0\xbe', blank=True)),
                ('turnover', models.CharField(blank=True, max_length=20, null=True, verbose_name=b'\xd0\x9e\xd0\xb1\xd0\xbe\xd1\x80\xd0\xbe\xd1\x82', choices=[(b'SingleSide', b'\xd0\x91\xd0\xb5\xd0\xb7 \xd0\xbe\xd0\xb1\xd0\xbe\xd1\x80\xd0\xbe\xd1\x82\xd0\xb0'), (b'WorkAndTurn', b'\xd0\xa1\xd0\xb2\xd0\xbe\xd0\xb9 \xd0\xbe\xd0\xb1\xd0\xbe\xd1\x80\xd0\xbe\xd1\x82'), (b'WorkAndThumble', b'\xd0\xa5\xd0\xb2\xd0\xbe\xd1\x81\xd1\x82-\xd0\xbd\xd0\xb0-\xd0\xb3\xd0\xbe\xd0\xbb\xd0\xbe\xd0\xb2\xd1\x83'), (b'Perfecting', b'\xd0\xa7\xd1\x83\xd0\xb6\xd0\xbe\xd0\xb9 \xd0\xbe\xd0\xb1\xd0\xbe\xd1\x80\xd0\xbe\xd1\x82')])),
                ('paper', models.CharField(max_length=300, null=True, verbose_name=b'\xd0\x93\xd1\x80\xd0\xb0\xd0\xbc\xd0\xbc\xd0\xb0\xd0\xb6 \xd0\xb8 \xd1\x82\xd0\xb8\xd0\xbf \xd0\xb1\xd1\x83\xd0\xbc\xd0\xb0\xd0\xb3\xd0\xb8', blank=True)),
                ('paper_warehouse_unit', models.CharField(choices=[(b'leaf', b'\xd0\x9b\xd0\xb8\xd1\x81\xd1\x82\xd1\x8b'), (b'kg', b'\xd0\x9a\xd0\xb3')], max_length=4, blank=True, help_text=b'\xd0\x95\xd0\xb4\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x86\xd0\xb0 \xd0\xb1\xd1\x83\xd0\xbc\xd0\xb0\xd0\xb3\xd0\xb8 (\xd0\xa1\xd0\x9a\xd0\x9b\xd0\x90\xd0\x94)', null=True, verbose_name=b'\xd0\x95\xd0\xb4.:')),
                ('paper_warehouse_amount', models.DecimalField(decimal_places=2, max_digits=12, blank=True, help_text=b'\xd0\x9a\xd0\xbe\xd0\xbb\xd0\xb8\xd1\x87\xd0\xb5\xd1\x81\xd1\x82\xd0\xb2\xd0\xbe \xd0\xb5\xd0\xb4\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x86, \xd0\xb2\xd1\x8b\xd0\xb4\xd0\xb0\xd0\xbd\xd0\xbd\xd1\x8b\xd1\x85 \xd1\x81\xd0\xbe \xd1\x81\xd0\xba\xd0\xbb\xd0\xb0\xd0\xb4\xd0\xb0', null=True, verbose_name=b'\xd0\x9a\xd0\xbe\xd0\xbb-\xd0\xb2\xd0\xbe')),
                ('paper_warehouse_format', models.CharField(help_text=b'\xd0\xa4\xd0\xbe\xd1\x80\xd0\xbc\xd0\xb0\xd1\x82 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xbc\xd0\xbe\xd1\x82\xd0\xba\xd0\xb8 \xd0\x98\xd0\x9b\xd0\x98 \xd1\x84\xd0\xbe\xd1\x80\xd0\xbc\xd0\xb0\xd1\x82 \xd0\xbb\xd0\xb8\xd1\x81\xd1\x82\xd0\xbe\xd0\xb2\xd0\xbe\xd0\xb9 \xd0\xb1\xd1\x83\xd0\xbc\xd0\xb0\xd0\xb3\xd0\xb8', max_length=20, verbose_name=b'\xd0\xa4-\xd1\x82 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xbc\xd0\xbe\xd1\x82\xd0\xba\xd0\xb8', blank=True)),
                ('paper_printing_amount', models.CharField(help_text=b'\xd0\x9e\xd0\xb1\xd1\x89\xd0\xb5\xd0\xb5 \xd0\xba\xd0\xbe\xd0\xbb-\xd0\xb2\xd0\xbe \xd0\xb2\xd1\x8b\xd0\xb4\xd0\xb0\xd0\xbd\xd0\xbd\xd1\x8b\xd1\x85 \xd0\xbb\xd0\xb8\xd1\x81\xd1\x82\xd0\xbe\xd0\xb2', max_length=20, verbose_name=b'\xd0\x9f\xd0\xb5\xd1\x87\xd0\xb0\xd1\x82\xd1\x8c, \xd0\xba\xd0\xbe\xd0\xbb-\xd0\xb2\xd0\xbe', blank=True)),
                ('paper_printing_format', models.CharField(help_text=b'\xd0\xa4\xd0\xbe\xd1\x80\xd0\xbc\xd0\xb0\xd1\x82 \xd0\xb1\xd1\x83\xd0\xbc\xd0\xb0\xd0\xb3\xd0\xb8 \xd0\xb2 \xd0\xbf\xd0\xb5\xd1\x87\xd0\xb0\xd1\x82\xd1\x8c', max_length=20, verbose_name=b'\xd0\x9f\xd0\xb5\xd1\x87\xd0\xb0\xd1\x82\xd1\x8c, \xd1\x84-\xd1\x82', blank=True)),
                ('order', models.ForeignKey(to='technologichka.Order')),
                ('outputter', models.ForeignKey(verbose_name=b'\xd0\x92\xd1\x8b\xd0\xb2\xd0\xbe\xd0\xb4 \xd0\xbf\xd0\xbb\xd0\xb0\xd1\x81\xd1\x82\xd0\xb8\xd0\xbd', blank=True, to='technologichka.Contractor', null=True)),
                ('printingpress', models.ForeignKey(verbose_name=b'\xd0\x9f\xd0\xb5\xd1\x87\xd0\xb0\xd1\x82\xd0\xbd\xd0\xb0\xd1\x8f \xd0\xbc\xd0\xb0\xd1\x88\xd0\xb8\xd0\xbd\xd0\xb0', blank=True, to='workflow.PrintingPress', null=True)),
            ],
            options={
                'verbose_name': '\u041f\u0435\u0447\u0430\u0442\u043d\u044b\u0439 \u043b\u0438\u0441\u0442',
                'verbose_name_plural': '\u041f\u0435\u0447\u0430\u0442\u043d\u044b\u0435 \u043b\u0438\u0441\u0442\u044b',
            },
        ),
        migrations.AddField(
            model_name='operation',
            name='name',
            field=models.ForeignKey(verbose_name=b'\xd0\x9d\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5 \xd0\xbe\xd0\xbf\xd0\xb5\xd1\x80\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8', to='technologichka.OperationList', help_text=b'\xd0\xbb\xd1\x86\xd1\x83\xd0\xbf\xd1\x80\xd1\x83\xd0\xba\xd0\xbb\xd0\xbf\xd0\xbe\xd1\x80'),
        ),
        migrations.AddField(
            model_name='operation',
            name='order',
            field=models.ForeignKey(to='technologichka.Order'),
        ),
        migrations.AddField(
            model_name='operation',
            name='printsheet',
            field=models.ForeignKey(blank=True, to='technologichka.PrintSheet', help_text=b'\xd0\x95\xd1\x81\xd0\xbb\xd0\xb8 \xd0\xbe\xd0\xbf\xd0\xb5\xd1\x80\xd1\x86\xd0\xb8\xd1\x8f \xd0\xbd\xd0\xb5 \xd0\xbe\xd1\x82\xd0\xbd\xd0\xbe\xd1\x81\xd0\xb8\xd1\x82\xd1\x81\xd1\x8f \xd0\xba \xd0\xba\xd0\xbe\xd0\xbd\xd0\xba\xd1\x80\xd0\xb5\xd1\x82\xd0\xbd\xd0\xbe\xd0\xbc\xd1\x83 \xd0\xbf\xd0\xb5\xd1\x87\xd0\xb0\xd1\x82\xd0\xbd\xd0\xbe\xd0\xbc\xd1\x83 \xd0\xbb\xd0\xb8\xd1\x81\xd1\x82\xd1\x83, \xd0\xbe\xd1\x81\xd1\x82\xd0\xb0\xd0\xb2\xd1\x8c\xd1\x82\xd0\xb5 \xd1\x8d\xd1\x82\xd0\xbe \xd0\xbf\xd0\xbe\xd0\xbb\xd0\xb5 \xd0\xbf\xd1\x83\xd1\x81\xd1\x82\xd1\x8b\xd0\xbc', null=True, verbose_name=b'\xd0\x9f\xd0\xb5\xd1\x87\xd0\xb0\xd1\x82\xd0\xbd\xd1\x8b\xd0\xb9 \xd0\xbb\xd0\xb8\xd1\x81\xd1\x82'),
        ),
        migrations.AddField(
            model_name='detal',
            name='printsheet',
            field=models.ForeignKey(to='technologichka.PrintSheet'),
        ),
    ]
