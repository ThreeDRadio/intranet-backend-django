# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('session', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OldPassword',
            fields=[
                ('user', models.OneToOneField(primary_key=True, on_delete=models.PROTECT, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('password', models.CharField(max_length=200)),
            ],
        ),
    ]
