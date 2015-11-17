# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0005_auto_20151118_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='occurrence',
            name='created_by',
            field=models.ForeignKey(default=1, to='data_manager.UserExtension'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='release',
            name='created_by',
            field=models.ForeignKey(default=1, to='data_manager.UserExtension'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attribute',
            name='value_type',
            field=models.CharField(max_length=3, choices=[('PRS', 'Presence'), ('RTN', 'Rating')]),
        ),
        migrations.AlterField(
            model_name='concept',
            name='primary_nature',
            field=models.CharField(max_length=10, choices=[('CONSOLE', 'Console'), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game'))), ('Accessory', (('GUN', 'Gun'),))]),
        ),
        migrations.AlterField(
            model_name='conceptnature',
            name='nature',
            field=models.CharField(max_length=10, choices=[('CONSOLE', 'Console'), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game'))), ('Accessory', (('GUN', 'Gun'),))]),
        ),
        migrations.AlterField(
            model_name='releasecustomattribute',
            name='value_type',
            field=models.CharField(max_length=3, choices=[('PRS', 'Presence'), ('RTN', 'Rating')]),
        ),
    ]
