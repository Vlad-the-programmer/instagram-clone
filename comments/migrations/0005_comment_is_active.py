# Generated by Django 5.0.4 on 2025-07-23 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0004_alter_comment_managers_alter_comment_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
