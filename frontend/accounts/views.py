import json
import urllib.request
import urllib.error

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from .forms import RegisterForm, LoginForm


def _register_user_fastapi(username, email, password):
    """Registra el usuario en MongoDB a través del backend FastAPI."""
    url = f"{settings.FASTAPI_BASE_URL}/api/v1/auth/register"
    payload = json.dumps({
        "username": username,
        "email": email,
        "password": password
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _login_user_fastapi(username, password):
    """Autentica al usuario en FastAPI y obtiene el token JWT."""
    url = f"{settings.FASTAPI_BASE_URL}/api/v1/auth/login"
    payload = json.dumps({
        "username": username,
        "password": password
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("access_token")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            if User.objects.filter(username=username).exists():
                messages.error(request, "El nombre de usuario ya está registrado.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "El correo electrónico ya está registrado.")
            else:
                try:
                    # 1. Registrar en MongoDB a través de FastAPI
                    _register_user_fastapi(username, email, password)
                except urllib.error.HTTPError as e:
                    try:
                        err_data = json.loads(e.read().decode("utf-8"))
                        err_msg = err_data.get("detail", "Error en el servidor de autenticación.")
                    except Exception:
                        err_msg = "Error al registrar en la base de datos."
                    messages.error(request, err_msg)
                    return render(request, "accounts/register.html", {"form": form})
                except Exception as e:
                    messages.warning(
                        request,
                        f"Advertencia: No se pudo sincronizar inmediatamente con la API: {str(e)}"
                    )

                # 2. Registrar en Django
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                messages.success(request, "¡Cuenta creada exitosamente en la base de datos! Ahora puedes iniciar sesión.")
                return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                # Obtener token JWT de FastAPI / MongoDB
                try:
                    token = _login_user_fastapi(username, password)
                    request.session["jwt_token"] = token
                except urllib.error.HTTPError as e:
                    # Si el usuario existía en Django antes de MongoDB, auto-sincronizarlo
                    if e.code in (400, 401, 404):
                        try:
                            _register_user_fastapi(username, user.email or f"{username}@example.com", password)
                            token = _login_user_fastapi(username, password)
                            request.session["jwt_token"] = token
                        except Exception:
                            pass
                except Exception:
                    pass

                messages.success(request, f"¡Bienvenido de nuevo, {user.username}!")
                return redirect("dashboard")
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    request.session.pop("jwt_token", None)
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("login")

