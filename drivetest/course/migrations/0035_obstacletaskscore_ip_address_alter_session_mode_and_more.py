# Generated by Django 4.2.11 on 2024-06-08 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0034_delete_sensorfeed'),
    ]

    operations = [
        migrations.AddField(
            model_name='obstacletaskscore',
            name='ip_address',
            field=models.CharField(default=0, max_length=100),
        ),
        migrations.AlterField(
            model_name='session',
            name='mode',
            field=models.IntegerField(choices=[(0, 'Evaluate'), (1, 'Training')], default=0),
        ),
        migrations.AlterField(
            model_name='task',
            name='category',
            field=models.IntegerField(choices=[(0, 'Boolean'), (1, 'Parking'), (9, 'Reverse Parking'), (4, 'Left Parking'), (5, 'Right Parking'), (2, 'Speed'), (3, 'Turning'), (6, 'Left Turning'), (7, 'Right Turning'), (8, 'Zig-zag Turning')], default=0),
        ),
    ]
