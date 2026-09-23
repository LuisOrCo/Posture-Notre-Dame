from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
        label="Nombre de usuario",
        max_length=50,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo electrónico"}),
        label="Correo electrónico",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"}),
        label="Contraseña",
        min_length=6,
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirmar contraseña"}),
        label="Confirmar contraseña",
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
        label="Nombre de usuario"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"}),
        label="Contraseña"
    )