# Generated by Django 2.2.4 on 2019-10-11 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0012_auto_20190812_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='release',
            name='ghoul_approved',
            field=models.BooleanField(blank=True, default=True),
        ),
    ]
