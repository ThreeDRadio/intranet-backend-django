# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0008_show'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]
