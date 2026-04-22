from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import (
    AssistantMessageForm,
    CloseListingForm,
    DealMessageForm,
    ListingForm,
    ProfileForm,
    ReviewForm,
    UserRegisterForm,
)
from .models import Category, Deal, Listing, Profile, Review
from .services import (
    PhoneAssistantConfigurationError,
    PhoneAssistantError,
    ask_phone_assistant,
)


ASSISTANT_SESSION_KEY = "phone_helper_messages"
ASSISTANT_MAX_MESSAGES = 10


def get_filtered_listings(request):
    listings = Listing.objects.select_related("category", "author__profile").filter(
        is_active=True,
        is_sold=False,
    )
    search_query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "").strip()

    if search_query:
        listings = listings.filter(title__icontains=search_query)

    if selected_category:
        listings = listings.filter(category_id=selected_category)

    return listings, search_query, selected_category


def get_conversations_for_queryset(queryset):
    return queryset.select_related(
        "listing",
        "buyer__profile",
        "seller__profile",
    ).annotate(
        message_count=Count("messages", distinct=True),
        last_message_time=Max("messages__created_at"),
    ).order_by("-last_message_time", "-created_at")


def get_assistant_history(request):
    raw_history = request.session.get(ASSISTANT_SESSION_KEY, [])
    history = []

    for item in raw_history:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            history.append({"role": role, "content": content})

    return history[-ASSISTANT_MAX_MESSAGES:]


def save_assistant_history(request, history):
    request.session[ASSISTANT_SESSION_KEY] = history[-ASSISTANT_MAX_MESSAGES:]
    request.session.modified = True


def build_assistant_context(request, form=None):
    return {
        "assistant_messages": get_assistant_history(request),
        "assistant_form": form or AssistantMessageForm(),
        "assistant_available": bool(settings.AI_API_KEY),
        "assistant_model": settings.AI_MODEL,
        "assistant_status_visible": request.user.is_staff,
    }


def register_view(request):
    if request.user.is_authenticated:
        return redirect("listing_list")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Регистрация прошла успешно. Теперь войдите в систему.")
            return redirect("login")
    else:
        form = UserRegisterForm()

    return render(request, "register.html", {"form": form})


def listing_list(request):
    listings, search_query, selected_category = get_filtered_listings(request)
    categories = Category.objects.all()
    context = {
        "listings": listings,
        "categories": categories,
        "search_query": search_query,
        "selected_category": selected_category,
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string("includes/listing_cards.html", context, request=request)
        return HttpResponse(html)

    return render(request, "list.html", context)


def assistant_page(request):
    if request.method == "POST":
        form = AssistantMessageForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data["message"].strip()
            history = get_assistant_history(request)
            request_payload = [*history, {"role": "user", "content": user_message}]

            try:
                assistant_reply, _model_used = ask_phone_assistant(request_payload)
            except PhoneAssistantConfigurationError as exc:
                messages.error(request, str(exc))
                context = build_assistant_context(request, form=form)
                return render(request, "assistant.html", context)
            except PhoneAssistantError as exc:
                messages.error(request, str(exc))
                context = build_assistant_context(request, form=form)
                return render(request, "assistant.html", context)

            save_assistant_history(
                request,
                [
                    *request_payload,
                    {"role": "assistant", "content": assistant_reply},
                ],
            )
            return redirect("assistant_page")

        context = build_assistant_context(request, form=form)
        return render(request, "assistant.html", context)

    return render(request, "assistant.html", build_assistant_context(request))


@require_POST
def assistant_ask(request):
    form = AssistantMessageForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": "Введите вопрос."}, status=400)

    user_message = form.cleaned_data["message"].strip()
    history = get_assistant_history(request)
    request_payload = [*history, {"role": "user", "content": user_message}]

    try:
        assistant_reply, model_used = ask_phone_assistant(request_payload)
    except PhoneAssistantConfigurationError as exc:
        return JsonResponse({"error": str(exc)}, status=503)
    except PhoneAssistantError as exc:
        return JsonResponse({"error": str(exc)}, status=502)

    updated_history = [
        *request_payload,
        {"role": "assistant", "content": assistant_reply},
    ]
    save_assistant_history(request, updated_history)

    return JsonResponse(
        {
            "reply": assistant_reply,
            "messages": updated_history[-ASSISTANT_MAX_MESSAGES:],
            "model": model_used,
        }
    )


@require_POST
def assistant_clear(request):
    save_assistant_history(request, [])
    return JsonResponse({"ok": True})


def listing_detail(request, pk):
    listing = get_object_or_404(Listing.objects.select_related("category", "author__profile"), pk=pk)
    completed_deal = listing.deals.select_related("buyer__profile", "seller__profile").filter(
        is_completed=True
    ).first()
    reviews = (
        Review.objects.select_related("author__profile", "target_user__profile").filter(deal=completed_deal)
        if completed_deal
        else Review.objects.none()
    )

    seller_conversations = Deal.objects.none()
    existing_conversation = None
    existing_review = None
    can_review = False
    can_close_listing = False

    if request.user.is_authenticated:
        if request.user == listing.author:
            seller_conversations = get_conversations_for_queryset(listing.deals.all())
            can_close_listing = not listing.is_sold
        else:
            existing_conversation = listing.deals.select_related(
                "buyer__profile",
                "seller__profile",
            ).filter(buyer=request.user).first()

        if completed_deal:
            existing_review = Review.objects.filter(deal=completed_deal, author=request.user).first()
            is_participant = request.user.id in {completed_deal.buyer_id, completed_deal.seller_id}
            can_review = is_participant and existing_review is None

    context = {
        "listing": listing,
        "completed_deal": completed_deal,
        "reviews": reviews,
        "seller_conversations": seller_conversations,
        "existing_conversation": existing_conversation,
        "existing_review": existing_review,
        "can_review": can_review,
        "can_close_listing": can_close_listing,
    }
    return render(request, "detail.html", context)


@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.author = request.user
            listing.save()
            messages.success(request, "Объявление успешно создано.")
            return redirect("listing_detail", pk=listing.pk)
    else:
        form = ListingForm()

    return render(
        request,
        "form.html",
        {
            "form": form,
            "title": "Новое объявление",
            "submit_text": "Сохранить",
            "cancel_url": reverse("listing_list"),
        },
    )


@login_required
def edit_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if listing.author != request.user:
        messages.error(request, "Редактировать объявление может только автор.")
        return redirect("listing_detail", pk=listing.pk)

    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, "Объявление обновлено.")
            return redirect("listing_detail", pk=listing.pk)
    else:
        form = ListingForm(instance=listing)

    return render(
        request,
        "form.html",
        {
            "form": form,
            "title": "Редактирование объявления",
            "submit_text": "Обновить",
            "cancel_url": reverse("listing_detail", args=[listing.pk]),
        },
    )


