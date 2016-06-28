# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0006_auto_20160628_1034'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Cdcomment',
            new_name='Comment',
        ),
    ]
