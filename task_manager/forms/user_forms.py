from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password','email']

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username',
            'class': 'input-field',
            'required': 'required'
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email',
            'class': 'input-field',
            'required': 'required'
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Password',
            'class': 'input-field',
            'required': 'required'
        })

    def save(self, commit=True):
        user = super().save(commit=False) #saveaza local ca sa poata cripta parola
        user.set_password(self.cleaned_data['password'])  # hash-uiește parola
        if commit:
            user.save()
        return user