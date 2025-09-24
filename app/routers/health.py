from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", description="Health Check", tags=["Health Check"])
def ping() -> dict[str, str]:
    """Endpoint to check if the service is still running."""
    return {"ping": "pong"}
