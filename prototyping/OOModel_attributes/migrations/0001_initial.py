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
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='InstanceAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('value', models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B')])),
                ('instance', models.ForeignKey(to='OOModel_attributes.Instance')),
            ],
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('note', models.CharField(null=True, blank=True, max_length=120)),
                ('attribute', models.ForeignKey(to='OOModel_attributes.Attribute')),
                ('release', models.ForeignKey(to='OOModel_attributes.Release')),
            ],
        ),
        migrations.CreateModel(
            name='UniqueAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.AddField(
            model_name='release',
            name='attributes',
            field=models.ManyToManyField(to='OOModel_attributes.Attribute', through='OOModel_attributes.ReleaseAttribute'),
        ),
        migrations.AddField(
            model_name='release',
            name='unique_attributes',
            field=models.ManyToManyField(to='OOModel_attributes.UniqueAttribute', blank=True),
        ),
        migrations.AddField(
            model_name='instanceattribute',
            name='release_attribute',
            field=models.ForeignKey(to='OOModel_attributes.ReleaseAttribute'),
        ),
        migrations.AddField(
            model_name='instance',
            name='release',
            field=models.ForeignKey(to='OOModel_attributes.Release'),
        ),
        migrations.AddField(
            model_name='instance',
            name='release_attributes',
            field=models.ManyToManyField(to='OOModel_attributes.ReleaseAttribute', through='OOModel_attributes.InstanceAttribute'),
        ),
    ]
