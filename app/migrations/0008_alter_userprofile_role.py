# Generated by Django 5.2 on 2025-05-09 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_adminusers_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('superadmin', 'SuperAdmin'), ('admin', 'Admin'), ('user', 'User')], max_length=20),
        ),
    ]
