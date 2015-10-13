# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=60)),
                ('description', models.CharField(blank=True, max_length=180)),
                ('value_type', models.CharField(max_length=3, choices=[('PRS', 'Presence'), ('RTN', 'Rating')])),
            ],
        ),
        migrations.CreateModel(
            name='AttributeCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('common_name', models.CharField(blank=True, max_length=60)),
                ('distinctive_name', models.CharField(unique=True, max_length=180)),
                ('primary_nature', models.CharField(max_length=10, choices=[('_COMBO', '_COMBO'), ('CONSOLE', 'Console'), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game'))), ('Accessory', (('GUN', 'Gun'),))])),
            ],
        ),
        migrations.CreateModel(
            name='ConceptNature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('nature', models.CharField(max_length=10, choices=[('_COMBO', '_COMBO'), ('CONSOLE', 'Console'), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game'))), ('Accessory', (('GUN', 'Gun'),))])),
                ('concept', models.ForeignKey(to='data_manager.Concept', related_name='additional_nature_set')),
            ],
        ),
        migrations.CreateModel(
            name='Console',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('region_modded', models.BooleanField()),
                ('copy_modded', models.BooleanField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Demo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('issue_number', models.PositiveIntegerField(blank=True, null=True)),
                ('games_playable', models.ManyToManyField(to='data_manager.Concept', blank=True, related_name='playable_demo_set')),
                ('games_video', models.ManyToManyField(to='data_manager.Concept', blank=True, related_name='video_demo_set')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Hardware',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('model', models.CharField(blank=True, max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Memory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('capacity', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('lastmodif_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='OccurrenceAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('value', models.CharField(max_length=1)),
                ('occurrence', models.ForeignKey(to='data_manager.Occurrence')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OccurrenceComposition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('from_occurrence', models.ForeignKey(to='data_manager.Occurrence', related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='OccurrenceCustomAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('value', models.CharField(max_length=1)),
                ('occurrence', models.ForeignKey(to='data_manager.Occurrence')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('loose', models.BooleanField()),
                ('version', models.CharField(blank=True, max_length=20)),
                ('name', models.CharField(blank=True, max_length=180, verbose_name="Release's name")),
                ('date', models.DateField(blank=True, null=True)),
                ('barcode', models.CharField(blank=True, max_length=20)),
                ('concept', models.ForeignKey(to='data_manager.Concept')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReleaseAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('note', models.CharField(blank=True, max_length=60, help_text='Distinctive remark if the attribute is repeated.', null=True)),
                ('attribute', models.ForeignKey(to='data_manager.Attribute')),
                ('release', models.ForeignKey(to='data_manager.Release')),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseComposition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('from_release', models.ForeignKey(to='data_manager.Release', related_name='+')),
                ('to_release', models.ForeignKey(to='data_manager.Release')),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseCustomAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=60)),
                ('description', models.CharField(blank=True, max_length=180)),
                ('value_type', models.CharField(max_length=3, choices=[('PRS', 'Presence'), ('RTN', 'Rating')])),
                ('note', models.CharField(blank=True, max_length=60, help_text='Distinctive remark if the attribute is repeated.', null=True)),
                ('category', models.ForeignKey(to='data_manager.AttributeCategory')),
                ('release', models.ForeignKey(to='data_manager.Release')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Software',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('immaterial', models.BooleanField(default=False)),
                ('collection_label', models.CharField(blank=True, max_length=120, verbose_name='Released in collection')),
                ('release', models.ForeignKey(to='data_manager.Release')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='release',
            name='nested_releases',
            field=models.ManyToManyField(to='data_manager.Release', through='data_manager.ReleaseComposition'),
        ),
        migrations.AddField(
            model_name='occurrencecustomattribute',
            name='release_corresponding_entry',
            field=models.ForeignKey(to='data_manager.ReleaseCustomAttribute'),
        ),
        migrations.AddField(
            model_name='occurrencecomposition',
            name='release_composition',
            field=models.ForeignKey(to='data_manager.ReleaseComposition'),
        ),
        migrations.AddField(
            model_name='occurrencecomposition',
            name='to_occurrence',
            field=models.ForeignKey(null=True, to='data_manager.Occurrence', blank=True),
        ),
        migrations.AddField(
            model_name='occurrenceattribute',
            name='release_corresponding_entry',
            field=models.ForeignKey(to='data_manager.ReleaseAttribute'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='nested_occurrences',
            field=models.ManyToManyField(to='data_manager.Occurrence', through='data_manager.OccurrenceComposition'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='release',
            field=models.ForeignKey(to='data_manager.Release'),
        ),
        migrations.AddField(
            model_name='memory',
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
        migrations.AddField(
            model_name='console',
            name='release',
            field=models.ForeignKey(to='data_manager.Occurrence'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='category',
            field=models.ForeignKey(to='data_manager.AttributeCategory'),
        ),
        migrations.AlterUniqueTogether(
            name='attribute',
            unique_together=set([('category', 'name')]),
        ),
    ]
