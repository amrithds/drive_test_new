# Generated by Django 4.2.11 on 2024-07-18 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0038_task_negation_task_flag'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='negation_task_flag',
            new_name='all_success_value_flag',
        ),
    ]