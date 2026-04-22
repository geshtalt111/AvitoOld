from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .forms import UserLoginForm
from . import views


urlpatterns = [
    path("", views.listing_list, name="listing_list"),
    path("assistant/", views.assistant_page, name="assistant_page"),
    path("assistant/ask/", views.assistant_ask, name="assistant_ask"),
    path("assistant/clear/", views.assistant_clear, name="assistant_clear"),
    path("register/", views.register_view, name="register"),
    path(
        "login/",
        LoginView.as_view(template_name="login.html", authentication_form=UserLoginForm),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("listing/create/", views.create_listing, name="listing_create"),
    path("listing/<int:pk>/", views.listing_detail, name="listing_detail"),
    path("listing/<int:pk>/edit/", views.edit_listing, name="listing_edit"),
    path("listing/<int:pk>/delete/", views.delete_listing, name="listing_delete"),
    path("listing/<int:pk>/close/", views.close_listing, name="listing_close"),
    path("listing/<int:pk>/deal/", views.create_deal, name="create_deal"),
    path("profile/", views.profile_view, name="profile"),
    path("my-listings/", views.my_listings, name="my_listings"),
    path("deals/", views.deal_list, name="deal_list"),
    path("deal/<int:pk>/chat/", views.deal_chat, name="deal_chat"),
    path("deal/<int:pk>/review/", views.create_review, name="create_review"),
]
