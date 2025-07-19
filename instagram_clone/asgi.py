import os
import django
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack


# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')
django.setup()

# Then import other dependencies
from channels.routing import ProtocolTypeRouter, URLRouter
import chats.routing  # This will now work properly

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chats.routing.websocket_urlpatterns
        )
    )
})

