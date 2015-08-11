# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('common_name', models.CharField(max_length=60, blank=True)),
                ('distinctive_name', models.CharField(unique=True, max_length=180)),
                ('primary_nature', models.CharField(max_length=10, choices=[('CONSOLE', 'Console'), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game')))])),
            ],
        ),
        migrations.CreateModel(
            name='ConceptNature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('nature', models.CharField(max_length=10, choices=[('CONSOLE', 'Console'), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game')))])),
                ('concept', models.ForeignKey(to='data_manager.Concept', related_name='additional_nature_set')),
            ],
        ),
        migrations.CreateModel(
            name='Demo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('issue_number', models.PositiveIntegerField(null=True, blank=True)),
                ('games_playable', models.ManyToManyField(blank=True, related_name='playable_demo_set', to='data_manager.Concept')),
                ('games_video', models.ManyToManyField(blank=True, related_name='video_demo_set', to='data_manager.Concept')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Hardware',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('model', models.CharField(max_length=20, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Memory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('capacity', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('loose', models.BooleanField()),
                ('version', models.CharField(max_length=20, blank=True)),
                ('name', models.CharField(max_length=180, blank=True, verbose_name="Release's name")),
                ('date', models.DateField(null=True, blank=True)),
                ('barcode', models.CharField(max_length=20, blank=True)),
                ('concept', models.ForeignKey(to='data_manager.Concept')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Software',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('immaterial', models.BooleanField(default=False)),
                ('collection_label', models.CharField(max_length=120, blank=True, verbose_name='Released in collection')),
                ('release', models.ForeignKey(to='data_manager.Release')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='memory',
            name='release',
            field=models.ForeignKey(to='data_manager.Release'),
        ),
        migrations.AddField(
            model_name='instance',
            name='release',
            field=models.ForeignKey(to='data_manager.Release'),
        ),
        migrations.AddField(
            model_name='hardware',
            name='release',
            field=models.ForeignKey(to='data_manager.Release'),
        ),
        migrations.AddField(
            model_name='demo',
            name='release',
            field=models.ForeignKey(to='data_manager.Release'),
        ),
    ]
