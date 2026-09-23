import json
import urllib.request
import urllib.error

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import RegisterForm, LoginForm


def _get_api_url(request, path: str) -> str:
    """Construye la URL absoluta para el endpoint de FastAPI."""
    base = (getattr(settings, "FASTAPI_BASE_URL", "") or "").strip()
    if base:
        return f"{base.rstrip('/')}{path}"
    # Si FASTAPI_BASE_URL está vacío en Vercel, generar la URL absoluta con el dominio actual
    return request.build_absolute_uri(path)


def _register_user_fastapi(request, username, email, password):
    """Registra el usuario en MongoDB a través del backend FastAPI."""
    url = _get_api_url(request, "/api/v1/auth/register")
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
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _login_user_fastapi(request, username, password):
    """Autentica al usuario en FastAPI contra MongoDB y obtiene el token JWT."""
    url = _get_api_url(request, "/api/v1/auth/login")
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
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("access_token")


def register_view(request):
    if getattr(request, "user", None) and request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                # 1. Registrar únicamente en MongoDB a través de FastAPI
                _register_user_fastapi(request, username, email, password)
                messages.success(request, "¡Cuenta creada exitosamente en MongoDB! Ahora puedes iniciar sesión.")
                return redirect("login")
            except urllib.error.HTTPError as e:
                try:
                    raw_content = e.read().decode("utf-8")
                    err_data = json.loads(raw_content)
                    err_msg = err_data.get("detail", raw_content or f"Error {e.code}")
                except Exception:
                    err_msg = f"Error HTTP {e.code}: {e.reason}"
                messages.error(request, err_msg)
            except Exception as e:
                messages.error(
                    request,
                    f"No se pudo conectar con el servidor de autenticación: {str(e)}"
                )
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if getattr(request, "user", None) and request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            try:
                token = _login_user_fastapi(request, username, password)
                if token:
                    request.session["jwt_token"] = token
                    request.session["username"] = username
                    messages.success(request, f"¡Bienvenido de nuevo, {username}!")
                    return redirect("dashboard")
                else:
                    messages.error(request, "Usuario o contraseña incorrectos.")
            except urllib.error.HTTPError as e:
                try:
                    raw_content = e.read().decode("utf-8")
                    err_data = json.loads(raw_content)
                    err_msg = err_data.get("detail", raw_content or f"Error {e.code}")
                except Exception:
                    err_msg = f"Error HTTP {e.code}: {e.reason}"
                messages.error(request, err_msg)
            except Exception as e:
                messages.error(request, f"Error al conectar con el servidor: {str(e)}")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    request.session.flush()
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("login")
