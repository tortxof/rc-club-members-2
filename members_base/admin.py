from django.contrib import admin

from members_base.models import Member, MembershipClass, Office, PhoneNumber


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    inlines = [PhoneNumberInline]


admin.site.register(MembershipClass)
admin.site.register(Office)
