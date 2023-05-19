from django import forms

class reCAPTCHA(forms.Form):
    captcha_key = forms.CharField(
        max_length=254,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter the words you heard.'})
    )