# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0002_auto_20150812_1949'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('description', models.CharField(blank=True, max_length=180)),
                ('value_type', models.CharField(max_length=3, choices=[('Rating', 'RTN'), ('Presence', 'PRS')])),
            ],
        ),
        migrations.CreateModel(
            name='AttributeCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=60, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='OccurenceAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('value', models.CharField(max_length=1)),
                ('occurrence', models.ForeignKey(to='data_manager.Occurrence')),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('note', models.CharField(null=True, blank=True, max_length=60, help_text='Distinctive remark if the attribute is repeated.')),
                ('attribute', models.ForeignKey(to='data_manager.Attribute')),
                ('release', models.ForeignKey(to='data_manager.Release')),
            ],
        ),
        migrations.AlterField(
            model_name='concept',
            name='primary_nature',
            field=models.CharField(max_length=10, choices=[('CONSOLE', 'Console'), ('Software', (('GAME', 'Game'), ('DEMO', 'Demo')))]),
        ),
        migrations.AlterField(
            model_name='conceptnature',
            name='nature',
            field=models.CharField(max_length=10, choices=[('CONSOLE', 'Console'), ('Software', (('GAME', 'Game'), ('DEMO', 'Demo')))]),
        ),
        migrations.AddField(
            model_name='occurenceattribute',
            name='release_attribute',
            field=models.ForeignKey(to='data_manager.ReleaseAttribute'),
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
