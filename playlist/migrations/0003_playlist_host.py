# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0002_playlist_complete'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='host',
            field=models.CharField(default='Michael', max_length=200),
            preserve_default=False,
        ),
    ]
