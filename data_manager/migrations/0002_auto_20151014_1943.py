# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='value_type',
            field=models.CharField(max_length=3, choices=[('RTN', 'Rating'), ('PRS', 'Presence')]),
        ),
        migrations.AlterField(
            model_name='concept',
            name='primary_nature',
            field=models.CharField(max_length=10, choices=[('CONSOLE', 'Console'), ('Accessory', (('GUN', 'Gun'),)), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game')))]),
        ),
        migrations.AlterField(
            model_name='conceptnature',
            name='nature',
            field=models.CharField(max_length=10, choices=[('CONSOLE', 'Console'), ('Accessory', (('GUN', 'Gun'),)), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game')))]),
        ),
        migrations.AlterField(
            model_name='releaseattribute',
            name='release',
            field=models.ForeignKey(null=True, to='data_manager.Release'),
        ),
        migrations.AlterField(
            model_name='releasecustomattribute',
            name='value_type',
            field=models.CharField(max_length=3, choices=[('RTN', 'Rating'), ('PRS', 'Presence')]),
        ),
    ]
