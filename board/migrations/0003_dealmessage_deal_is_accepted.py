from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def mark_existing_deals_as_accepted(apps, schema_editor):
    Deal = apps.get_model("board", "Deal")
    Deal.objects.all().update(is_accepted=True)


class Migration(migrations.Migration):
    dependencies = [
        ("board", "0002_profile_listing_images"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="deal",
            name="is_accepted",
            field=models.BooleanField(default=False, verbose_name="Продавец подтвердил сделку"),
        ),
        migrations.CreateModel(
            name="DealMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField(verbose_name="Текст сообщения")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deal_messages",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
                (
                    "deal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="board.deal",
                        verbose_name="Сделка",
                    ),
                ),
            ],
            options={
                "verbose_name": "Сообщение по сделке",
                "verbose_name_plural": "Сообщения по сделкам",
                "ordering": ["created_at"],
            },
        ),
        migrations.RunPython(mark_existing_deals_as_accepted, migrations.RunPython.noop),
    ]
