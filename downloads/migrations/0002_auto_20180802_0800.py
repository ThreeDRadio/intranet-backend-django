# Generated by Django 2.0.7 on 2018-08-02 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('downloads', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downloadlink',
            name='path',
            field=models.FilePathField(path='/Users/Michael/test/', recursive=True),
        ),
    ]
