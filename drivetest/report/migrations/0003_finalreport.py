# Generated by Django 4.2.11 on 2024-05-10 07:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0020_session_pid'),
        ('report', '0002_alter_sessionreport_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('data', models.JSONField(default=None)),
                ('obstacle', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='course.obstacle')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]