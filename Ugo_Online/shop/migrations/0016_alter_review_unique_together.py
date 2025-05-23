# Generated by Django 5.1.2 on 2024-12-05 07:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0005_alter_order_status"),
        ("shop", "0015_alter_sellershop_shop"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="review",
            unique_together={("user", "order")},
        ),
    ]
