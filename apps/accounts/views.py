from urllib.parse import urlparse

from django.contrib.messages.views import SuccessMessageMixin

from django.utils.translation import ugettext_lazy as _
from django.shortcuts import resolve_url
from django.conf import settings
from django.http import Http404
from django.core.urlresolvers import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model, logout as logout_user, login as login_user, REDIRECT_FIELD_NAME
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView, FormView, CreateView, UpdateView

from apps.accounts.forms import ProfileForm, RegisterForm, AuthenticationForm, \
    PasswordResetForm, SetPasswordForm, PasswordChangeForm

User = get_user_model()


class Login(FormView):
    template_name = 'accounts/login.html'
    form_class = AuthenticationForm

    def get_redirect_to(self):
        field = REDIRECT_FIELD_NAME
        return self.request.GET.get(field, self.request.POST.get(field, ''))

    def get_context_data(self, **kwargs):
        kwargs['redirect_field'] = REDIRECT_FIELD_NAME
        kwargs['redirect_to'] = self.get_redirect_to()
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        redirect_to = self.get_redirect_to()
        netloc = urlparse(redirect_to)[1]
        if not redirect_to or (netloc and netloc != self.request.get_host()):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
        return redirect_to

    def form_valid(self, form):
        login_user(self.request, form.get_user())
        return super().form_valid(form)


class Logout(RedirectView):
    pattern_name = settings.LOGIN_URL
    permanent = False

    def get(self, request, *args, **kwargs):
        logout_user(request)
        return super().get(request, *args, **kwargs)


class Register(SuccessMessageMixin, CreateView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_message = _('Your account has been created. You may now log in.')
    success_url = reverse_lazy('accounts:login')

    def get_initial(self):
        initial = super().get_initial()
        initial['auth_code'] = self.kwargs.get('auth', '')
        return initial


class Profile(SuccessMessageMixin, UpdateView):
    template_name = 'accounts/profile.html'
    form_class = ProfileForm
    success_message = _('Your profile has been successfully updated.')
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user


class PasswordChange(SuccessMessageMixin, UpdateView):
    template_name = 'accounts/profile.html'
    form_class = PasswordChangeForm
    success_message = _('Your password has been successfully changed.')
    success_url = reverse_lazy('accounts:password_change')

    def get_object(self, queryset=None):
        return self.request.user


class PasswordReset(SuccessMessageMixin, FormView):
    template_name = 'accounts/password_reset.html'
    form_class = PasswordResetForm
    email_template_name = 'accounts/password_reset_email.txt'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_message = _('You will receive an email with instructions to reset your password. Please look for it.')
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        options = {
            'token_generator': default_token_generator,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
        }
        form.save(**options)
        return super().form_valid(form)


class PasswordResetConfirm(SuccessMessageMixin, UpdateView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = SetPasswordForm
    success_message = _('Your password has been successfully changed. You may now log in.')
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        try:
            self.uid36 = self.kwargs['uid36']
            self.token = self.kwargs['token']
            self.user = User._default_manager.get(pk=urlsafe_base64_decode(self.uid36))
            if not default_token_generator.check_token(self.user, self.token):
                raise ValueError
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise Http404('Invalid request. uid36={} token={}'.format(self.uid36, self.token))
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uid36'] = self.uid36
        context['token'] = self.token
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


logout = Logout.as_view()
login = Login.as_view()
register = Register.as_view()
profile = login_required(Profile.as_view())
password_change = login_required(PasswordChange.as_view())
password_reset = PasswordReset.as_view()
password_reset_confirm = PasswordResetConfirm.as_view()
