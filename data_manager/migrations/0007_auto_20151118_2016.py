# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_manager', '0006_auto_20151118_1952'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagToOccurrence',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('tag_occurrence_id', models.IntegerField()),
                ('occurrence', models.OneToOneField(to='data_manager.Occurrence')),
                ('user', models.ForeignKey(to='data_manager.UserExtension')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='tagtooccurrnce',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='tagtooccurrnce',
            name='occurrence',
        ),
        migrations.RemoveField(
            model_name='tagtooccurrnce',
            name='user',
        ),
        migrations.DeleteModel(
            name='TagToOccurrnce',
        ),
        migrations.AlterUniqueTogether(
            name='tagtooccurrence',
            unique_together=set([('user', 'tag_occurrence_id')]),
        ),
    ]
