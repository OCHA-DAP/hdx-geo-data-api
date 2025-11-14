from venv import logger

import requests
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.config import HDX_URL, PREFIX

ALLOWED_API_ENDPOINTS = {
    f"{PREFIX}/healthz",
}


async def app_identifier_middleware(request: Request, call_next):
    """Middleware to check for the app_identifier in the request and add it to the request state"""
    header_identifier = request.headers.get("X-HDX-GEODATA-API-APP-IDENTIFIER")

    request.state.is_nginx_verify_request = False

    path = request.url.path

    status_code, error_message, identifier_params = _check_allow_request(
        path,
        header_identifier,
    )

    if status_code == status.HTTP_200_OK:
        request.state.app_name = identifier_params.get("app_name")
        request.state.email_hash = identifier_params.get("email_hash")
    else:
        return JSONResponse(content={"error": error_message}, status_code=status_code)

    response = await call_next(request)
    return response


def _check_allow_request(
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
            ckan_url = f"{HDX_URL}api/3/action/hdx_token_info"
            headers = {"Authorization": hdx_api_token}

            response = requests.get(ckan_url, headers=headers)

            if response.json().get("success"):
                app_name = response.json().get("result", {}).get("token_name", "")
                email_hash = response.json().get("result", {}).get("email_hash", "")
                identifier_params = {"app_name": app_name, "email_hash": email_hash}
                logger.warning(f"Application: {app_name}, Email: {email_hash}")

                return status.HTTP_200_OK, None, identifier_params
            return status.HTTP_403_FORBIDDEN, "Invalid app identifier", None

        except Exception:
            return status.HTTP_403_FORBIDDEN, "Invalid app identifier", None

    return status.HTTP_200_OK, None, None
