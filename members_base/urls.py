from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sign-out/", views.sign_out, name="sign_out"),
    path("ro/<str:token>/", views.read_only_token_auth, name="read_only_token_auth"),
    path("email-ro-token/", views.email_read_only_token, name="email_read_only_token"),
    path(
        "members-active/", views.MembersActiveListView.as_view(), name="members_active"
    ),
    path(
        "members-current/",
        views.MembersCurrentListView.as_view(),
        name="members_current",
    ),
    path(
        "members-expired/",
        views.MembersExpiredListView.as_view(),
        name="members_expired",
    ),
    path(
        "members-previous/",
        views.MembersPreviousListView.as_view(),
        name="members_previous",
    ),
    path("members-officers/", views.MembersOfficersListView.as_view(), name="members_officers"),
    path("members/", views.MembersListView.as_view(), name="members"),
    path("members/<uuid:pk>", views.MemberDetailView.as_view(), name="member_detail"),
    path("ama-verify/<uuid:pk>", views.ama_verify, name="ama_verify"),
    path("send-email-prepare/", views.send_email_prepare, name="send_email_prepare"),
    path("send-email-confirm/", views.send_email_confirm, name="send_email_confirm"),
    path("xlsx/<str:group>/", views.download_xlsx, name="download_xlsx"),
]
