# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0008_auto_20151120_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='value_type',
            field=models.CharField(choices=[('RTN', 'Rating'), ('PRS', 'Presence')], max_length=3),
        ),
        migrations.AlterField(
            model_name='occurrencecomposition',
            name='to_occurrence',
            field=models.OneToOneField(to='data_manager.Occurrence', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='releasecustomattribute',
            name='value_type',
            field=models.CharField(choices=[('RTN', 'Rating'), ('PRS', 'Presence')], max_length=3),
        ),
    ]
