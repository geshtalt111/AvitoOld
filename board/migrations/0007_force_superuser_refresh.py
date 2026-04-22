import os

from django.db import migrations
from django.contrib.auth.hashers import make_password


def force_superuser_refresh(apps, schema_editor):
    if os.environ.get("AUTO_CREATE_SUPERUSER", "false").lower() != "true":
        return

    User = apps.get_model("auth", "User")
    username = os.environ.get("AUTO_CREATE_SUPERUSER_USERNAME", "admin")
    email = os.environ.get("AUTO_CREATE_SUPERUSER_EMAIL", "admin@example.com")
    password = os.environ.get("AUTO_CREATE_SUPERUSER_PASSWORD", "admin123456")

    user, _created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "is_staff": True,
            "is_superuser": True,
        },
    )

    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.password = make_password(password)
    user.save()


class Migration(migrations.Migration):
    dependencies = [
        ("board", "0006_ensure_superuser"),
    ]

    operations = [
        migrations.RunPython(force_superuser_refresh, migrations.RunPython.noop),
    ]
