# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0005_auto_20150828_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='value_type',
            field=models.CharField(max_length=3, choices=[('PRS', 'Presence'), ('RTN', 'Rating')]),
        ),
    ]
