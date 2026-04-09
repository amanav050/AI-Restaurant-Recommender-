"""Phase 5: Output Display and User Experience.

Exports the Phase 5 frontend components under a phase-specific namespace.
"""

from app.web.routes import router as web_router
from pathlib import Path

# Get the path to the static files for Phase 5
def get_static_path() -> Path:
    return Path(__file__).parent / "static"

def get_template_path() -> Path:
    return get_static_path() / "index.html"

__all__ = [
    "web_router",
    "get_static_path",
    "get_template_path",
]
