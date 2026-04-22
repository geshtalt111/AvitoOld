import os

from django.db import migrations


def ensure_superuser(apps, schema_editor):
    User = apps.get_model("auth", "User")

    username = os.environ.get("AUTO_CREATE_SUPERUSER_USERNAME", "admin")
    email = os.environ.get("AUTO_CREATE_SUPERUSER_EMAIL", "admin@example.com")
    password = os.environ.get("AUTO_CREATE_SUPERUSER_PASSWORD", "admin123456")

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "is_staff": True,
            "is_superuser": True,
        },
    )

    if not created:
        user.email = email
        user.is_staff = True
        user.is_superuser = True

    user.set_password(password)
    user.save()


class Migration(migrations.Migration):

    dependencies = [
        ("board", "0005_create_superuser"),
    ]

    operations = [
        migrations.RunPython(ensure_superuser, migrations.RunPython.noop),
    ]
