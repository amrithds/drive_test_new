# Generated by Django 4.2.11 on 2024-05-09 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0017_alter_taskmetric_range_1_alter_taskmetric_range_2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskmetric',
            name='value',
            field=models.CharField(blank=True, default=None, max_length=1024),
        ),
    ]
