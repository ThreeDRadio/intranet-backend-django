# Generated by Django 2.0.7 on 2019-08-12 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporters', '0014_auto_20190809_0804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supporter',
            name='address1',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='supporter',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='supporter',
            name='first_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='supporter',
            name='last_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='supporter',
            name='postcode',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='supporter',
            name='town',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='expires_at',
            field=models.DateField(),
        ),
    ]