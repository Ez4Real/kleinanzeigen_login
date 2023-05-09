from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput, required=True)