from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(label='Имя пользователя:')
    password = forms.CharField(label='Пароль:', widget=forms.PasswordInput)
    

    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user