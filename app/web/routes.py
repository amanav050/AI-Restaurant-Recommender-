from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.core.config import get_settings

router = APIRouter(tags=["web"])


@router.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    settings = get_settings()
    template_path = Path("src/phase_5/static/index.html")
    html = template_path.read_text(encoding="utf-8")
    html = html.replace("{{ app_name }}", settings.app_name)
    html = html.replace("{{ api_prefix }}", settings.api_prefix)
    return HTMLResponse(content=html)

