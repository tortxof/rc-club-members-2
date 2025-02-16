from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("members/", views.MembersListView.as_view(), name="members"),
    path(
        "members/<uuid:pk>",
        views.MemberDetailView.as_view(),
        name="member_detail",
    ),
]
