# Generated by Django 4.2.11 on 2024-05-02 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskmetrics',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='taskmetrics',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
