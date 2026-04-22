from django.contrib import admin

from .models import Category, Deal, DealMessage, Listing, Profile, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "author",
        "price",
        "sold_price",
        "created_at",
        "is_active",
        "is_sold",
    )
    list_filter = ("category", "is_active", "is_sold", "created_at")
    search_fields = ("title", "description", "author__username")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "display_name")
    search_fields = ("user__username", "display_name")


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "buyer", "seller", "created_at", "is_completed")
    list_filter = ("is_completed", "created_at")
    search_fields = ("listing__title", "buyer__username", "seller__username")


@admin.register(DealMessage)
class DealMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "deal", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("deal__listing__title", "author__username", "text")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "deal", "author", "target_user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("author__username", "target_user__username", "text")