@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if listing.author != request.user:
        messages.error(request, "Удалять объявление может только автор.")
        return redirect("listing_detail", pk=listing.pk)

    if Deal.objects.filter(listing=listing).exists():
        messages.error(request, "Нельзя удалить объявление, по которому уже есть переписка.")
        return redirect("listing_detail", pk=listing.pk)

    if request.method == "POST":
        listing.delete()
        messages.success(request, "Объявление удалено.")
        return redirect("listing_list")

    return render(
        request,
        "delete.html",
        {
            "listing": listing,
            "cancel_url": reverse("listing_detail", args=[listing.pk]),
        },
    )


@login_required
def close_listing(request, pk):
    listing = get_object_or_404(Listing.objects.prefetch_related("deals"), pk=pk)

    if listing.author != request.user:
        messages.error(request, "Закрыть объявление может только автор.")
        return redirect("listing_detail", pk=listing.pk)

    if listing.is_sold:
        messages.info(request, "Объявление уже закрыто.")
        return redirect("listing_detail", pk=listing.pk)

    if request.method == "POST":
        form = CloseListingForm(request.POST, listing=listing)
        if form.is_valid():
            sold_price = form.cleaned_data["sold_price"]
            winning_deal = form.cleaned_data["winning_deal"]

            listing.sold_price = sold_price
            listing.is_sold = True
            listing.is_active = False
            listing.save(update_fields=["sold_price", "is_sold", "is_active"])

            listing.deals.update(is_completed=False)
            if winning_deal:
                winning_deal.is_completed = True
                winning_deal.save(update_fields=["is_completed"])

            messages.success(request, "Объявление закрыто и отправлено в архив.")
            return redirect("my_listings")
    else:
        form = CloseListingForm(listing=listing)

    return render(
        request,
        "form.html",
        {
            "form": form,
            "title": "Закрыть объявление",
            "submit_text": "Закрыть объявление",
            "cancel_url": reverse("listing_detail", args=[listing.pk]),
        },
    )


