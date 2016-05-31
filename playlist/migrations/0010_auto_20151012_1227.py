# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0009_playlist_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlistentry',
            name='duration',
            field=models.DurationField(null=True, blank=True),
        ),
    ]
