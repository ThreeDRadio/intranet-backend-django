# Generated by Django 2.0.7 on 2019-08-09 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporters', '0012_transaction_transaction_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='expires_at',
            field=models.DateTimeField(default='2019-01-01'),
            preserve_default=False,
        ),
    ]