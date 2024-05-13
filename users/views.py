from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import LoginForm, RegisterForm, UpdateUserForm, JambonzForm
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from verify_email.email_handler import send_verification_email
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests


def redirect_after_login(request):
    nxt = request.GET.get("next", None)
    if nxt is None:
        return redirect('/')
    elif not url_has_allowed_host_and_scheme(
            url=nxt,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure()):
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return redirect(nxt)

def sign_in(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request,'users/login.html', {'form': form})
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].lower()
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user:
                login(request, user)
                return redirect_after_login(request)
        # form is not valid or user is not authenticated
        messages.error(request,f'Invalid username or password')
        return render(request,'users/login.html',{'form': form})

def sign_out(request):
    logout(request)
    messages.success(request,f'You have been logged out.')
    return redirect('login')    


def sign_up(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'users/register.html', { 'form': form})   
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = send_verification_email(request, form)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'Please check your email for a verification message.')
            return redirect('login')
        else:
            return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    # could this use form instead of user_form, and use the new form template?
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect('profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
    return render(request, 'users/profile.html', {'user_form': user_form})


@login_required
def jambonz(request):
    if request.method == 'GET':
        form = JambonzForm(initial={"username": request.user.username})
        description = 'Use this form to create or update your account on the Jambonz platform, setting the password here for an existing account will change the password in Jambonz.<ul><li>Your username will be the same as this platform.<li>Your password must be between 8 and 20 characters<li>You can access Jambonz at <a href="https://jambonz.poc.emf.camp">jambonz.poc.emf.camp</a></ul>'
        return render(request, 'form.html', { 'form': form, 'title' :'Set Jambonz Password', 'description' : description})   
    if request.method == 'POST':
        form = JambonzForm(request.POST, request=request)
        if form.is_valid():
            data = {}
            data['username'] = form.cleaned_data['username']
            data['password'] = form.cleaned_data['password1']
            headers = {'token': settings.HOOKDECK_TOKEN}
            url = settings.HOOKDECK_URL+'/jambonz'
            r = requests.post(url, headers=headers, data=data)
            messages.success(request, 'Request Sent.')
            return redirect('profile')
        else:
            return render(request, 'form.html', {'form': form})    


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')
    from_email= 'poc@emfcamp.org'


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = '/profile'

