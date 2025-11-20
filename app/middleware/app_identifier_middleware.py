import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from httpx import AsyncClient

from app.config import HDX_URL, PREFIX

logger = logging.getLogger(__name__)

ALLOWED_API_ENDPOINTS = {
    f"{PREFIX}/healthz",
}


async def app_identifier_middleware(request: Request, call_next):
    """Middleware to check for the app_identifier in the request and add it to the request state"""
    header_identifier = request.headers.get("Authorization")

    request.state.is_nginx_verify_request = False

    path = request.url.path

    status_code, error_message, identifier_params = await _check_allow_request(
        path,
        header_identifier,
    )

    if status_code == status.HTTP_200_OK:
        if identifier_params is not None:
            request.state.app_name = identifier_params.get("app_name")
            request.state.email_hash = identifier_params.get("email_hash")
        else:
            request.state.app_name = None
            request.state.email_hash = None
    else:
        return JSONResponse(content={"error": error_message}, status_code=status_code)

    response = await call_next(request)
    return response


async def _check_allow_request(
    request_path: str,
    hdx_api_token: str | None,
) -> tuple[int, str | None, dict | None]:
    """Check if the request is allowed.

    Args:
        request_path: The path of the request
        hdx_api_token: The app_identifier
    Returns:
        Tuple of status code, error message and identifier parameters dictionary

    """
    if (
        request_path
        and request_path.startswith(PREFIX)
        and request_path not in ALLOWED_API_ENDPOINTS
    ):
        if not hdx_api_token:
            return status.HTTP_403_FORBIDDEN, "Missing app identifier", None

        try:
            ckan_url = f"{HDX_URL}/api/3/action/hdx_token_info"
            headers = {"Authorization": hdx_api_token}

            async with AsyncClient(timeout=10.0) as client:
                response = await client.get(ckan_url, headers=headers)
                json = response.json()

                if json.get("success"):
                    app_name = json.get("result", {}).get("token_name", "")
                    email_hash = json.get("result", {}).get("email_hash", "")
                    identifier_params = {"app_name": app_name, "email_hash": email_hash}
                    logger.info(f"Application: {app_name}, Email: {email_hash}")
                    return status.HTTP_200_OK, None, identifier_params
                logger.warning(f"Token validation failed: {json}")
                return status.HTTP_403_FORBIDDEN, "Invalid app identifier", None

        except Exception as e:
            logger.warning(f"Token validation error: {e}")
            return status.HTTP_403_FORBIDDEN, "Invalid app identifier", None

    return status.HTTP_200_OK, None, None
