from functools import wraps
from django.shortcuts import redirect


class MongoSessionUser:
    """Representa el usuario autenticado a través de MongoDB y JWT."""
    def __init__(self, username: str, is_authenticated: bool = True):
        self.username = username
        self.is_authenticated = is_authenticated

    def __str__(self):
        return self.username or "AnonymousUser"


class AnonymousMongoUser:
    """Representa un usuario anónimo (sin sesión activa)."""
    username = ""
    is_authenticated = False

    def __str__(self):
        return "AnonymousUser"


class MongoAuthMiddleware:
    """
    Middleware que asocia request.user según el JWT y username
    guardados en la sesión firmada (signed cookies), sin consultar bases de datos SQL.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        jwt_token = request.session.get("jwt_token")
        username = request.session.get("username")

        if jwt_token and username:
            request.user = MongoSessionUser(username=username, is_authenticated=True)
        else:
            request.user = AnonymousMongoUser()

        return self.get_response(request)


def mongo_login_required(view_func):
    """Decorador para proteger vistas que requieren autenticación con MongoDB."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
