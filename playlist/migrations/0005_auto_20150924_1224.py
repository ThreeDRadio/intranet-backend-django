# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0004_playlistentry_playlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlistentry',
            name='catalogueEntry',
            field=models.ForeignKey(to='playlist.Cdtrack', null=True),
        ),
    ]
