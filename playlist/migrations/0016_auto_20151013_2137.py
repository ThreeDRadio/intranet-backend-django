# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0015_auto_20151013_1242'),
    ]

    operations = [
        migrations.RenameField(
            model_name='show',
            old_name='show',
            new_name='name',
        ),
        migrations.AddField(
            model_name='playlist',
            name='show',
            field=models.ForeignKey(null=True, to='playlist.Show'),
            preserve_default=False,
        ),
    ]
