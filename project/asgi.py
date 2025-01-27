import os
from django.core.asgi import get_asgi_application
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
#application = get_asgi_application()
django_asgi_app = get_asgi_application()  # 通常のHTTPリクエストを処理する

import app.routing # なぜかこの行を上の行の後にしないといけない
application = ProtocolTypeRouter( {
    'http': get_asgi_application(),
    'websocket': URLRouter( app.routing.websocket_urlpatterns ),
} )