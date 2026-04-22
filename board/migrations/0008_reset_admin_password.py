from django.contrib.auth.hashers import make_password
from django.db import migrations


def reset_admin_password(apps, schema_editor):
    User = apps.get_model("auth", "User")

    username = "admin"
    email = "adminchik@gmail.com"
    password = "119928"

    user, _created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "is_staff": True,
            "is_superuser": True,
            "password": make_password(password),
        },
    )

    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.password = make_password(password)
    user.save()


class Migration(migrations.Migration):
    dependencies = [
        ("board", "0007_force_superuser_refresh"),
    ]

    operations = [
        migrations.RunPython(reset_admin_password, migrations.RunPython.noop),
    ]
