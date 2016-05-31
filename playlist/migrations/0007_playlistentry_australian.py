# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0006_auto_20150924_1256'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlistentry',
            name='australian',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]
