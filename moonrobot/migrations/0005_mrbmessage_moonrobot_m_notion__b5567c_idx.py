# Generated by Django 3.2.8 on 2021-10-30 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moonrobot', '0004_auto_20211030_1200'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='mrbmessage',
            index=models.Index(fields=['notion_synced', 'sent_timestamp'], name='moonrobot_m_notion__b5567c_idx'),
        ),
    ]