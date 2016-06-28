# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0003_auto_20160628_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cdcomment',
            name='cdid',
            field=models.ForeignKey(related_name='comments', db_column=b'cdid', to='catalogue.Release'),
        ),
    ]
