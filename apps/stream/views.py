from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from apps.stream.models import Action


class List(ListView):
    template_name = 'stream/action_list.html'
    paginate_by = 50
    model = Action


list = login_required(List.as_view())
