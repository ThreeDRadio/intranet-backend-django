# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0011_auto_20151012_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlistentry',
            name='album',
            field=models.CharField(default='Album', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='playlistentry',
            name='artist',
            field=models.CharField(default='artist', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='playlistentry',
            name='title',
            field=models.CharField(default='track', max_length=200),
            preserve_default=False,
        ),
    ]
