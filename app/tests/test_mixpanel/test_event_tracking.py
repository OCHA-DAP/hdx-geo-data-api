# ruff: noqa: ANN001, ARG001, PLR0913, S101, S108
from unittest.mock import patch

import pytest
from fastapi import status

from app.tests.utils.utils import create_mock_hdx_client

HEALTH_ENDPOINT = "/api/healthz"
VECTOR_INFO_ENDPOINT = "/api/vector/info"
VISITOR_HASH = "visitor-hash-123"
USER_HASH = "user-hash-456"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
IP_ADDRESS = "192.168.1.1"


@pytest.mark.asyncio
@patch("app.middleware.utils.HashCodeGenerator.compute_hash", return_value=VISITOR_HASH)
@patch("app.middleware.utils.send_mixpanel_event")
async def test_unauthenticated_request_creates_mixpanel_event(
    mock_mixpanel,
    mock_hash,
    async_client,
) -> None:
    """Unauthenticated request should create a Mixpanel event with visitor hash."""
    headers = {"User-Agent": USER_AGENT, "x-forwarded-for": IP_ADDRESS}

    response = await async_client.get(HEALTH_ENDPOINT, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert mock_mixpanel.call_count == 1

    event_name, distinct_id, _ = mock_mixpanel.call_args[0]
    assert event_name == "geodata api call"
    assert distinct_id == VISITOR_HASH


@pytest.mark.asyncio
@patch("app.middleware.utils.HashCodeGenerator.compute_hash", return_value=VISITOR_HASH)
@patch("app.middleware.utils.send_mixpanel_event")
async def test_unauthenticated_request_event_includes_request_metadata(
    mock_mixpanel,
    mock_hash,
    async_client,
) -> None:
    """Unauthenticated request event test.

    Should include endpoint, response code, and request info.
    """
    headers = {"User-Agent": USER_AGENT, "x-forwarded-for": IP_ADDRESS}

    await async_client.get(HEALTH_ENDPOINT, headers=headers)

    _, _, event_payload = mock_mixpanel.call_args[0]

    # Verify request metadata is present
    assert event_payload.get("endpoint path") == HEALTH_ENDPOINT
    assert event_payload.get("request type") == "standard"
    assert event_payload.get("server side")
    assert event_payload.get("response code") == status.HTTP_200_OK
    assert event_payload.get("ip") == IP_ADDRESS
    assert event_payload.get("user agent") == USER_AGENT

    # Verify no auth metadata for unauthenticated request
    assert event_payload.get("app name") is None
    assert event_payload.get("email hash") is None


@pytest.mark.asyncio
@patch("app.auth.AsyncClient", new_callable=create_mock_hdx_client)
@patch("app.routers.vector_utils.download_resource", return_value="/tmp/test.geojson")
@patch("app.routers.vector_utils.run_command_and_check", return_value="[]")
@patch("app.middleware.utils.HashCodeGenerator.compute_hash", return_value=USER_HASH)
@patch("app.middleware.utils.send_mixpanel_event")
async def test_authenticated_request_event_includes_hdx_metadata(
    mock_mixpanel,
    mock_hash,
    mock_run_cmd,
    mock_download,
    mock_hdx_client,
    async_client,
) -> None:
    """Authenticated request event should include HDX user metadata."""
    headers = {
        "Authorization": "valid-hdx-token",
        "User-Agent": USER_AGENT,
        "x-forwarded-for": IP_ADDRESS,
    }
    query_params = {"input": "resource-id-123"}

    response = await async_client.get(
        VECTOR_INFO_ENDPOINT,
        params=query_params,
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK

    _, _, event_payload = mock_mixpanel.call_args[0]
    assert event_payload.get("app name") == "testapp"
    assert event_payload.get("email hash") == "email-hash"


@pytest.mark.asyncio
@patch("app.auth.AsyncClient", new_callable=create_mock_hdx_client)
@patch("app.routers.vector_utils.download_resource", return_value="/tmp/test.geojson")
@patch("app.routers.vector_utils.run_command_and_check", return_value="[]")
@patch("app.middleware.utils.HashCodeGenerator.compute_hash", return_value=USER_HASH)
@patch("app.middleware.utils.send_mixpanel_event")
async def test_authenticated_request_event_includes_request_metadata(
    mock_mixpanel,
    mock_hash,
    mock_run_cmd,
    mock_download,
    mock_hdx_client,
    async_client,
) -> None:
    """Authenticated request event should include all request metadata."""
    headers = {
        "Authorization": "valid-hdx-token",
        "User-Agent": USER_AGENT,
        "x-forwarded-for": IP_ADDRESS,
    }
    query_params = {"input": "resource-id-123", "limit": "10"}

    await async_client.get(VECTOR_INFO_ENDPOINT, params=query_params, headers=headers)

    _, _, event_payload = mock_mixpanel.call_args[0]
    assert event_payload.get("endpoint path") == VECTOR_INFO_ENDPOINT
    assert event_payload.get("request type") == "standard"
    assert event_payload.get("server side")
    assert event_payload.get("response code") == status.HTTP_200_OK
    assert event_payload.get("ip") == IP_ADDRESS
    assert event_payload.get("user agent") == USER_AGENT
    assert event_payload.get("query params") == ["input", "limit"]
    assert event_payload.get("resource id") == "resource-id-123"


@pytest.mark.asyncio
@patch("app.middleware.utils.send_mixpanel_event")
async def test_docs_endpoint_excluded_from_tracking(
    mock_mixpanel,
    async_client,
) -> None:
    """Docs endpoint should not be tracked by Mixpanel."""
    docs_endpoint = "/docs"

    response = await async_client.get(docs_endpoint)

    assert response.status_code == status.HTTP_200_OK
    assert mock_mixpanel.call_count == 0
