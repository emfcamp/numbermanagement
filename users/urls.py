from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import include

urlpatterns = [
    path('login/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('register/', views.sign_up, name='register'),
    path('password-reset/', views.ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    path('password-change/', views.ChangePasswordView.as_view(), name='password_change'),
    path('profile/', views.profile, name='profile'),
    path('verification/', include('verify_email.urls')),
    path('jambonz/', views.jambonz, name='jambonz'),
]