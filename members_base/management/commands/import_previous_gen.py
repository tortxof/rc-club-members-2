import datetime
import json

from django.core.management.base import BaseCommand

from members_base.models import Member, MembershipClass, PhoneNumber


class Command(BaseCommand):
    help = "Imports data from previous generation app"

    def add_arguments(self, parser):
        parser.add_argument("export_file", type=str)

    def handle(self, *args, **options):
        membership_class, _ = MembershipClass.objects.get_or_create(name="Adult")

        with open(options["export_file"]) as f:
            data = json.load(f)["members"]

        for record in data:
            try:
                expiration_date = datetime.date.fromisoformat(record["expire"])
            except ValueError:
                expiration_date = None

            try:
                date_of_birth = datetime.datetime.strptime(
                    record["dob"], "%a, %d %b %Y %H:%M:%S %Z"
                ).date()
            except ValueError:
                date_of_birth = None

            member = Member.objects.create(
                membership_class=membership_class,
                email=record["email"],
                first_name=record["first_name"],
                last_name=record["last_name"],
                ama_number=record["ama"],
                address=record["address"],
                city=record["city"],
                state=record["state"],
                zip_code=record["zip_code"],
                expiration_date=expiration_date,
                date_of_birth=date_of_birth,
            )

            for phone_number in record["phone"].split():
                PhoneNumber.objects.create(phone_number=phone_number, member=member)
