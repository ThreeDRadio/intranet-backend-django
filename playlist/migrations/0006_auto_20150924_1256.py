# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0005_auto_20150924_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlistentry',
            name='duration',
            field=models.DurationField(blank=True),
        ),
    ]
