# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0003_playlist_host'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlistentry',
            name='playlist',
            field=models.ForeignKey(default=5, on_delete=models.PROTECT, to='playlist.Playlist'),
            preserve_default=False,
        ),
    ]
