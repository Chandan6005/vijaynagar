from django import forms
from .models import Edition


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class EditionForm(forms.ModelForm):
    class Meta:
        model = Edition
        fields = ['title', 'edition_date', 'pdf_file', 'cover_image', 'description', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. The Daily Tribune - Morning Edition'}),
            'edition_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of this edition...'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
