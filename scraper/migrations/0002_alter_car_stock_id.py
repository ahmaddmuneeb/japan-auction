# Generated by Django 5.1.3 on 2024-11-26 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='stock_id',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
