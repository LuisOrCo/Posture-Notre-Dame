import json
import urllib.request
import urllib.error

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_GET
from accounts.middleware import mongo_login_required as login_required


@login_required
def dashboard_view(request):
    jwt_token = request.session.get("jwt_token", "")
    context = {
        "fastapi_url": settings.FASTAPI_BASE_URL,
        "jwt_token": jwt_token,
    }
    return render(request, "monitor/dashboard.html", context)


@login_required
@require_GET
def posture_stats_view(request):
    """
    Vista proxy: consulta el endpoint /api/v1/posture-stats de FastAPI
    y retorna el JSON directamente al cliente Django (para evitar CORS).
    """
    fastapi_url = settings.FASTAPI_BASE_URL + "/api/v1/posture-stats"
    jwt_token = request.session.get("jwt_token", "")

    try:
        req = urllib.request.Request(fastapi_url, method="GET")
        req.add_header("Accept", "application/json")
        if jwt_token:
            req.add_header("Authorization", f"Bearer {jwt_token}")

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            return JsonResponse(data)

    except urllib.error.URLError as e:
        return JsonResponse(
            {"error": "No se pudo conectar con el servidor de análisis.", "detail": str(e)},
            status=502,
        )
    except Exception as e:
        return JsonResponse(
            {"error": "Error interno al consultar estadísticas.", "detail": str(e)},
            status=500,
        )

