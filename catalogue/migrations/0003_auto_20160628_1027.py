# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0002_auto_20160628_1024'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Cdtrack',
            new_name='Track',
        ),
    ]
