# Generated by Django 4.2.11 on 2024-05-10 07:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0020_session_pid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='taskmetric',
            old_name='range_1',
            new_name='max_range',
        ),
        migrations.RenameField(
            model_name='taskmetric',
            old_name='range_2',
            new_name='min_range',
        ),
    ]
