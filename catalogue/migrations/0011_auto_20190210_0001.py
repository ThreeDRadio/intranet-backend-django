# Generated by Django 2.0.7 on 2019-02-10 00:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0010_auto_20190126_1141'),
    ]

    operations = [
        migrations.RenameField(
            model_name='track',
            old_name='needsEncoding',
            new_name='needsencoding',
        ),
    ]