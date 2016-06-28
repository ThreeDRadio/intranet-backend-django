# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_auto_20160628_1033'),
    ]

    operations = [
        migrations.RenameField(
            model_name='track',
            old_name='cdid',
            new_name='release',
        ),
    ]
