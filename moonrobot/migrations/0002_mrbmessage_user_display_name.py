# Generated by Django 3.2.8 on 2021-10-28 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moonrobot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mrbmessage',
            name='user_display_name',
            field=models.TextField(blank=True, null=True),
        ),
    ]
