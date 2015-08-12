# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Console',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('region_modded', models.BooleanField()),
                ('copy_modded', models.BooleanField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('lastmodif_date', models.DateTimeField(auto_now=True)),
                ('release', models.ForeignKey(to='data_manager.Release')),
            ],
        ),
        migrations.RemoveField(
            model_name='instance',
            name='release',
        ),
        migrations.DeleteModel(
            name='Instance',
        ),
        migrations.AddField(
            model_name='console',
            name='release',
            field=models.ForeignKey(to='data_manager.Occurrence'),
        ),
    ]
