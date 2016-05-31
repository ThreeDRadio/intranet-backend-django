# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0007_playlistentry_australian'),
    ]

    operations = [
        migrations.CreateModel(
            name='Show',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('show', models.CharField(max_length=200)),
                ('defaultHost', models.CharField(max_length=200, blank=True)),
                ('startTime', models.TimeField()),
                ('endTime', models.TimeField()),
            ],
        ),
    ]
