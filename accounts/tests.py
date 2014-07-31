from django.contrib.auth.tokens import default_token_generator

from django.test import TestCase, Client
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.forms.fields import Field
from django.utils.encoding import force_text, force_bytes
from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.utils.http import urlsafe_base64_encode

from accounts.forms import PasswordResetForm, RegisterForm, \
    AuthenticationForm, ProfileForm, PasswordChangeForm, SetPasswordForm


class TestCaseWithUser(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'secret'
        self.user = User.objects.create_user(
            username='jacob',
            email='jacob@example.com',
            password=self.password)

    def login(self):
        form_data = {'username': self.user.username, 'password': self.password}
        response = self.client.post(reverse('accounts:login'), form_data)
        self.assertTrue(SESSION_KEY in self.client.session)
        return response

    def form_in_response(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)


class ProfileView(TestCaseWithUser):
    def test_get(self):
        """
        Test that the profile contains the profile form.
        """
        self.login()
        self.form_in_response(reverse('accounts:profile'))

    def test_update(self):
        """
        Test that a user can update his profile successfully.
        """
        self.login()
        form_data = {'first_name': 'Jacob', 'last_name': 'User',
                     'email': 'newemail@example.com'}
        response = self.client.post(reverse('accounts:profile'), form_data)
        self.assertRedirects(response, reverse('accounts:profile'))
        user = User.objects.get(username=self.user.username)
        self.assertEqual(user.first_name, 'Jacob')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.email, 'newemail@example.com')

    def test_cant_change_username(self):
        """
        Test that a user cannot update his username through profile.
        """
        self.login()
        form_data = {'username': 'hacked', 'email': 'jacob@example.com'}
        response = self.client.post(reverse('accounts:profile'), form_data)
        self.assertRedirects(response, reverse('accounts:profile'))
        with self.assertRaises(User.DoesNotExist):
            user = User.objects.get(username='hacked')

    def test_duplicate_email(self):
        """
        Test that email address cannot be a duplicate of another user.
        """
        self.login()
        self.user = User.objects.create_user(
            username='jacob2',
            email='jacob2@example.com',
            password='welcome2')
        form_data = {'first_name': 'Jacob', 'last_name': 'User',
                     'email': 'jacob2@example.com'}
        response = self.client.post(reverse('accounts:profile'), form_data)
        self.assertFormError(
            response, 'form', 'email',
            ProfileForm.error_messages['duplicate_email'])


class LogoutView(TestCaseWithUser):
    def test_get(self):
        """
        Test that the logout page works and redirects to login page.
        """
        self.login()
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertTrue(SESSION_KEY not in self.client.session)


class LoginView(TestCaseWithUser):
    def test_get(self):
        """
        Test that the login page contains the login form.
        """
        self.form_in_response(reverse('accounts:login'))

    def test_valid(self):
        """
        Test that a valid login gets redirected to the home page.
        """
        form_data = {'username': self.user.username, 'password': self.password}
        response = self.client.post(reverse('accounts:login'), form_data)
        self.assertTrue(SESSION_KEY in self.client.session)
        self.assertRedirects(response, reverse('home'))

    def test_invalid(self):
        """
        Test that an invalid login does not work.
        """
        form_data = {'username': 'bad', 'password': 'bad'}
        response = self.client.post(reverse('accounts:login'), form_data)
        self.assertTrue(SESSION_KEY not in self.client.session)
        self.assertFormError(
            response, 'form', '__all__',
            AuthenticationForm.error_messages['invalid_login'] % {
                'username': User._meta.get_field('username').verbose_name
            })


