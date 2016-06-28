# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0002_oldpassword'),
    ]

    operations = [
        migrations.CreateModel(
            name='OldUser',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=100)),
                ('password', models.CharField(max_length=100, null=True, blank=True)),
                ('first', models.CharField(max_length=100, null=True, blank=True)),
                ('last', models.CharField(max_length=100, null=True, blank=True)),
                ('admin', models.NullBooleanField()),
                ('active', models.NullBooleanField()),
                ('cdeditor', models.NullBooleanField()),
                ('adminbook', models.NullBooleanField()),
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
        ),
    ]
