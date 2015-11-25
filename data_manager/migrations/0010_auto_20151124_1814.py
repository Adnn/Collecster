# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0009_auto_20151121_1252'),
    ]

    operations = [
        migrations.RenameField(
            model_name='release',
            old_name='date',
            new_name='partial_date',
        ),
        migrations.AddField(
            model_name='release',
            name='partial_part',
            field=models.CharField(max_length=8, blank=True, choices=[('%Y', 'Year'), ('%Y-%m', 'Month'), ('%Y-%m-%d', 'Day')]),
        ),
        migrations.AlterField(
            model_name='attribute',
            name='value_type',
            field=models.CharField(max_length=3, choices=[('PRS', 'Presence'), ('RTN', 'Rating')]),
        ),
        migrations.AlterField(
            model_name='concept',
            name='primary_nature',
            field=models.CharField(max_length=7, choices=[('CONSOLE', 'Console'), ('Accessory', (('GUN', 'Gun'),)), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game')))]),
        ),
        migrations.AlterField(
            model_name='conceptnature',
            name='nature',
            field=models.CharField(max_length=7, choices=[('CONSOLE', 'Console'), ('Accessory', (('GUN', 'Gun'),)), ('Software', (('DEMO', 'Demo'), ('GAME', 'Game')))]),
        ),
        migrations.AlterField(
            model_name='occurrencecomposition',
            name='to_occurrence',
            field=models.OneToOneField(null=True, to='data_manager.Occurrence', related_name='occurrence_composition', blank=True),
        ),
        migrations.AlterField(
            model_name='releasecustomattribute',
            name='value_type',
            field=models.CharField(max_length=3, choices=[('PRS', 'Presence'), ('RTN', 'Rating')]),
        ),
        migrations.AlterUniqueTogether(
            name='conceptnature',
            unique_together=set([('concept', 'nature')]),
        ),
        migrations.AlterUniqueTogether(
            name='occurrenceattribute',
            unique_together=set([('occurrence', 'release_corresponding_entry')]),
        ),
        migrations.AlterUniqueTogether(
            name='occurrencecomposition',
            unique_together=set([('release_composition', 'from_occurrence')]),
        ),
        migrations.AlterUniqueTogether(
            name='occurrencecustomattribute',
            unique_together=set([('occurrence', 'release_corresponding_entry')]),
        ),
    ]
