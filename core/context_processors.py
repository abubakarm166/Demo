from django.conf import settings


def demo_flags(_request):
    """
    Inject deployment-mode flags into every template so that navigation and
    call-to-action elements can adapt automatically between demo and full
    builds.
    """
    return {
        "DEMO_MODE": getattr(settings, "DEMO_MODE", False),
        "ENABLE_AUTH": getattr(settings, "ENABLE_AUTH", False),
        "ENABLE_REAL_PAYMENTS": getattr(settings, "ENABLE_REAL_PAYMENTS", False),
        "ENABLE_REAL_CHAT": getattr(settings, "ENABLE_REAL_CHAT", False),
    }

