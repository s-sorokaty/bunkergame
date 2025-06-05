from django import forms
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(label='Имя пользователя:')
    password = forms.CharField(
        label='Пароль:',
        widget=forms.PasswordInput,

    )

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        if not pwd:
            return pwd

        try:
            # здесь запускаем все валидаторы из AUTH_PASSWORD_VALIDATORS
            validate_password(pwd, self.instance)
        except DjangoValidationError as e:
            ru_messages = []
            for msg in e.messages:
                if 'too short' in msg:
                    ru_messages.append(
                        'Пароль слишком короткий. Он должен содержать не менее 8 символов.'
                    )
                elif 'too common' in msg:
                    ru_messages.append(
                        'Пароль слишком простой.'
                    )
                elif 'entirely numeric' in msg:
                    ru_messages.append(
                        'Пароль не может состоять только из цифр.'
                    )
                else:
                    # остальные оставим как есть или переведём по аналогии
                    ru_messages.append(msg)
            raise forms.ValidationError(ru_messages)

        return pwd

    def save(self, request, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            login(request, user)
        return user
