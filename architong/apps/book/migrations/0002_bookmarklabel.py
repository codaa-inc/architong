# Generated by Django 3.2.3 on 2021-07-13 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookmarkLabel',
            fields=[
                ('label_id', models.AutoField(primary_key=True, serialize=False)),
                ('label_name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'bookmark_label',
                'managed': False,
            },
        ),
    ]
