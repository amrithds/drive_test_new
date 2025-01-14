# Generated by Django 4.2.11 on 2024-05-02 08:56

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('unique_ref_id', models.CharField(default='superuser', max_length=100)),
                ('rank', models.CharField(blank=True, choices=[('Rect', 'Rect'), ('SEP', 'SEP'), ('L Nk', 'L Nk'), ('Nk', 'Nk'), ('L Hav', 'L Hav'), ('Hav', 'Hav'), ('Nb Sub', 'Nb Sub'), ('Sub', 'Sub'), ('Sub Maj', 'Sub Maj'), ('Lt', 'Lt'), ('Maj', 'Maj'), ('Capt', 'Capt'), ('Lt Col', 'Lt Col')], default='Rect', max_length=50, null=True)),
                ('unit', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('type', models.IntegerField(choices=[(1, 'Driver'), (2, 'Instructor')], default=2)),
            ],
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Obstacle',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('is_mandatory', models.BooleanField(default=False)),
                ('order', models.IntegerField()),
                ('start_rf_id', models.CharField(max_length=20)),
                ('end_rf_id', models.CharField(blank=True, max_length=20)),
                ('audio_file', models.FileField(blank=True, upload_to='uploads/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('sensor_id', models.IntegerField()),
                ('category', models.IntegerField(choices=[(0, 'Boolean'), (1, 'Parking'), (2, 'Speed'), (3, 'Turning')], default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='course.course')),
                ('trainee', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='trinee_user_set', to=settings.AUTH_USER_MODEL)),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='trainer_user_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaskMetrics',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.CharField(max_length=1024)),
                ('message', models.CharField(default='', max_length=1024)),
                ('created_at', models.DateField()),
                ('updated_at', models.DateField()),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.task')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.IntegerField(choices=[(0, 'Ideal'), (1, 'In progress'), (2, 'Completed')], default=0)),
                ('mode', models.IntegerField(choices=[(0, 'Evaluate'), (1, 'Test')], default=0)),
                ('course', models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='course.course')),
                ('trainee_no', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='trainee_session_set', to=settings.AUTH_USER_MODEL)),
                ('trainer_no', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='trainer_session_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SensorFeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('s1', models.CharField(max_length=10)),
                ('s2', models.CharField(max_length=10)),
                ('s3', models.CharField(max_length=10)),
                ('s4', models.CharField(max_length=10)),
                ('s5', models.CharField(max_length=10)),
                ('s6', models.CharField(max_length=10)),
                ('s7', models.CharField(max_length=10)),
                ('s8', models.CharField(max_length=10)),
                ('s9', models.CharField(max_length=10)),
                ('s10', models.CharField(max_length=10)),
                ('s11', models.CharField(max_length=10)),
                ('s12', models.CharField(max_length=10)),
                ('s13', models.CharField(max_length=10)),
                ('s14', models.CharField(max_length=10)),
                ('s15', models.CharField(max_length=10)),
                ('s16', models.CharField(max_length=10)),
                ('s17', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('Obstacle', models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='course.obstacle')),
            ],
        ),
        migrations.CreateModel(
            name='ObstacleTaskScore',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('score', models.IntegerField(default=0)),
                ('is_mandatory', models.BooleanField(default=False)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('order', models.IntegerField(blank=True)),
                ('obstacle_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.obstacle')),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.task')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='obstacle',
            name='track_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.track'),
        ),
        migrations.AddField(
            model_name='user',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='course.course'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together={('course', 'unique_ref_id')},
        ),
    ]
