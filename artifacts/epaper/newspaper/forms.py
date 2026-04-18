from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class EditionForm(forms.Form):
    """Form for uploading editions with Cloudinary file handling"""
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. The Daily Tribune - Morning Edition'})
    )
    edition_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    pdf_file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),
        help_text='Upload a PDF (max 100 MB)'
    )
    cover_image = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        help_text='Upload a cover image (optional)'
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of this edition...'}),
    )
    is_published = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Publish immediately'
    )


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
        }
