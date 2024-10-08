# Generated by Django 5.0.3 on 2024-05-06 19:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, unique=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['username', 'first_name', 'last_name'],
                'indexes': [models.Index(fields=['username'], name='movielist_u_usernam_ed5510_idx')],
            },
        ),
        migrations.CreateModel(
            name='ListEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movie_id', models.CharField(max_length=255)),
                ('rating', models.DecimalField(decimal_places=1, max_digits=3)),
                ('date_watched', models.DateField(null=True)),
                ('comments', models.TextField(null=True)),
                ('poster_url', models.TextField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movielist.user')),
            ],
            options={
                'indexes': [models.Index(fields=['user', 'movie_id'], name='movielist_l_user_id_9030a5_idx')],
            },
        ),
    ]
