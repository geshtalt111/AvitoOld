from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_profiles_for_existing_users(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL.split(".")[0], settings.AUTH_USER_MODEL.split(".")[1])
    Profile = apps.get_model("board", "Profile")

    for user in User.objects.all():
        Profile.objects.get_or_create(user=user)


class Migration(migrations.Migration):
    dependencies = [
        ("board", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="image_1",
            field=models.ImageField(blank=True, null=True, upload_to="listings/", verbose_name="Фото 1"),
        ),
        migrations.AddField(
            model_name="listing",
            name="image_2",
            field=models.ImageField(blank=True, null=True, upload_to="listings/", verbose_name="Фото 2"),
        ),
        migrations.AddField(
            model_name="listing",
            name="image_3",
            field=models.ImageField(blank=True, null=True, upload_to="listings/", verbose_name="Фото 3"),
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("display_name", models.CharField(blank=True, max_length=100, verbose_name="Никнейм")),
                ("avatar", models.ImageField(blank=True, null=True, upload_to="avatars/", verbose_name="Аватар")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Профиль",
                "verbose_name_plural": "Профили",
            },
        ),
        migrations.RunPython(create_profiles_for_existing_users, migrations.RunPython.noop),
    ]
