# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0003_auto_20151027_1107'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='occurrence',
            name='immaterial',
        ),
        migrations.AddField(
            model_name='release',
            name='immaterial',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='concept',
            name='primary_nature',
            field=models.CharField(choices=[('CONSOLE', 'Console'), ('Accessory', (('GUN', 'Gun'),)), ('Software', (('GAME', 'Game'), ('DEMO', 'Demo')))], max_length=10),
        ),
        migrations.AlterField(
            model_name='conceptnature',
            name='nature',
            field=models.CharField(choices=[('CONSOLE', 'Console'), ('Accessory', (('GUN', 'Gun'),)), ('Software', (('GAME', 'Game'), ('DEMO', 'Demo')))], max_length=10),
        ),
    ]
