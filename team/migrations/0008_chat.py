# Generated by Django 4.2 on 2023-05-01 18:56

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0007_remove_team_public_team_private'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('log', models.TextField(blank=True, null=True)),
                ('human_roles', models.ManyToManyField(to='team.role')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.team')),
            ],
        ),
    ]
