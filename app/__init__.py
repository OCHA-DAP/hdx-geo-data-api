from fastapi import FastAPI

from .config import PREFIX
from .routers import gdal_vector, health

routers = [health, gdal_vector]

app = FastAPI()

for router in routers:
    app.include_router(router.router, prefix=f"{PREFIX}")
