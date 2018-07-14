# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0017_auto_20151119_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='showname',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='playlistentry',
            name='playlist',
            field=models.ForeignKey(related_name='tracks',on_delete=models.PROTECT, to='playlist.Playlist'),
        ),
    ]
