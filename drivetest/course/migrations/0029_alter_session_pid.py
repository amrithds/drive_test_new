# Generated by Django 4.2.11 on 2024-05-16 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0028_alter_sensorfeed_s0_alter_sensorfeed_s1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='pid',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
