# Generated by Django 2.0.7 on 2018-08-02 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0007_auto_20160628_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='release',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
