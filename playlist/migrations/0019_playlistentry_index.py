# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0018_auto_20160603_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlistentry',
            name='index',
            field=models.IntegerField(null=True),
        ),
    ]
