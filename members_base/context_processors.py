from django.conf import settings


def app_settings(request):
    return {
        "APP_ORIGIN": settings.APP_ORIGIN,
        "APP_NAME": settings.APP_NAME,
    }


def url_name(request):
    return {"url_name": request.resolver_match.url_name}
