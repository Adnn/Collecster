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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=60)),
                ('description', models.CharField(blank=True, max_length=180)),
                ('value_type', models.CharField(max_length=3, choices=[('RTN', 'Rating'), ('PRS', 'Presence')])),
            ],
        ),
        migrations.CreateModel(
            name='AttributeCategory',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('common_name', models.CharField(blank=True, max_length=60)),
                ('distinctive_name', models.CharField(unique=True, max_length=180)),
                ('primary_nature', models.CharField(max_length=10, choices=[('CONSOLE', 'Console'), ('Accessory', (('GUN', 'Gun'),)), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game')))])),
            ],
        ),
        migrations.CreateModel(
            name='ConceptNature',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('nature', models.CharField(max_length=10, choices=[('CONSOLE', 'Console'), ('Accessory', (('GUN', 'Gun'),)), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game')))])),
                ('concept', models.ForeignKey(related_name='additional_nature_set', to='data_manager.Concept')),
            ],
        ),
        migrations.CreateModel(
            name='Console',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('issue_number', models.PositiveIntegerField(blank=True, null=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('model', models.CharField(blank=True, max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Memory',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('capacity', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OccurenceAttribute',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('value', models.CharField(max_length=1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OccurenceCustomAttribute',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('value', models.CharField(max_length=1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('lastmodif_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='OccurrenceComposition',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('from_occurrence', models.ForeignKey(related_name='+', to='data_manager.Occurrence')),
            ],
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('note', models.CharField(max_length=60, blank=True, help_text='Distinctive remark if the attribute is repeated.', null=True)),
                ('attribute', models.ForeignKey(to='data_manager.Attribute')),
                ('release', models.ForeignKey(to='data_manager.Release')),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseComposition',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('from_release', models.ForeignKey(related_name='+', to='data_manager.Release')),
                ('to_release', models.ForeignKey(to='data_manager.Release')),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseCustomAttribute',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=60)),
                ('description', models.CharField(blank=True, max_length=180)),
                ('value_type', models.CharField(max_length=3, choices=[('RTN', 'Rating'), ('PRS', 'Presence')])),
                ('note', models.CharField(max_length=60, blank=True, help_text='Distinctive remark if the attribute is repeated.', null=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
            field=models.ManyToManyField(through='data_manager.ReleaseComposition', to='data_manager.Release'),
        ),
        migrations.AddField(
            model_name='occurrencecomposition',
            name='release_composition',
            field=models.ForeignKey(to='data_manager.ReleaseComposition'),
        ),
        migrations.AddField(
            model_name='occurrencecomposition',
            name='to_occurrence',
            field=models.ForeignKey(blank=True, to='data_manager.Occurrence', null=True),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='nested_occurrences',
            field=models.ManyToManyField(through='data_manager.OccurrenceComposition', to='data_manager.Occurrence'),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='release',
            field=models.ForeignKey(to='data_manager.Release'),
        ),
        migrations.AddField(
            model_name='occurencecustomattribute',
            name='occurrence',
            field=models.ForeignKey(to='data_manager.Occurrence'),
        ),
        migrations.AddField(
            model_name='occurencecustomattribute',
            name='release_corresponding_entry',
            field=models.ForeignKey(to='data_manager.ReleaseCustomAttribute'),
        ),
        migrations.AddField(
            model_name='occurenceattribute',
            name='occurrence',
            field=models.ForeignKey(to='data_manager.Occurrence'),
        ),
        migrations.AddField(
            model_name='occurenceattribute',
            name='release_corresponding_entry',
            field=models.ForeignKey(to='data_manager.ReleaseAttribute'),
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
