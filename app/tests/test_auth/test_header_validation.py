# ruff: noqa: ANN001, ARG001, S101
from unittest.mock import patch

import pytest
from fastapi import status

from app.tests.utils.utils import create_mock_hdx_client

VECTOR_INFO_ENDPOINT = "/api/vector/info"
QUERY_PARAMS = {"input": "resource-id-123"}
VALID_AUTH_HEADER = {"Authorization": "valid-api-token"}
MISSING_AUTH_HEADER = {}


@pytest.mark.asyncio
@patch("app.auth.AsyncClient", new_callable=create_mock_hdx_client)
@patch("app.routers.vector_utils.run_command_and_check", return_value="[]")
@patch("app.routers.vector_utils.download_resource", return_value="dummy")
@patch("app.middleware.utils.send_mixpanel_event")
async def test_valid_authorization_header_allows_request(
    mock_mixpanel,
    mock_download,
    mock_run_cmd,
    mock_hdx_client,
    async_client,
) -> None:
    """Valid Authorization header should allow request and return 200."""
    response = await async_client.get(
        VECTOR_INFO_ENDPOINT,
        params=QUERY_PARAMS,
        headers=VALID_AUTH_HEADER,
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
@patch("app.auth.AsyncClient", new_callable=create_mock_hdx_client)
@patch("app.routers.vector_utils.run_command_and_check", return_value="[]")
@patch("app.routers.vector_utils.download_resource", return_value="dummy")
@patch("app.middleware.utils.send_mixpanel_event")
async def test_valid_auth_header_populates_hdx_metadata(
    mock_mixpanel,
    mock_download,
    mock_run_cmd,
    mock_hdx_client,
    async_client,
) -> None:
    """Valid auth header should populate request with HDX user metadata."""
    await async_client.get(
        VECTOR_INFO_ENDPOINT,
        params=QUERY_PARAMS,
        headers=VALID_AUTH_HEADER,
    )

    # Verify Mixpanel was called with HDX metadata
    assert mock_mixpanel.call_count == 1
    _event_name, _distinct_id, event_payload = mock_mixpanel.call_args[0]

    assert event_payload.get("app name") == "testapp"
    assert event_payload.get("email hash") == "email-hash"


@pytest.mark.asyncio
async def test_missing_authorization_header_returns_401(async_client) -> None:
    """Missing Authorization header should return 401 Unauthorized."""
    response = await async_client.get(
        VECTOR_INFO_ENDPOINT,
        params=QUERY_PARAMS,
        headers=MISSING_AUTH_HEADER,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_detail = response.json().get("detail", "")
    assert "Not authenticated" in error_detail


@pytest.mark.asyncio
@patch(
    "app.auth.AsyncClient",
    new_callable=lambda: create_mock_hdx_client(is_success=False),
)
@patch("app.routers.vector_utils.run_command_and_check", return_value="[]")
@patch("app.routers.vector_utils.download_resource", return_value="dummy")
async def test_invalid_hdx_token_returns_403(
    mock_download,
    mock_run_cmd,
    mock_hdx_client,
    async_client,
) -> None:
    """Invalid HDX token should return 403 Forbidden."""
    response = await async_client.get(
        VECTOR_INFO_ENDPOINT,
        params=QUERY_PARAMS,
        headers=VALID_AUTH_HEADER,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    error_detail = response.json().get("detail", "")
    assert error_detail == "Invalid API KEY"
