# Generated by Django 4.2 on 2023-04-30 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0006_team_tokens_used'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='public',
        ),
        migrations.AddField(
            model_name='team',
            name='private',
            field=models.BooleanField(default=False),
        ),
    ]
