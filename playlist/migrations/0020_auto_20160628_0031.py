# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0019_playlistentry_index'),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name='playlistentry',
            name='catalogueEntry',
        ),
        migrations.DeleteModel(
            name='Cdcomment',
        ),
        migrations.DeleteModel(
            name='Cd',
        ),
        migrations.DeleteModel(
            name='Cdtrack',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
