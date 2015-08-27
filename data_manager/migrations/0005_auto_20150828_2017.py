# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0004_auto_20150817_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concept',
            name='primary_nature',
            field=models.CharField(max_length=10, choices=[('CONSOLE', 'Console'), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game')))]),
        ),
        migrations.AlterField(
            model_name='conceptnature',
            name='nature',
            field=models.CharField(max_length=10, choices=[('CONSOLE', 'Console'), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game')))]),
        ),
    ]
