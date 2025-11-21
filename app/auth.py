import logging

from fastapi import HTTPException, Request, Security, status
from fastapi.security.api_key import APIKeyHeader
from httpx import AsyncClient

from .config import HDX_AUTH_URL

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


async def get_api_key(request: Request, api_key: str = Security(api_key_header)) -> str:
    """Authorize the API key in the header through the CKAN token endpoint."""
    request.state.is_nginx_verify_request = False
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Not authenticated, please include an 'Authorization' key in the "
                "header with a valid HDX API token"
            ),
        )
    try:
        async with AsyncClient(http2=True, timeout=10) as client:
            headers = {"Authorization": api_key}
            response = await client.get(HDX_AUTH_URL, headers=headers)
            json = response.json()
            if response.is_success:
                app_name = json.get("result", {}).get("token_name")
                email_hash = json.get("result", {}).get("email_hash")
                request.state.app_name = app_name
                request.state.email_hash = email_hash
                logger.info("Application: %s, Email: %s", app_name, email_hash)
                return api_key
            logger.warning("Token validation failed: %s", json)
    except Exception as e:  # noqa: BLE001
        logger.warning("Token validation error: %s", e)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API KEY")
