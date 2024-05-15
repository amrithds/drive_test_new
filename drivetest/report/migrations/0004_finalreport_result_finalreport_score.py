# Generated by Django 4.2.11 on 2024-05-15 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0003_finalreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='finalreport',
            name='result',
            field=models.IntegerField(choices=[(1, 'Pass'), (2, 'Fail')], default=1),
        ),
        migrations.AddField(
            model_name='finalreport',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]