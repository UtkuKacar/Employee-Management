"""
ASGI config for employee_management project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from core.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')

application = ProtocolTypeRouter({
    # HTTP istekleri için Django'nun standart uygulamasını kullan
    "http": get_asgi_application(),

    # WebSocket istekleri için AuthMiddlewareStack kullanarak yönlendirme yap
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)  # WebSocket URL'lerini yönlendiren routing dosyasını ekle
    ),
})
