from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)

class RegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields = ['username','email','password1','password2'] 

class UpdateUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput())
    last_name = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput())
    email = forms.EmailField(required=True,
                             widget=forms.TextInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class JambonzForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    password1.label = "Password"
    password2.label = "Confirm Password"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(JambonzForm, self).__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        cd = self.cleaned_data
        print(self.request)
        password1 = cd.get('password1')
        password2 = cd.get('password2')
        username = cd.get('username')
        if (password2 != password1):
            raise ValidationError("Passwords do not match")
        if not(8 <= len(password1) <= 20):
            raise ValidationError("Password must be between 8 and 20 chars")
        if (username != self.request.user.username):
            raise ValidationError("Incorrect Username")
        
        return cd



