# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0006_auto_20150828_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='value_type',
            field=models.CharField(max_length=3, choices=[('RTN', 'Rating'), ('PRS', 'Presence')]),
        ),
    ]
