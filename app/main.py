from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router as api_router
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import configure_logging
from app.web.routes import router as web_router

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router, prefix=settings.api_prefix)
app.include_router(web_router)


@app.exception_handler(AppError)
def app_error_handler(_, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details or {},
            }
        },
    )
