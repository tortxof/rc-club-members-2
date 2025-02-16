from django.http.response import HttpResponse
from django.views.generic import DetailView, ListView

from .models import Member


def index(request):
    return HttpResponse("This is the index.")


class MembersListView(ListView):
    queryset = Member.objects.all().order_by("last_name", "first_name")


class MemberDetailView(DetailView):
    model = Member
