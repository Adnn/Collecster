# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-11 10:25
from __future__ import unicode_literals

from Collecster.migration_utils import load_initial_fixtures_func

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advideogame', '0001_initial'),
        ('supervisor',  '0002_initial_data'),
    ]

    operations = [
        migrations.RunPython(load_initial_fixtures_func("advideogame")),
    ]