# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0010_auto_20151124_1814'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='release',
            name='partial_part',
        ),
        migrations.AddField(
            model_name='release',
            name='partial_precision',
            field=models.CharField(choices=[('%Y-%m-%d', 'Day'), ('%Y-%m', 'Month'), ('%Y', 'Year')], max_length=8, blank=True, default='%Y-%m-%d', verbose_name='Date precision'),
        ),
        migrations.AlterField(
            model_name='attribute',
            name='value_type',
            field=models.CharField(choices=[('RTN', 'Rating'), ('PRS', 'Presence')], max_length=3),
        ),
        migrations.AlterField(
            model_name='concept',
            name='primary_nature',
            field=models.CharField(choices=[('CONSOLE', 'Console'), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game'))), ('Accessory', (('GUN', 'Gun'),))], max_length=7),
        ),
        migrations.AlterField(
            model_name='conceptnature',
            name='nature',
            field=models.CharField(choices=[('CONSOLE', 'Console'), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game'))), ('Accessory', (('GUN', 'Gun'),))], max_length=7),
        ),
        migrations.AlterField(
            model_name='release',
            name='partial_date',
            field=models.DateField(null=True, verbose_name='Date', blank=True),
        ),
        migrations.AlterField(
            model_name='releasecustomattribute',
            name='value_type',
            field=models.CharField(choices=[('RTN', 'Rating'), ('PRS', 'Presence')], max_length=3),
        ),
    ]
