from django.contrib import admin

from members_base.models import Member, MembershipClass, Office, PhoneNumber


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber


class OfficerInline(admin.TabularInline):
    model = Member.offices.through


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    inlines = [PhoneNumberInline]
    list_display = ["first_name", "last_name", "email", "expiration_date"]
    list_display_links = ["first_name", "last_name"]
    ordering = ["last_name", "first_name"]


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    inlines = [OfficerInline]


admin.site.register(MembershipClass)
