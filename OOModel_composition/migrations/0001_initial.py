# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='InstanceComposition',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('container', models.ForeignKey(to='OOModel_composition.Instance', related_name='container_of_set')),
                ('nested_instance', models.OneToOneField(to='OOModel_composition.Instance', related_name='element_of')),
            ],
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseComposition',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('container_release', models.ForeignKey(to='OOModel_composition.Release', related_name='container_of_set')),
                ('nested_object', models.ForeignKey(to='OOModel_composition.Release', related_name='element_of_set')),
            ],
        ),
        migrations.AddField(
            model_name='release',
            name='composition',
            field=models.ManyToManyField(through='OOModel_composition.ReleaseComposition', to='OOModel_composition.Release'),
        ),
        migrations.AddField(
            model_name='instance',
            name='release',
            field=models.ForeignKey(to='OOModel_composition.Release'),
        ),
    ]
