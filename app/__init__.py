from collections.abc import Callable

from fastapi import FastAPI, Request

from .config import DOCS_URL, OPENAPI_URL, PREFIX, REDOC_URL
from .middleware.mixpanel import mixpanel_tracking
from .routers import health, vector

routers = [health, vector]

app = FastAPI(
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL,
)


@app.middleware("http")
async def mixpanel_tracking_init(request: Request, call_next: Callable) -> Callable:
    """Track the activity of the user in Mixpanel."""
    return await mixpanel_tracking(request, call_next)


for router in routers:
    app.include_router(router.router, prefix=PREFIX)
