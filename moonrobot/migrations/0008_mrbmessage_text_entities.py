# Generated by Django 3.2.8 on 2021-10-14 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moonrobot', '0007_auto_20211011_1914'),
    ]

    operations = [
        migrations.AddField(
            model_name='mrbmessage',
            name='text_entities',
            field=models.JSONField(blank=True, null=True),
        ),
    ]