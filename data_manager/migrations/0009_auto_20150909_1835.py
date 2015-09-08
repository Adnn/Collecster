# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0008_auto_20150908_2047'),
    ]

    operations = [
        migrations.RenameField(
            model_name='occurenceattribute',
            old_name='release_attribute',
            new_name='release_corresponding_entry',
        ),
        migrations.RenameField(
            model_name='occurencecustomattribute',
            old_name='release_custom_attribute',
            new_name='release_corresponding_entry',
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
