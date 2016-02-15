# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-12 10:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('configuration', models.CharField(max_length=20, unique=True)),
                ('version', models.DecimalField(decimal_places=2, default=1.0, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('nickname', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_collection_id', models.IntegerField()),
                ('deployment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisor.Deployment')),
            ],
        ),
        migrations.CreateModel(
            name='UserExtension',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('guid', models.IntegerField(unique=True)),
                ('person', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='supervisor.Person')),
            ],
        ),
        migrations.AddField(
            model_name='usercollection',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisor.UserExtension'),
        ),
        migrations.AlterUniqueTogether(
            name='usercollection',
            unique_together=set([('user', 'user_collection_id'), ('user', 'deployment')]),
        ),
    ]