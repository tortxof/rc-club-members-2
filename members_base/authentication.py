from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core import signing
from django.db.models import F
from django.urls import reverse

from .models import Member

UserModel = get_user_model()


def generate_token(member: Member):
    return signing.dumps({"member_id": member.id.hex}, salt="readonlytoken")


def generate_signin_url(member: Member):
    uri = reverse("read_only_token_auth", args=[generate_token(member)])
    return f"{settings.APP_ORIGIN}{uri}"


class ReadOnlyTokenBackend(BaseBackend):
    def get_user(self, user_id):
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        if user.is_active:
            return user

        return None

    def authenticate(self, request, token=None, **kwargs):
        try:
            token_data = signing.loads(
                token, salt="readonlytoken", max_age=timedelta(days=4 * 7)
            )
        except (signing.BadSignature, signing.SignatureExpired):
            return None

        try:
            member = Member.objects.get(id=token_data["member_id"])
        except Member.DoesNotExist:
            return None

        try:
            user = UserModel.objects.get(username=member.email, email=F("username"))
        except UserModel.DoesNotExist:
            user = UserModel.objects.create(username=member.email, email=member.email)

        if user.is_active:
            return user

        return None
