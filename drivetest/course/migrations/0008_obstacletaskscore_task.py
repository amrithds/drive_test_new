# Generated by Django 4.2.11 on 2024-05-03 08:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0007_obstaclesessiontracker'),
    ]

    operations = [
        migrations.AddField(
            model_name='obstacletaskscore',
            name='task',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='course.task'),
        ),
    ]
