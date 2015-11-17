# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('data_manager', '0004_auto_20151027_1110'),
    ]

    operations = [
        migrations.CreateModel(
            name='Operational',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('release', models.ForeignKey(to='data_manager.Occurrence')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TagToOccurrnce',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('tag_occurrence_id', models.IntegerField()),
                ('occurrence', models.OneToOneField(to='data_manager.Occurrence')),
            ],
        ),
        migrations.CreateModel(
            name='UserExtension',
            fields=[
                ('user', models.OneToOneField(serialize=False, primary_key=True, to=settings.AUTH_USER_MODEL)),
                ('guid', models.IntegerField(unique=True)),
            ],
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
            model_name='releaseattribute',
            name='note',
            field=models.CharField(help_text='Distinctive remark if the attribute is repeated.', blank=True, max_length=60, default=''),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='releaseattribute',
            unique_together=set([('release', 'attribute', 'note')]),
        ),
        migrations.AlterUniqueTogether(
            name='releasecustomattribute',
            unique_together=set([('release', 'note')]),
        ),
        migrations.AddField(
            model_name='tagtooccurrnce',
            name='user',
            field=models.ForeignKey(to='data_manager.UserExtension'),
        ),
        migrations.AddField(
            model_name='concept',
            name='created_by',
            field=models.ForeignKey(to='data_manager.UserExtension', default=1),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='tagtooccurrnce',
            unique_together=set([('user', 'tag_occurrence_id')]),
        ),
    ]
