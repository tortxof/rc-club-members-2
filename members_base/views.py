import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

from .authentication import generate_signin_url
from .forms import EmailReadOnlyTokenForm
from .models import Member


def index(request):
    if request.user.is_authenticated:
        return redirect("members")

    form = EmailReadOnlyTokenForm()

    return render(request, "members_base/index.html", {"form": form})


def sign_out(request):
    logout(request)
    return redirect("index")


def read_only_token_auth(request, token):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    user = authenticate(request, token=token)

    if user is not None:
        login(request, user)

    return redirect("index")


def email_read_only_token(request):
    if request.method == "POST":
        form = EmailReadOnlyTokenForm(request.POST)
        if form.is_valid():
            try:
                member = Member.objects.get(email=form.cleaned_data["email"])
            except Member.DoesNotExist:
                return redirect("index")

            requests.post(
                settings.MAILGUN_URL,
                auth=("api", settings.MAILGUN_API_KEY),
                data={
                    "from": f"Members App <{settings.DEFAULT_FROM_EMAIL}>",
                    "to": [member.email],
                    "subject": "Members Sign In",
                    "text": generate_signin_url(member),
                },
                timeout=settings.MAILGUN_TIMEOUT,
            )

            return redirect("index")

        return HttpResponse("Form not valid", status=400)

    return HttpResponseNotAllowed(["POST"])


class MembersListView(LoginRequiredMixin, ListView):
    queryset = Member.objects.all().order_by("last_name", "first_name")


class MemberDetailView(LoginRequiredMixin, DetailView):
    model = Member
