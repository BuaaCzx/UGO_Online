# Generated by Django 5.1.2 on 2024-11-07 12:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0003_invitationcode"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invitationcode",
            name="code",
            field=models.CharField(max_length=16, unique=True),
        ),
    ]
