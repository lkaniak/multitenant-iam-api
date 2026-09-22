from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from config import APP_VERSION, settings
from entities.exceptions.app_exception import AppException
from entities.exceptions.multiple_exception import MultipleExceptions
from presentation.handler import exception_handler, not_found_error
from presentation.middleware.tracking_middleware import TrackingRequestMiddleware
from presentation.routers import (
    auth_router,
    organization_router,
    user_router,
    my_user_router,
    my_organization_router,
    organization_user_groups_router,
    alert_router,
)

app = FastAPI(
    title="Multitenant IAM API", version=APP_VERSION, root_path=f"/{settings.API_VERSION}"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)
app.add_middleware(TrackingRequestMiddleware)

logger.info("Starting application")


app.add_exception_handler(404, not_found_error)
app.add_exception_handler(AppException, exception_handler)
app.add_exception_handler(MultipleExceptions, exception_handler)

app.include_router(**user_router)
app.include_router(**auth_router)
app.include_router(**organization_router)
app.include_router(**my_user_router)
app.include_router(**my_organization_router)
app.include_router(**organization_user_groups_router)
app.include_router(**alert_router)


if __name__ == "__main__" and settings.DEBUG:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
