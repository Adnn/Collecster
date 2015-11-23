# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0007_auto_20151118_2016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concept',
            name='primary_nature',
            field=models.CharField(choices=[('CONSOLE', 'Console'), ('Software', (('GAME', 'Game'), ('DEMO', 'Demo'))), ('Accessory', (('GUN', 'Gun'),))], max_length=10),
        ),
        migrations.AlterField(
            model_name='conceptnature',
            name='nature',
            field=models.CharField(choices=[('CONSOLE', 'Console'), ('Software', (('GAME', 'Game'), ('DEMO', 'Demo'))), ('Accessory', (('GUN', 'Gun'),))], max_length=10),
        ),
        migrations.AlterField(
            model_name='occurrencecomposition',
            name='to_occurrence',
            field=models.ForeignKey(unique=True, null=True, to='data_manager.Occurrence', blank=True),
        ),
    ]
