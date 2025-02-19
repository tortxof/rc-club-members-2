import json

import mistletoe
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from ama import verify_ama_membership

from .authentication import generate_signin_url
from .forms import EmailReadOnlyTokenForm, SendEmailForm
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


@login_required
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


@staff_member_required(login_url=settings.LOGIN_URL)
def send_email_prepare(request):
    if request.method == "POST":
        messages.info(request, "Not Implemented.")
        form = SendEmailForm(request.POST)
        if form.is_valid():
            match form.cleaned_data["member_group"]:
                case "all":
                    queryset = Member.objects.all()
                case "active":
                    queryset = Member.objects.active()
                case "current":
                    queryset = Member.objects.current()
                case "expired":
                    queryset = Member.objects.expired()
                case "previous":
                    queryset = Member.objects.previous()

            recipient_variables = {}

            for member in queryset:
                if not member.email:
                    continue

                recipient_variables[member.email] = {
                    "first_name": member.first_name,
                    "last_name": member.last_name,
                    "full_name": member.full_name,
                    "signin_url": generate_signin_url(member),
                }

            body_html = mistletoe.markdown(
                form.cleaned_data["body"].replace("\r\n", "\n")
            )

            request.session["send_email_data"] = {
                "form_data": form.cleaned_data,
                "recipient_variables": recipient_variables,
                "body_html": body_html,
            }

            return redirect("send_email_confirm")

        else:
            messages.error(request, "Form not valid.")

        return redirect("index")

    elif request.method == "GET":
        now = timezone.now()
        subject = f"{settings.APP_SHORT_NAME} {now.strftime('%B')} Newsletter"
        form = SendEmailForm(
            initial={
                "member_group": "active",
                "from_email_user": settings.DEFAULT_FROM_EMAIL_USER,
                "subject": subject,
            }
        )
        return render(request, "members_base/send_email_prepare.html", {"form": form})


@staff_member_required(login_url=settings.LOGIN_URL)
def send_email_confirm(request):
    if request.method == "POST":
        if "send_email_data" not in request.session:
            return redirect("send_email_prepare")

        send_email_data = request.session["send_email_data"]

        response = requests.post(
            settings.MAILGUN_URL,
            auth=("api", settings.MAILGUN_API_KEY),
            data={
                "from": f"{send_email_data['form_data']['from_email_user']}@{settings.MAILGUN_DOMAIN}",
                "to": list(send_email_data["recipient_variables"].keys()),
                "subject": send_email_data["form_data"]["subject"],
                "text": send_email_data["form_data"]["body"],
                "html": send_email_data["body_html"],
                "recipient-variables": json.dumps(
                    send_email_data["recipient_variables"]
                ),
            },
        )

        if response.status_code == 200:
            messages.success(request, response.json().get("message", "Email sent."))

            del request.session["send_email_data"]

            return redirect("index")

        else:
            messages.warning(request, "There was a problem sending the email.")

            return redirect("send_email_confirm")

    elif request.method == "GET":
        if "send_email_data" not in request.session:
            return redirect("send_email_prepare")

        return render(request, "members_base/send_email_confirm.html")


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
