from django.conf import settings


def app_settings(request):
    return {
        "APP_ORIGIN": settings.APP_ORIGIN,
        "APP_NAME": settings.APP_NAME,
    }
