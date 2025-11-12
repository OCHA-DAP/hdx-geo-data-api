from fastapi import FastAPI, Request

from .config import DOCS_URL, OPENAPI_URL, PREFIX, REDOC_URL
from .middleware.mixpanel_tracking_middleware import mixpanel_tracking_middleware
from .routers import gdal_vector, health

routers = [health, gdal_vector]

app = FastAPI(
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL,
)


# add middleware
@app.middleware("http")
async def mixpanel_tracking_middleware_init(request: Request, call_next):
    response = await mixpanel_tracking_middleware(request, call_next)
    return response


for router in routers:
    app.include_router(router.router, prefix=PREFIX)
