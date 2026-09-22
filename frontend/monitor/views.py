import json
import urllib.request
import urllib.error

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_GET


@login_required
def dashboard_view(request):
    context = {
        "fastapi_url": settings.FASTAPI_BASE_URL,
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

    try:
        req = urllib.request.Request(fastapi_url, method="GET")
        req.add_header("Accept", "application/json")

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
