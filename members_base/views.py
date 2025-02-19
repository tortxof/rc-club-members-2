import json
from itertools import count

import mistletoe
import requests
import xlsxwriter
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotAllowed
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

    return render(request, "members_base/index.html")


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

            signin_url = generate_signin_url(member)
            try:
                requests.post(
                    settings.MAILGUN_URL,
                    auth=("api", settings.MAILGUN_API_KEY),
                    data={
                        "from": f"{settings.APP_SHORT_NAME} Roster <{settings.NOREPLY_EMAIL}>",
                        "to": [member.email],
                        "subject": f"{settings.APP_SHORT_NAME} Roster Sign-In",
                        "text": signin_url,
                        "html": mistletoe.markdown(
                            f"[Click here to sign in.]({signin_url})"
                        ),
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


@login_required
def download_xlsx(request, group):
    match group:
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
        case _:
            messages.error(request, "Invalid group selection.")
            return redirect("index")

    queryset = queryset.order_by("last_name", "first_name")
    member_count = queryset.count()

    now = timezone.now()

    filename = f"{settings.APP_SHORT_NAME}-roster-{now.date().isoformat()}.xlsx".lower()

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

    col_names = [
        "First",
        "Last",
        "Email",
        "AMA Number",
        "Phone",
        "Address",
        "City",
        "State",
        "Zip Code",
        "Class",
        "Office",
        "Expiration",
        "Date of Birth",
    ]

    workbook = xlsxwriter.Workbook(response)

    worksheet = workbook.add_worksheet("Members")
    worksheet.set_landscape()

    header_fmt = workbook.add_format({"bold": True, "bottom": True})
    expired_fmt = workbook.add_format({"font_color": "red"})
    gray_bg_fmt = workbook.add_format({"bg_color": "#DDDDDD"})

    for col, name in enumerate(col_names):
        worksheet.write(0, col, name, header_fmt)

    for row, member in enumerate(queryset, start=1):
        col = count()
        worksheet.write(row, next(col), member.first_name)
        worksheet.write(row, next(col), member.last_name)
        worksheet.write(row, next(col), member.email)
        worksheet.write(row, next(col), member.ama_number)
        worksheet.write(
            row,
            next(col),
            " ".join(
                phonenumber.phone_number
                for phonenumber in member.phonenumber_set.all().order_by("is_primary")
            ),
        )
        worksheet.write(row, next(col), member.address)
        worksheet.write(row, next(col), member.city)
        worksheet.write(row, next(col), member.state)
        worksheet.write(row, next(col), member.zip_code)
        worksheet.write(row, next(col), member.membership_class.name)
        worksheet.write(
            row, next(col), " ".join(office.name for office in member.offices.all())
        )
        if member.membership_is_current:
            worksheet.write(row, next(col), member.expiration_date.isoformat())
        else:
            worksheet.write(
                row, next(col), member.expiration_date.isoformat(), expired_fmt
            )
        worksheet.write(
            row,
            next(col),
            member.date_of_birth.isoformat() if member.date_of_birth else "",
        )

    for row in range(2, member_count + 1, 2):
        worksheet.set_row(row, None, gray_bg_fmt)

    worksheet.merge_range(
        member_count + 2,
        0,
        member_count + 2,
        len(col_names) - 1,
        f"{member_count} members",
    )
    worksheet.merge_range(
        member_count + 3,
        0,
        member_count + 3,
        len(col_names) - 1,
        f"Generated: {now.date().isoformat()}",
    )
    worksheet.print_area(0, 0, member_count + 3, len(col_names) - 1)
    worksheet.fit_to_pages(1, 1)
    workbook.close()

    return response


@staff_member_required(login_url=settings.LOGIN_URL)
def send_email_prepare(request):
    if request.method == "POST":
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

            if len(recipient_variables) == 0:
                messages.warning(request, "No email recipients in this group.")
                return redirect("send_email_prepare")

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

        return redirect("send_email_prepare")

    elif request.method == "GET":
        now = timezone.now()
        month = now.strftime("%B")
        subject = f"{settings.APP_SHORT_NAME} {month} Newsletter"
        form = SendEmailForm(
            initial={
                "member_group": "active",
                "from_email_user": settings.DEFAULT_FROM_EMAIL_USER,
                "subject": subject,
            }
        )
        return render(
            request,
            "members_base/send_email_prepare.html",
            {"form": form, "month": month},
        )


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member_group"] = "all"
        return context


class MembersActiveListView(LoginRequiredMixin, ListView):
    queryset = Member.objects.active().order_by("last_name", "first_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member_group"] = "active"
        return context


class MembersCurrentListView(LoginRequiredMixin, ListView):
    queryset = Member.objects.current().order_by("last_name", "first_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member_group"] = "current"
        return context


class MembersExpiredListView(LoginRequiredMixin, ListView):
    queryset = Member.objects.expired().order_by("last_name", "first_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member_group"] = "expired"
        return context


class MembersPreviousListView(LoginRequiredMixin, ListView):
    queryset = Member.objects.previous().order_by("last_name", "first_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member_group"] = "previous"
        return context


class MemberDetailView(LoginRequiredMixin, DetailView):
    model = Member
