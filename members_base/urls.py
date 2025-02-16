from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sign-out/", views.sign_out, name="sign_out"),
    path(
        "ro-token/<str:token>/", views.read_only_token_auth, name="read_only_token_auth"
    ),
    path("email-ro-token/", views.email_read_only_token, name="email_read_only_token"),
    path("members/", views.MembersListView.as_view(), name="members"),
    path(
        "members/<uuid:pk>",
        views.MemberDetailView.as_view(),
        name="member_detail",
    ),
]
