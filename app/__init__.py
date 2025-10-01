from fastapi import FastAPI

from .config import PREFIX
from .routers import health
from .routers.gdal.vector import convert

routers = [health, convert]

app = FastAPI()

for router in routers:
    app.include_router(router.router, prefix=f"{PREFIX}")
    app.include_router(router.router, prefix=f"{PREFIX}/v1")
