from __future__ import annotations

import base64
import json
from copy import deepcopy
from functools import wraps
from io import BytesIO
from typing import Dict, List

from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from PIL import Image

from .models import Prompt, SubscriptionPlan

PLAN_DEFINITIONS: List[Dict[str, object]] = [
    {
        "name": "monthly",
        "display_name": "Monthly Discipline",
        "duration_label": "month",
        "description": "Entry-level access for guys who want to test the waters — but stay locked in.",
        "features": [
            "Daily Prompts & Guidance",
            "Full GPT-4 Chat Access",
            "Weekly Identity Reflection",
            "Community Chat Access",
        ],
        "tag": "Most Popular",
        "cta_paid": "Sign Up",
        "cta_demo": "Explore Plan",
        "demo_price_default": "€9 / month",
    },
    {
        "name": "quarterly",
        "display_name": "Quarterly Reset",
        "duration_label": "3 months",
        "description": "Best for guys who want change — and want to commit.",
        "features": [
            "Daily Prompts & Guidance",
            "Custom Vision-Building Plan",
            "Full GPT-4 Chat Access",
            "Weekly Identity Reflection",
            "Community Chat Access",
            "Monthly Personal Audit Templates",
            "Early Feature Access",
        ],
        "tag": None,
        "cta_paid": "Sign Up",
        "cta_demo": "Explore Plan",
        "demo_price_default": "€24 / 3 months",
    },
    {
        "name": "yearly",
        "display_name": "Yearly Reset",
        "duration_label": "year",
        "description": "Built for the serious. One-time investment, 12 months of no-excuses growth.",
        "features": [
            "Personalized Welcome Breakdown",
            "Daily Prompts & Guidance",
            "Mental Rebuild Guidebook",
            "Full GPT-4 Chat Access",
            "Community Chat Access",
            "Weekly Identity Reflection",
        ],
        "tag": None,
        "cta_paid": "Request Access",
        "cta_demo": "Explore Plan",
        "demo_price_default": "€79 / year",
    },
]


def maybe_login_required(view_func):
    if settings.ENABLE_AUTH:
        return login_required(view_func)

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return _wrapped


def _format_stripe_price(price_id: str) -> str:
    if not (settings.STRIPE_SECRET_KEY and price_id):
        return "Contact us"

    try:
        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY
        price = stripe.Price.retrieve(price_id)
        amount = price.get("unit_amount") or price.get("unit_amount_decimal")
        currency = price.get("currency", "").upper()
        if amount is None:
            return "Contact us"
        amount = float(amount) / 100
        return f"{amount:.2f} {currency}"
    except Exception:
        return "Contact us"


def build_plan_catalog() -> List[Dict[str, object]]:
    catalog: List[Dict[str, object]] = []
    for raw_plan in PLAN_DEFINITIONS:
        plan = deepcopy(raw_plan)
        plan_name = plan["name"]

        if settings.ENABLE_REAL_PAYMENTS:
            price_id = settings.STRIPE_PRICE_IDS.get(plan_name, "")
            plan["stripe_price_id"] = price_id
            plan["price_display"] = f"{_format_stripe_price(price_id)} / {plan['duration_label']}"
            plan["button_label"] = plan["cta_paid"]
        else:
            plan["stripe_price_id"] = ""
            plan["price_display"] = settings.DEMO_PLAN_PRICING.get(
                plan_name, plan["demo_price_default"]
            )
            plan["button_label"] = plan["cta_demo"]

        catalog.append(plan)
    return catalog


def index(request):
    plans = build_plan_catalog()
    return render(request, "index.html", {"plans": plans})


@maybe_login_required
def chatbot(request):
    if settings.ENABLE_REAL_PAYMENTS and settings.ENABLE_AUTH:
        try:
            subscription = SubscriptionPlan.objects.get(user=request.user)
            if subscription.expire_date and subscription.expire_date < now():
                messages.error(
                    request,
                    "Your subscription has expired. Please renew to access the chatbot.",
                )
                return redirect("index")
        except SubscriptionPlan.DoesNotExist:
            messages.error(request, "You need an active plan to access the chatbot.")
            return redirect("index")

    return render(request, "chatbot.html")


def sign(request):
    if not settings.ENABLE_AUTH:
        messages.info(request, "Sign-ups are disabled in the demo build.")
        return redirect("index")

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        terms_checked = request.POST.get("TC")

        if not all([first_name, last_name, email, password1, password2]):
            messages.error(request, "All fields are required.")
            return redirect("sign")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("sign")

        if not terms_checked:
            messages.error(request, "You must agree to the Terms and Conditions.")
            return redirect("sign")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("sign")

        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1,
        )
        user.save()
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect("login")

    return render(request, "signup.html")


def login(request):
    if not settings.ENABLE_AUTH:
        messages.info(request, "Authentication is disabled in demo mode.")
        return redirect("index")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful!")
            return redirect("index")

        messages.error(request, "Invalid email or password.")

    return render(request, "login.html")


