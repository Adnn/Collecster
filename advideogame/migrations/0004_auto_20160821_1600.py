# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-21 14:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advideogame', '0003_auto_20160811_1713'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='systemspecification',
            options={'ordering': ['interfaces_specification__internal_name', 'bios_version']},
        ),
    ]
