from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from django.template.loader import render_to_string


def json_render(request, template_name, context, **kwargs):
    """
    Returns a JSON response for displaying some HTML. This is very specific
    to this project and depends on the JavaScript supporting the result that
    is returned from this method.
    """
    if not request.is_ajax():
        raise PermissionDenied("Must be an AJAX request.")
    html = render_to_string(
        template_name, context, context_instance=RequestContext(request))
    return JsonResponse({'html': html}, **kwargs)


def json_redirect(request, url, **kwargs):
    """
    Returns a JSON response for redirecting to a new URL. This is very specific
    to this project and depends on the JavaScript supporting the result that
    is returned from this method.
    """
    if not request.is_ajax():
        raise PermissionDenied("Must be an AJAX request.")
    return JsonResponse({'url': url}, **kwargs)


from django.http import JsonResponse
from django.views.generic import FormView, CreateView, UpdateView, DeleteView, RedirectView

__all__ = ['AjaxFormView', 'AjaxCreateView', 'AjaxUpdateView', 'AjaxDeleteView', 'RedirectView']


class AjaxFormMixin:
    """
    Provides methods to return JSON responses for Django's class-based form views.
    """
    def json(self, **data):
        return JsonResponse(data)

    def form_valid(self, form):
        return self.json(url=self.get_success_url())

    def render_to_response(self, context, **kwargs):
        response = super().render_to_response(context, **kwargs)
        return self.json(html=response.rendered_content)


class AjaxCreateView(AjaxFormMixin, CreateView):
    """
    Just like a normal CreateView, except it will return JSON responses.
    """
    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)


class AjaxUpdateView(AjaxFormMixin, UpdateView):
    """
    Just like a normal UpdateView, except it will return JSON responses.
    """
    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)


class AjaxDeleteView(AjaxFormMixin, DeleteView):
    """
    Just like a normal DeleteView, except it will return JSON responses
    if the request was a JSON request.
    TODO: fix this
    """
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return self.json(url=success_url)

