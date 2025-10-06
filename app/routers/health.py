from fastapi import APIRouter

router = APIRouter(tags=["Health Check"])


@router.get("/healthz")
def health_check() -> dict[str, str]:
    """Endpoint to check if the service is still running."""
    return {"ping": "pong"}
