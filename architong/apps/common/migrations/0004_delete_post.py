# Generated by Django 3.2 on 2021-04-30 14:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_alter_post_options'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Post',
        ),
    ]
