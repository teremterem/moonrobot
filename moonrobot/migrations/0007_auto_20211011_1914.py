# Generated by Django 3.2.8 on 2021-10-11 19:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moonrobot', '0006_mrbmessage_from_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mrbchat',
            old_name='notion_synched',
            new_name='notion_synced',
        ),
        migrations.RenameField(
            model_name='mrbmessage',
            old_name='notion_synched',
            new_name='notion_synced',
        ),
        migrations.RenameField(
            model_name='mrbuser',
            old_name='notion_synched',
            new_name='notion_synced',
        ),
    ]