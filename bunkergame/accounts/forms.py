from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(label='Имя пользователя:')
    password = forms.CharField(
        label='Пароль:',
        widget=forms.PasswordInput,
        validators=[validate_password],
        help_text='Пароль должен содержать хотя бы одну цифру'
    )

    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user