from backend.platform import build_app

from .routes import register
from .settings import settings

app = build_app(settings, routers=[register])
