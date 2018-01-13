# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0014_auto_20151013_0950'),
    ]

    operations = [
        migrations.RenameField(
            model_name='playlist',
            old_name='show',
            new_name='showname',
        ),
        migrations.AlterField(
            model_name='cdtrack',
            name='cdid',
            field=models.ForeignKey(related_name='tracks', on_delete=models.PROTECT, db_column='cdid', to='playlist.Cd'),
        ),
    ]
