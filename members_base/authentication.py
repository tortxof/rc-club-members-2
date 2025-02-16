from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core import signing
from django.db.models import F

from .models import Member

UserModel = get_user_model()


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
            token_data = signing.loads(token, salt="readonlytoken")
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
