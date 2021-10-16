# Generated by Django 3.2.8 on 2021-10-16 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moonrobot', '0008_mrbmessage_text_entities'),
    ]

    operations = [
        migrations.CreateModel(
            name='MrbBot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notion_synced', models.BooleanField(db_index=True, default=False)),
                ('notion_id', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]