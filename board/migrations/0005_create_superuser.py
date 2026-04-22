import os

from django.db import migrations


def create_superuser(apps, schema_editor):
    enabled = os.environ.get("AUTO_CREATE_SUPERUSER", "false").lower() == "true"
    if not enabled:
        return

    User = apps.get_model("auth", "User")
    username = os.environ.get("AUTO_CREATE_SUPERUSER_USERNAME", "admin")
    email = os.environ.get("AUTO_CREATE_SUPERUSER_EMAIL", "admin@example.com")
    password = os.environ.get("AUTO_CREATE_SUPERUSER_PASSWORD", "admin123456")

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("board", "0004_avito_style_conversations"),
    ]

    operations = [
        migrations.RunPython(create_superuser, migrations.RunPython.noop),
    ]
