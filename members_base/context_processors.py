from django.conf import settings


def app_settings(request):
    return {
        "APP_ORIGIN": settings.APP_ORIGIN,
        "APP_NAME": settings.APP_NAME,
        "APP_SHORT_NAME": settings.APP_SHORT_NAME,
        "MAILGUN_DOMAIN": settings.MAILGUN_DOMAIN,
    }


def url_name(request):
    return {"url_name": request.resolver_match.url_name}
