from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def get_user_display_name(user):
    if hasattr(user, "profile") and user.profile.display_name:
        return user.profile.display_name
    return user.username


class Category(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Listing(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="listings",
        verbose_name="Категория",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
        verbose_name="Автор",
    )
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание")
    price = models.DecimalField(
        "Цена",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    is_active = models.BooleanField("Показывать объявление", default=True)
    is_sold = models.BooleanField("Продано", default=False)
    sold_price = models.DecimalField(
        "Финальная цена продажи",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
    )
    image_1 = models.ImageField("Фото 1", upload_to="listings/", blank=True, null=True)
    image_2 = models.ImageField("Фото 2", upload_to="listings/", blank=True, null=True)
    image_3 = models.ImageField("Фото 3", upload_to="listings/", blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"

    def __str__(self):
        return self.title

    def get_images(self):
        return [image for image in [self.image_1, self.image_2, self.image_3] if image]

    def author_name(self):
        return get_user_display_name(self.author)


class Deal(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="deals",
        verbose_name="Объявление",
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchases",
        verbose_name="Покупатель",
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sales",
        verbose_name="Продавец",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    is_completed = models.BooleanField("Сделка завершена", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Диалог"
        verbose_name_plural = "Диалоги"
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "buyer"],
                name="unique_dialog_for_listing_buyer",
            )
        ]

    def __str__(self):
        return f"Диалог по объявлению: {self.listing.title}"

    def buyer_name(self):
        return get_user_display_name(self.buyer)

    def seller_name(self):
        return get_user_display_name(self.seller)

    def status_text(self):
        if self.is_completed:
            return "покупка завершена"
        if self.listing.is_sold:
            return "объявление закрыто"
        return "идет переписка"

    def can_chat(self):
        return not self.listing.is_sold


class DealMessage(models.Model):
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Диалог",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deal_messages",
        verbose_name="Автор",
    )
    text = models.TextField("Текст сообщения")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Сообщение в диалоге"
        verbose_name_plural = "Сообщения в диалогах"

    def __str__(self):
        return f"Сообщение от {self.author} по сделке {self.deal_id}"

    def author_name(self):
        return get_user_display_name(self.author)


class Review(models.Model):
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Диалог",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="written_reviews",
        verbose_name="Автор",
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_reviews",
        verbose_name="Кому оставлен отзыв",
    )
    rating = models.IntegerField(
        "Оценка",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    text = models.TextField("Текст отзыва")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=["deal", "author"],
                name="unique_review_author_per_deal",
            )
        ]

    def __str__(self):
        return f"Отзыв {self.author} -> {self.target_user}"

    def author_name(self):
        return get_user_display_name(self.author)

    def target_user_name(self):
        return get_user_display_name(self.target_user)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    display_name = models.CharField("Никнейм", max_length=100, blank=True)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True, null=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.display_name or self.user.username
