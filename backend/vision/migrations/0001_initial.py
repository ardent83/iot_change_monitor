# Generated by Django 5.2.3 on 2025-06-26 04:09

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeDetectionLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image1', models.ImageField(upload_to='change_detection/', verbose_name='First Image')),
                ('image2', models.ImageField(upload_to='change_detection/', verbose_name='Second Image')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Change Description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creation Time')),
            ],
            options={
                'verbose_name': 'Change Detection Log',
                'verbose_name_plural': 'Change Detection Logs',
                'ordering': ['-created_at'],
            },
        ),
    ]
