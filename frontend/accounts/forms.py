from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Contraseña"
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar contraseña"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data