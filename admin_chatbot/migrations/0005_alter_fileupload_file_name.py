# Generated by Django 5.0.3 on 2024-03-06 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_chatbot', '0004_alter_fileupload_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='file_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
