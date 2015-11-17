# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0002_auto_20151014_1943'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='software',
            name='immaterial',
        ),
        migrations.AddField(
            model_name='occurrence',
            name='blister',
            field=models.BooleanField(default=False, help_text='Indicates whether a blister is still present.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='occurrence',
            name='immaterial',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='notes',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='price',
            field=models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='releaseattribute',
            name='release',
            field=models.ForeignKey(to='data_manager.Release'),
        ),
    ]
