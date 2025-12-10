from collections.abc import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import DOCS_URL, OPENAPI_URL, PREFIX, REDOC_URL
from .docs import app_description
from .middleware.mixpanel import mixpanel_tracking
from .routers import health, vector

routers = [vector, health]

app = FastAPI(
    description=app_description,
    docs_url=DOCS_URL,
    openapi_url=OPENAPI_URL,
    redoc_url=REDOC_URL,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def mixpanel_tracking_init(request: Request, call_next: Callable) -> Callable:
    """Track the activity of the user in Mixpanel."""
    return await mixpanel_tracking(request, call_next)


for router in routers:
    app.include_router(router.router, prefix=PREFIX)
