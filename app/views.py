from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

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
        "demo_price_default": "€79 / year",
    },
]


def build_plan_catalog() -> List[Dict[str, object]]:
    catalog: List[Dict[str, object]] = []
    for raw_plan in PLAN_DEFINITIONS:
        plan = deepcopy(raw_plan)
        plan_name = plan["name"]
        plan["price_display"] = settings.DEMO_PLAN_PRICING.get(
            plan_name,
            plan.get("demo_price_default") or "Contact for pricing",
        )
        plan["button_label"] = "View Demo"
        catalog.append(plan)
    return catalog


def index(request):
    plans = build_plan_catalog()
    return render(request, "index.html", {"plans": plans})


def demo(request):
    return render(request, "chatbot.html")


def coach_demo_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    user_message = ""
    if request.content_type and request.content_type.startswith("multipart/form-data"):
        user_message = request.POST.get("message", "")
    else:
        payload = request.body.decode("utf-8") or ""
        if payload:
            try:
                data = json.loads(payload)
                user_message = data.get("message", "")
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    canned_responses = settings.DEMO_CHAT_RESPONSES or [
        "Hi there! This is a demo response.",
        "Stay disciplined. This version is for showcasing only.",
        "Thanks for trying the demo — no real API calls were made.",
    ]

    index = sum(ord(char) for char in user_message) if user_message else 0
    reply = canned_responses[index % len(canned_responses)]

    return JsonResponse({"message": reply})