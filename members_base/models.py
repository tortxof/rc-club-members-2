from uuid import uuid4

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


class Member(UUIDModel):
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


class PhoneNumber(UUIDModel):
    phone_number = models.CharField(max_length=255)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.phone_number}"
