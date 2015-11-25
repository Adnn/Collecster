# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0011_auto_20151125_1533'),
    ]

    operations = [
        migrations.RenameField(
            model_name='release',
            old_name='partial_precision',
            new_name='partial_date_precision',
        ),
        migrations.AlterField(
            model_name='attribute',
            name='value_type',
            field=models.CharField(max_length=3, choices=[('PRS', 'Presence'), ('RTN', 'Rating')]),
        ),
        migrations.AlterField(
            model_name='concept',
            name='primary_nature',
            field=models.CharField(max_length=7, choices=[('CONSOLE', 'Console'), ('Accessory', (('GUN', 'Gun'),)), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game')))]),
        ),
        migrations.AlterField(
            model_name='conceptnature',
            name='nature',
            field=models.CharField(max_length=7, choices=[('CONSOLE', 'Console'), ('Accessory', (('GUN', 'Gun'),)), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game')))]),
        ),
        migrations.AlterField(
            model_name='releasecustomattribute',
            name='value_type',
            field=models.CharField(max_length=3, choices=[('PRS', 'Presence'), ('RTN', 'Rating')]),
        ),
    ]
