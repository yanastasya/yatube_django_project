import django.contrib.auth.views as Auth
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'),
    path(
        'login/',
        Auth.LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'logout/',
        Auth.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'password_reset/done/',
        Auth.PasswordResetDoneView.as_view
        (template_name='users/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'password_reset/',
        Auth.PasswordResetView.as_view
        (template_name='users/password_reset_form.html'),
        name='password_reset_form'
    ),
    path(
        'reset/done/',
        Auth.PasswordResetCompleteView.as_view
        (template_name='users/password_reset_complete.html'),
        name='password_reset_complete'
    ),
    path(
        'reset/<uidb64>/<token>/',
        Auth.PasswordResetConfirmView.as_view
        (template_name='users/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'password_change/',
        Auth.PasswordChangeView.as_view
        (template_name='users/password_change_form.html'),
        name='password_change_form'
    ),
    path(
        'password_change/done/',
        Auth.PasswordChangeDoneView.as_view
        (template_name='users/password_change_done.html'),
        name='password_change_done'
    ),
]
