# Generated by Django 2.2.11 on 2020-04-03 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sync_server', '0003_auto_20200402_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appregister',
            name='secret',
            field=models.CharField(max_length=256),
        ),
    ]
