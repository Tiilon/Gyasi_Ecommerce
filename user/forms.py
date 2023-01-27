
from django.contrib.auth import authenticate
from django import forms
from user.models import User, UserProfile
from django.utils.translation import gettext, gettext_lazy as _

class LoginForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['email', 'password']

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid login credentials.")

class CreateAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']

class CreateUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name','last_name','other_name']

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name','last_name','other_name', 'phone', 'date_of_birth']



class UploadProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']

class SetPasswordForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password2', widget=forms.PasswordInput)

    def clean(self):
        if 'password' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields did not match."))
        return self.cleaned_data 

    class Meta:
        model = User
        fields = ["password"]


class UpdateUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']