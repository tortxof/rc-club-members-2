import datetime
import urllib.parse
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils import timezone


def get_default_expiration_date():
    return timezone.now().date().replace(month=12, day=31)


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class Office(UUIDModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.name}"


class MembershipClass(UUIDModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Membership classes"

    def __str__(self):
        return f"{self.name}"


class MemberQuerySet(models.QuerySet):
    def expired(self):
        return self.filter(expiration_date__lt=datetime.date.today())

    def current(self):
        return self.filter(expiration_date__gte=datetime.date.today())

    def current_last_year(self):
        end_of_last_year = datetime.date.today().replace(
            month=1, day=1
        ) - datetime.timedelta(days=1)
        return self.filter(expiration_date__gte=end_of_last_year)

    def active(self):
        if datetime.date.today().month <= 3:
            return self.current_last_year()
        return self.current()

    def previous(self):
        return self.expired().intersection(self.current_last_year())

    def officers(self):
        return self.filter(offices__isnull=False)

    def mailto_url(self):
        emails = ",".join(member.email for member in self if member.email)
        emails = f"bcc={emails}"
        url = urllib.parse.urlunparse(
            ("mailto", "", settings.NOREPLY_EMAIL, "", emails, "")
        )
        return url

    mailto_url.queryset_only = True


class Member(UUIDModel):
    objects = MemberQuerySet.as_manager()
    membership_class = models.ForeignKey(
        MembershipClass, on_delete=models.PROTECT, related_name="membership_class"
    )
    offices = models.ManyToManyField(Office, blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True)
    ama_number = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=255, blank=True)
    expiration_date = models.DateField(default=get_default_expiration_date)
    date_of_birth = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.full_name}"

    @property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"

        return f"{self.first_name}"

    @property
    def membership_is_current(self):
        return self.expiration_date >= datetime.date.today()


class PhoneNumber(UUIDModel):
    phone_number = models.CharField(max_length=255)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone_number}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            self.__class__.objects.filter(member=self.member).update(is_primary=False)
        return super().save(*args, **kwargs)
