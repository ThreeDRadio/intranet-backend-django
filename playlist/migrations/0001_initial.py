# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cd',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('artist', models.CharField(max_length=200, null=True, blank=True)),
                ('title', models.CharField(max_length=200, null=True, blank=True)),
                ('year', models.SmallIntegerField(null=True, blank=True)),
                ('genre', models.CharField(max_length=50, null=True, blank=True)),
                ('company', models.CharField(max_length=100, null=True, blank=True)),
                ('cpa', models.CharField(max_length=100, null=True, blank=True)),
                ('arrivaldate', models.DateField(null=True, blank=True)),
                ('copies', models.SmallIntegerField(null=True, blank=True)),
                ('compilation', models.SmallIntegerField(null=True, blank=True)),
                ('demo', models.SmallIntegerField(null=True, blank=True)),
                ('local', models.SmallIntegerField(null=True, blank=True)),
                ('female', models.SmallIntegerField(null=True, blank=True)),
                ('createwho', models.BigIntegerField(null=True, blank=True)),
                ('createwhen', models.BigIntegerField(null=True, blank=True)),
                ('modifywho', models.BigIntegerField(null=True, blank=True)),
                ('modifywhen', models.BigIntegerField(null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('status', models.SmallIntegerField(null=True, blank=True)),
                ('format', models.SmallIntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'cd',
            },
        ),
        migrations.CreateModel(
            name='Cdcomment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cdid', models.BigIntegerField()),
                ('cdtrackid', models.BigIntegerField()),
                ('comment', models.TextField(null=True, blank=True)),
                ('createwho', models.BigIntegerField()),
                ('createwhen', models.BigIntegerField()),
                ('modifywho', models.BigIntegerField()),
                ('modifywhen', models.BigIntegerField()),
            ],
            options={
                'db_table': 'cdcomment',
            },
        ),
        migrations.CreateModel(
            name='Cdtrack',
            fields=[
                ('trackid', models.BigIntegerField(serialize=False, primary_key=True)),
                ('cdid', models.BigIntegerField()),
                ('tracknum', models.BigIntegerField()),
                ('tracktitle', models.CharField(max_length=200, null=True, blank=True)),
                ('trackartist', models.CharField(max_length=200, null=True, blank=True)),
                ('tracklength', models.BigIntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'cdtrack',
            },
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('show', models.CharField(max_length=200)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='PlaylistEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('artist', models.CharField(max_length=200, null=True, blank=True)),
                ('album', models.CharField(max_length=200, null=True, blank=True)),
                ('title', models.CharField(max_length=200, null=True, blank=True)),
                ('duration', models.DurationField()),
                ('local', models.BooleanField()),
                ('female', models.BooleanField()),
                ('newRelease', models.BooleanField()),
                ('catalogueEntry', models.ForeignKey(to='playlist.Cdtrack')),
            ],
        ),
    ]
