# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0010_auto_20151012_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlistentry',
            name='duration',
            field=models.DurationField(default=datetime.timedelta(0), null=True, blank=True),
        ),
    ]
