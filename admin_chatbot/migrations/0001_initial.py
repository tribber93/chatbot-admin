# Generated by Django 5.0.3 on 2024-04-04 17:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_celery_results', '0011_taskresult_periodic_task_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(default='NULL', max_length=255, unique=True)),
                ('file_path', models.FileField(default='NULL', upload_to='documents/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('count_retrieved', models.IntegerField(default=0)),
                ('task_result', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_celery_results.taskresult')),
            ],
        ),
    ]
