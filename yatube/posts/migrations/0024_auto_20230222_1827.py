# Generated by Django 2.2.16 on 2023-02-22 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0023_auto_20230222_1615'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-created',), 'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
    ]