# Generated by Django 2.0.7 on 2019-08-09 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporters', '0005_auto_20190809_0329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supporter',
            name='state',
            field=models.CharField(default='SA', max_length=200, null=True),
        ),
    ]
