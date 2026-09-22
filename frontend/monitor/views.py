from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings


@login_required
def dashboard_view(request):
    context = {
        "fastapi_url": settings.FASTAPI_BASE_URL,
    }
    return render(request, "monitor/dashboard.html", context)
