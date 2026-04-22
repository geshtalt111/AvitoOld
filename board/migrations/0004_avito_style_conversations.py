import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("board", "0003_dealmessage_deal_is_accepted"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="sold_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Финальная цена продажи",
            ),
        ),
        migrations.AlterModelOptions(
            name="deal",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Диалог",
                "verbose_name_plural": "Диалоги",
            },
        ),
        migrations.AlterField(
            model_name="deal",
            name="listing",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="deals",
                to="board.listing",
                verbose_name="Объявление",
            ),
        ),
        migrations.RemoveField(
            model_name="deal",
            name="is_accepted",
        ),
        migrations.AddConstraint(
            model_name="deal",
            constraint=models.UniqueConstraint(
                fields=("listing", "buyer"),
                name="unique_dialog_for_listing_buyer",
            ),
        ),
    ]
