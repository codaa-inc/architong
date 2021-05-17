# Generated by Django 3.2 on 2021-05-17 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('comment_id', models.AutoField(primary_key=True, serialize=False)),
                ('page_id', models.IntegerField()),
                ('parent_id', models.IntegerField()),
                ('depth', models.IntegerField()),
                ('username', models.CharField(max_length=150)),
                ('content', models.TextField(blank=True, null=True)),
                ('rls_yn', models.CharField(blank=True, max_length=10, null=True)),
                ('reg_dt', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'db_table': 'comments',
                'managed': False,
            },
        ),
    ]