class RegisterView(TestCaseWithUser):
    def test_get(self):
        """
        Test that the register page contains the register form.
        """
        self.form_in_response(reverse('accounts:register'))

    def test_invalid(self):
        """
        Test that all required fields are enforced.
        """
        form_data = {'username': ''}
        response = self.client.post(reverse('accounts:register'), form_data)
        required_error = force_text(Field.default_error_messages['required'])
        self.assertFormError(response, 'form', 'username', required_error)
        self.assertFormError(response, 'form', 'auth_code', required_error)
        self.assertFormError(response, 'form', 'username', required_error)
        self.assertFormError(response, 'form', 'email', required_error)
        self.assertFormError(response, 'form', 'password1', required_error)

    def test_duplicate_fields(self):
        """
        Test that username and email must be unique.
        """
        form_data = {'username': self.user.username, 'email': self.user.email}
        response = self.client.post(reverse('accounts:register'), form_data)
        self.assertFormError(
            response, 'form', 'username',
            RegisterForm.error_messages['duplicate_username'])
        self.assertFormError(
            response, 'form', 'email',
            RegisterForm.error_messages['duplicate_email'])

    def test_valid_auth_code_user(self):
        """
        Test that valid authorization code works for user.
        """
        form_data = {'username': 'uniq', 'email': 'uniq@example.com',
                     'password1': 'welcome', 'password2': 'welcome',
                     'auth_code': settings.AUTH_CODE_USER}
        response = self.client.post(reverse('accounts:register'), form_data)
        self.assertRedirects(response, reverse('accounts:login'))
        uniq = User.objects.get_by_natural_key('uniq').groups.all()
        self.assertEqual(uniq.count(), 0)

    def test_valid_auth_code_admin(self):
        """
        Test that valid authorization code works for admin.
        """
        form_data = {'username': 'uniq', 'email': 'uniq@example.com',
                     'password1': 'welcome', 'password2': 'welcome',
                     'auth_code': settings.AUTH_CODE_ADMIN}
        response = self.client.post(reverse('accounts:register'), form_data)
        self.assertRedirects(response, reverse('accounts:login'))
        uniq = User.objects.get_by_natural_key('uniq').groups.all()
        self.assertEqual(uniq.count(), 1)
        self.assertEqual(uniq[0], Group.objects.get(
            name=settings.AUTH_CODE_ADMIN_GROUP))

    def test_invalid_auth(self):
        """
        Test that otherwise valid forms do not work with an invalid auth code.
        """
        form_data = {'username': 'uniq', 'email': 'uniq@example.com',
                     'password1': 'welcome', 'password2': 'welcome',
                     'auth_code': 'fake'}
        response = self.client.post(reverse('accounts:register'), form_data)
        self.assertFormError(
            response, 'form', 'auth_code',
            RegisterForm.error_messages['invalid_auth_code'])


class PasswordResetView(TestCaseWithUser):
    def test_get(self):
        """
        Test that the password reset page contains the form.
        """
        self.form_in_response(reverse('accounts:password_reset'))

    def test_invalid(self):
        """
        Test that invalid email addresses will be caught.
        """
        form_data = {'email': 'invalid@invalid.com'}
        response = self.client.post(
            reverse('accounts:password_reset'), form_data)
        self.assertFormError(
            response, 'form', 'email',
            PasswordResetForm.error_messages['invalid_email'])
        self.assertEqual(len(mail.outbox), 0)

    def test_valid(self):
        """
        Test that the valid email addresses will get an email.
        """
        form_data = {'email': self.user.email}
        response = self.client.post(
            reverse('accounts:password_reset'), form_data)
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue('http://' in mail.outbox[0].body)
        self.assertEqual(
            settings.DEFAULT_FROM_EMAIL, mail.outbox[0].from_email)


class PasswordResetConfirmView(TestCaseWithUser):
    def test_invalid(self):
        """
        Test that non matching passwords will be caught.
        """
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse(
            'accounts:password_reset_confirm',
            kwargs=dict(uidb64=uid, token=token))
        self.form_in_response(url)
        form_data = {'new_password1': 'password1',
                     'new_password2': 'password2'}
        response = self.client.post(url, form_data)
        self.assertFormError(
            response, 'form', 'new_password2',
            SetPasswordForm.error_messages['password_mismatch'])

    def test_valid(self):
        """
        Test that matching passwords will be saved.
        """
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse(
            'accounts:password_reset_confirm',
            kwargs=dict(uidb64=uid, token=token))
        self.form_in_response(url)
        form_data = {'new_password1': 'newpass', 'new_password2': 'newpass'}
        response = self.client.post(url, form_data)
        self.assertRedirects(response, reverse('accounts:login'))

    def test_tampered(self):
        """
        Test that a tampered token or uid will not process.
        """
        urlname = 'accounts:password_reset_confirm'

        # invalid uid, valid token
        uid = 'invalid'
        token = default_token_generator.make_token(self.user)
        url = reverse(urlname, kwargs=dict(uidb64=uid, token=token))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # valid uid, invalid token
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = 'not-valid-token'
        url = reverse(urlname, kwargs=dict(uidb64=uid, token=token))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class PasswordChangeView(TestCaseWithUser):
    def test_get(self):
        """
        Test that the password change page contains the form.
        """
        self.login()
        self.form_in_response(reverse('accounts:password_change'))

    def test_invalid(self):
        """
        Test that non matching passwords or invalid current password will
        caught.
        """
        self.login()
        form_data = {'old_password': 'notright', 'new_password1': 'password1',
                     'new_password2': 'password2'}
        response = self.client.post(
            reverse('accounts:password_change'), form_data)
        self.assertFormError(
            response, 'form', 'old_password',
            PasswordChangeForm.error_messages['password_incorrect'])
        self.assertFormError(
            response, 'form', 'new_password2',
            PasswordChangeForm.error_messages['password_mismatch'])

    def test_valid(self):
        """
        Test that the valid passwords can be changed.
        """
        self.login()
        form_data = {'old_password': self.password, 'new_password1': 'newpass',
                     'new_password2': 'newpass'}
        response = self.client.post(
            reverse('accounts:password_change'), form_data)
        self.assertRedirects(response, reverse('accounts:password_change'))
