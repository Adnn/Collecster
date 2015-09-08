# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0007_auto_20150828_2021'),
    ]

    operations = [
        migrations.CreateModel(
            name='OccurenceCustomAttribute',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=1)),
                ('occurrence', models.ForeignKey(to='data_manager.Occurrence')),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseCustomAttribute',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('description', models.CharField(blank=True, max_length=180)),
                ('value_type', models.CharField(choices=[('PRS', 'Presence'), ('RTN', 'Rating')], max_length=3)),
                ('note', models.CharField(help_text='Distinctive remark if the attribute is repeated.', max_length=60, blank=True, null=True)),
                ('category', models.ForeignKey(to='data_manager.AttributeCategory')),
                ('release', models.ForeignKey(to='data_manager.Release')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='attribute',
            name='value_type',
            field=models.CharField(choices=[('PRS', 'Presence'), ('RTN', 'Rating')], max_length=3),
        ),
        migrations.AddField(
            model_name='occurencecustomattribute',
            name='release_custom_attribute',
            field=models.ForeignKey(to='data_manager.ReleaseCustomAttribute'),
        ),
    ]