@login_required
@require_POST
def create_deal(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if listing.author == request.user:
        messages.error(request, "Нельзя писать самому себе.")
        return redirect("listing_detail", pk=listing.pk)

    if listing.is_sold or not listing.is_active:
        messages.error(request, "Это объявление уже закрыто.")
        return redirect("listing_detail", pk=listing.pk)

    deal = Deal.objects.filter(listing=listing, buyer=request.user).first()
    if deal:
        messages.info(request, "У вас уже есть переписка по этому объявлению.")
        return redirect("deal_chat", pk=deal.pk)

    deal = Deal.objects.create(
        listing=listing,
        buyer=request.user,
        seller=listing.author,
    )
    messages.success(request, "Переписка создана. Теперь можно писать продавцу.")
    return redirect("deal_chat", pk=deal.pk)


@login_required
def deal_list(request):
    conversations = get_conversations_for_queryset(
        Deal.objects.filter(Q(buyer=request.user) | Q(seller=request.user))
    )
    reviewed_deal_ids = list(
        Review.objects.filter(author=request.user, deal__in=conversations).values_list("deal_id", flat=True)
    )
    return render(
        request,
        "deals.html",
        {
            "conversations": conversations,
            "reviewed_deal_ids": reviewed_deal_ids,
        },
    )


@login_required
def my_listings(request):
    active_listings = request.user.listings.select_related("category").annotate(
        conversation_count=Count("deals", distinct=True)
    ).filter(is_sold=False)
    archived_listings = request.user.listings.select_related("category").annotate(
        conversation_count=Count("deals", distinct=True)
    ).filter(is_sold=True)

    return render(
        request,
        "my_listings.html",
        {
            "active_listings": active_listings,
            "archived_listings": archived_listings,
        },
    )


@login_required
def deal_chat(request, pk):
    deal = get_object_or_404(
        Deal.objects.select_related("listing", "buyer__profile", "seller__profile"),
        pk=pk,
    )

    if request.user.id not in {deal.buyer_id, deal.seller_id}:
        messages.error(request, "Доступ к сообщениям есть только у участников переписки.")
        return redirect("listing_detail", pk=deal.listing.pk)

    can_write_messages = not deal.listing.is_sold

    if request.method == "POST":
        if not can_write_messages:
            messages.info(request, "Объявление уже закрыто. Новые сообщения отправлять нельзя.")
            return redirect("deal_chat", pk=deal.pk)

        form = DealMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.deal = deal
            message.author = request.user
            message.save()
            return redirect("deal_chat", pk=deal.pk)
    else:
        form = DealMessageForm()

    chat_messages = deal.messages.select_related("author__profile")
    if request.user == deal.seller:
        sidebar_conversations = get_conversations_for_queryset(
            Deal.objects.filter(listing=deal.listing)
        )
    else:
        sidebar_conversations = get_conversations_for_queryset(
            Deal.objects.filter(buyer=request.user)
        )

    existing_review = Review.objects.filter(deal=deal, author=request.user).first()
    can_review = deal.is_completed and existing_review is None

    return render(
        request,
        "deal_chat.html",
        {
            "deal": deal,
            "chat_messages": chat_messages,
            "form": form,
            "sidebar_conversations": sidebar_conversations,
            "can_write_messages": can_write_messages,
            "can_close_listing": request.user == deal.seller and not deal.listing.is_sold,
            "existing_review": existing_review,
            "can_review": can_review,
        },
    )


@login_required
def create_review(request, pk):
    deal = get_object_or_404(
        Deal.objects.select_related("listing", "buyer__profile", "seller__profile"),
        pk=pk,
    )

    if not deal.is_completed:
        messages.error(request, "Отзыв можно оставить только после завершения продажи.")
        return redirect("listing_detail", pk=deal.listing.pk)

    if request.user.id not in {deal.buyer_id, deal.seller_id}:
        messages.error(request, "Только участник продажи может оставить отзыв.")
        return redirect("listing_detail", pk=deal.listing.pk)

    if Review.objects.filter(deal=deal, author=request.user).exists():
        messages.error(request, "Вы уже оставили отзыв по этой продаже.")
        return redirect("listing_detail", pk=deal.listing.pk)

    target_user = deal.seller if request.user == deal.buyer else deal.buyer

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.deal = deal
            review.author = request.user
            review.target_user = target_user
            review.save()
            messages.success(request, "Отзыв сохранен.")
            return redirect("listing_detail", pk=deal.listing.pk)
    else:
        form = ReviewForm()

    return render(
        request,
        "form.html",
        {
            "form": form,
            "title": f"Отзыв для пользователя {target_user.username}",
            "submit_text": "Оставить отзыв",
            "cancel_url": reverse("listing_detail", args=[deal.listing.pk]),
        },
    )


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлен.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "profile.html",
        {
            "form": form,
            "profile": profile,
        },
    )
