import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

from ama import verify_ama_membership

from .authentication import generate_signin_url
from .forms import EmailReadOnlyTokenForm
from .models import Member


def index(request):
    if request.user.is_authenticated:
        return redirect("members_active")

    form = EmailReadOnlyTokenForm()

    return render(request, "members_base/index.html", {"form": form})


def sign_out(request):
    logout(request)
    return redirect("index")


def read_only_token_auth(request, token):
    user = authenticate(request, token=token)

    if user is not None:
        login(request, user)
    else:
        messages.error(
            request,
            "There was a problem signing you in. The sign-in link may be expired. Please try again.",
        )

    return redirect("index")


def email_read_only_token(request):
    if request.method == "POST":
        form = EmailReadOnlyTokenForm(request.POST)
        if form.is_valid():
            try:
                member = Member.objects.get(email=form.cleaned_data["email"])
            except Member.DoesNotExist:
                messages.error(request, "Email address not found.")
                return redirect("index")

            try:
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
            except requests.RequestException:
                messages.error(
                    request,
                    "There was a problem sending your email. Please try again later.",
                )
                return redirect("index")

            messages.success(request, "A sign-in link has been sent to your email.")

            return redirect("index")

        messages.error(
            request,
            "There was a problem with the data that was submitted. Please try again.",
        )

        return redirect("index")

    return HttpResponseNotAllowed(["POST"])


def ama_verify(request, pk):
    response = redirect(request.GET.get("next", "index"))

    try:
        member = Member.objects.get(pk=pk)
    except Member.DoesNotExist:
        messages.error(request, "Member not found.")
        return response

    if not (member.last_name and member.ama_number):
        messages.error(
            request, "Last name and AMA number are needed to verify AMA membership."
        )
        return response

    ama_status = verify_ama_membership(member.last_name, member.ama_number)

    messages.info(request, ama_status)

    return response


class MembersListView(LoginRequiredMixin, ListView):
    queryset = Member.objects.all().order_by("last_name", "first_name")


class MembersActiveListView(LoginRequiredMixin, ListView):
    queryset = Member.objects.active().order_by("last_name", "first_name")


class MembersCurrentListView(LoginRequiredMixin, ListView):
    queryset = Member.objects.current().order_by("last_name", "first_name")


class MembersExpiredListView(LoginRequiredMixin, ListView):
    queryset = Member.objects.expired().order_by("last_name", "first_name")


class MembersPreviousListView(LoginRequiredMixin, ListView):
    queryset = Member.objects.previous().order_by("last_name", "first_name")


class MemberDetailView(LoginRequiredMixin, DetailView):
    model = Member
