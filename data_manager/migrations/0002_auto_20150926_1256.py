# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OccurrenceAttribute',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('value', models.CharField(max_length=1)),
                ('occurrence', models.ForeignKey(to='data_manager.Occurrence')),
                ('release_corresponding_entry', models.ForeignKey(to='data_manager.ReleaseAttribute')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OccurrenceCustomAttribute',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('value', models.CharField(max_length=1)),
                ('occurrence', models.ForeignKey(to='data_manager.Occurrence')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='occurenceattribute',
            name='occurrence',
        ),
        migrations.RemoveField(
            model_name='occurenceattribute',
            name='release_corresponding_entry',
        ),
        migrations.RemoveField(
            model_name='occurencecustomattribute',
            name='occurrence',
        ),
        migrations.RemoveField(
            model_name='occurencecustomattribute',
            name='release_corresponding_entry',
        ),
        migrations.AlterField(
            model_name='attribute',
            name='value_type',
            field=models.CharField(choices=[('PRS', 'Presence'), ('RTN', 'Rating')], max_length=3),
        ),
        migrations.AlterField(
            model_name='concept',
            name='primary_nature',
            field=models.CharField(choices=[('CONSOLE', 'Console'), ('Software', (('GAME', 'Game'), ('DEMO', 'Demo'))), ('Accessory', (('GUN', 'Gun'),))], max_length=10),
        ),
        migrations.AlterField(
            model_name='conceptnature',
            name='nature',
            field=models.CharField(choices=[('CONSOLE', 'Console'), ('Software', (('GAME', 'Game'), ('DEMO', 'Demo'))), ('Accessory', (('GUN', 'Gun'),))], max_length=10),
        ),
        migrations.AlterField(
            model_name='releasecustomattribute',
            name='value_type',
            field=models.CharField(choices=[('PRS', 'Presence'), ('RTN', 'Rating')], max_length=3),
        ),
        migrations.DeleteModel(
            name='OccurenceAttribute',
        ),
        migrations.DeleteModel(
            name='OccurenceCustomAttribute',
        ),
        migrations.AddField(
            model_name='occurrencecustomattribute',
            name='release_corresponding_entry',
            field=models.ForeignKey(to='data_manager.ReleaseCustomAttribute'),
        ),
    ]
