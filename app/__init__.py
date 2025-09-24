from fastapi import FastAPI

from .config import PREFIX
from .routers import health

app = FastAPI()

for router in [health]:
    app.include_router(router.router, prefix=f"{PREFIX}", tags=["Default"])
    app.include_router(router.router, prefix=f"{PREFIX}/latest", tags=["Latest"])
    app.include_router(router.router, prefix=f"{PREFIX}/v1", tags=["Version 1"])