def logout_view(request):
    if settings.ENABLE_AUTH:
        logout(request)
        storage = messages.get_messages(request)
        for _ in storage:
            pass
        messages.success(request, "Logout successful!")
        return redirect("login")

    return redirect("index")


def _store_plan_in_session(request, plan: Dict[str, object]) -> None:
    request.session["plan_name"] = plan.get("name")
    request.session["display_name"] = plan.get("display_name")
    request.session["stripe_price_id"] = plan.get("stripe_price_id")
    request.session["price_display"] = plan.get("price_display")
    request.session["description"] = plan.get("description")
    request.session["features"] = plan.get("features")


@maybe_login_required
def create_checkout_session(request, plan_name: str):
    plan = next((p for p in build_plan_catalog() if p["name"] == plan_name), None)
    if not plan:
        messages.error(request, "Plan not found.")
        return redirect("index")

    _store_plan_in_session(request, plan)

    if not settings.ENABLE_REAL_PAYMENTS:
        messages.info(request, "Demo mode enabled — skipping payment gateway.")
        return redirect("success")

    if not settings.STRIPE_SECRET_KEY:
        messages.error(request, "Stripe is not configured.")
        return redirect("index")

    price_id = plan.get("stripe_price_id")
    if not price_id:
        messages.error(request, "Stripe price ID missing for this plan.")
        return redirect("index")

    try:
        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=request.build_absolute_uri("/success/"),
            cancel_url=request.build_absolute_uri("/cancel/"),
        )
        return redirect(checkout_session.url)
    except Exception as exc:
        messages.error(request, f"Unable to create checkout session: {exc}")
        return redirect("index")


def success_view(request):
    plan_name = request.session.get("plan_name")
    display_name = request.session.get("display_name")
    stripe_price_id = request.session.get("stripe_price_id")
    description = request.session.get("description")
    features = request.session.get("features") or []
    price_display = request.session.get("price_display")

    if (
        settings.ENABLE_REAL_PAYMENTS
        and settings.ENABLE_AUTH
        and request.user.is_authenticated
        and plan_name
    ):
        start_date = timezone.now()
        expire_date = None
        if plan_name == "monthly":
            expire_date = start_date + timedelta(days=30)
        elif plan_name == "quarterly":
            expire_date = start_date + timedelta(days=90)
        elif plan_name == "yearly":
            expire_date = start_date + timedelta(days=365)

        SubscriptionPlan.objects.update_or_create(
            user=request.user,
            defaults={
                "name": plan_name,
                "stripe_price_id": stripe_price_id or "",
                "display_name": display_name or "",
                "description": description or "",
                "features": ", ".join(features) if isinstance(features, list) else str(features),
                "start_date": start_date,
                "expire_date": expire_date,
            },
        )

    context = {
        "plan_summary": {
            "name": display_name,
            "price_display": price_display,
            "description": description,
            "features": features,
        },
    }
    return render(request, "success.html", context)


def cancel_view(request):
    return render(request, "cancel.html")


def encode_image_to_base64(file) -> str:
    image = Image.open(file)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _generate_demo_response(user_message: str) -> str:
    responses = settings.DEMO_CHAT_RESPONSES or [
        "Remember: consistency beats intensity. Choose one action you can finish before the day ends.",
        "Audit your last 24 hours. What helped you move forward? What held you back?",
        "Take a 5-minute reset. Breathe, re-focus, then attack the hardest task on your list.",
    ]
    if not responses:
        return "Stay disciplined. Use this time to plan your next move."

    index = sum(ord(char) for char in user_message) if user_message else 0
    return responses[index % len(responses)]


@csrf_exempt
def smart_chat_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    message = ""
    image_file = None

    if request.content_type and request.content_type.startswith("multipart/form-data"):
        message = request.POST.get("message", "")
        image_file = request.FILES.get("image")
    else:
        try:
            payload = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)
        message = payload.get("message", "")

    if not settings.ENABLE_REAL_CHAT:
        return JsonResponse({"response": _generate_demo_response(message)})

    if not settings.OPENAI_API_KEY:
        return JsonResponse({"error": "Chat service is not configured."}, status=503)

    try:
        import openai

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        prompt_instance = Prompt.objects.first()
        final_message = message
        if prompt_instance:
            final_message = f"{prompt_instance.content}\n{message}" if message else prompt_instance.content

        messages_payload: List[Dict[str, object]]
        model = "gpt-4o"

        if image_file:
            messages_payload = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": final_message},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{encode_image_to_base64(image_file)}"},
                        },
                    ],
                }
            ]
        else:
            messages_payload = [{"role": "user", "content": final_message}]

        response = client.chat.completions.create(
            model=model,
            messages=messages_payload,
            max_tokens=800,
        )
        return JsonResponse({"response": response.choices[0].message.content})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)