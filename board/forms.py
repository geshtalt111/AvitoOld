from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import DealMessage, Listing, Profile, Review


class DealChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        has_profile = hasattr(obj.buyer, "profile") and obj.buyer.profile.display_name
        buyer_name = obj.buyer.profile.display_name if has_profile else obj.buyer.username
        return f"{buyer_name} - {obj.created_at:%d.%m.%Y %H:%M}"


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")
        labels = {
            "username": "Имя пользователя",
            "password1": "Пароль",
            "password2": "Подтверждение пароля",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            "category",
            "title",
            "description",
            "price",
            "is_active",
            "image_1",
            "image_2",
            "image_3",
        ]
        labels = {
            "title": "Название объявления",
            "description": "Описание",
            "price": "Цена",
            "is_active": "Показывать на сайте",
            "image_1": "Фотография 1",
            "image_2": "Фотография 2",
            "image_3": "Фотография 3",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "price": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        labels = {
            "rating": "Оценка",
            "text": "Текст отзыва",
        }
        widgets = {
            "rating": forms.Select(choices=[(i, i) for i in range(1, 6)]),
            "text": forms.Textarea(attrs={"rows": 5}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["display_name", "avatar"]
        labels = {
            "display_name": "Никнейм",
            "avatar": "Аватар",
        }


class DealMessageForm(forms.ModelForm):
    class Meta:
        model = DealMessage
        fields = ["text"]
        labels = {
            "text": "Сообщение",
        }
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Напишите сообщение...",
                }
            ),
        }


class AssistantMessageForm(forms.Form):
    message = forms.CharField(
        label="Вопрос",
        max_length=1200,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Задайте любой вопрос...",
            }
        ),
    )


class CloseListingForm(forms.Form):
    sold_price = forms.DecimalField(
        label="Финальная цена продажи",
        min_value=0,
        decimal_places=2,
        max_digits=10,
    )
    winning_deal = DealChoiceField(
        label="Кому продали",
        queryset=None,
        required=False,
        empty_label="Продал не через этот сайт",
    )

    def __init__(self, *args, **kwargs):
        listing = kwargs.pop("listing")
        super().__init__(*args, **kwargs)
        self.fields["winning_deal"].queryset = listing.deals.select_related("buyer__profile").order_by("-created_at")
