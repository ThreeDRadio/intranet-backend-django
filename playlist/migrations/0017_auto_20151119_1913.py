# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0016_auto_20151013_2137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='show',
            field=models.ForeignKey(related_name='playlists', to='playlist.Show', on_delete=models.PROTECT, null=True),
        ),
    ]
