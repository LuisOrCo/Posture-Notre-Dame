from django.urls import path, include
from django.shortcuts import redirect


def root_redirect(request):
    if getattr(request, "user", None) and request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


urlpatterns = [
    path('', root_redirect, name='root'),
    path('accounts/', include('accounts.urls')),
    path('', include('accounts.urls')),
    path('', include('monitor.urls')),
]
