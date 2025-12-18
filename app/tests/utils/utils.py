# ruff: noqa: ANN002, ANN003, ARG001, S107
from collections.abc import Callable
from unittest.mock import AsyncMock, MagicMock


def create_mock_hdx_response(
    token_name: str = "testapp",
    email_hash: str = "email-hash",
    *,
    is_success: bool = True,
) -> MagicMock:
    """Create a mock HDX response for testing.

    Args:
        token_name: The app/token name from HDX
        email_hash: The hashed email from HDX
        is_success: Whether the response represents a successful HDX call

    Returns:
        A MagicMock that behaves like httpx.Response with a json() method and is_success
        property

    """
    response_mock = MagicMock()
    response_mock.is_success = is_success

    if is_success:
        response_mock.json.return_value = {
            "result": {"token_name": token_name, "email_hash": email_hash},
        }
    else:
        response_mock.json.return_value = {"error": "token not found"}

    return response_mock


def create_mock_hdx_client(
    token_name: str = "testapp",
    email_hash: str = "email-hash",
    *,
    is_success: bool = True,
) -> Callable[[], AsyncMock]:
    """Create a mock HDX AsyncClient factory for testing.

    Returns a factory function that creates mock clients compatible with @patch
    decorator. The returned mock can be used with `async with AsyncClient()` syntax.

    Usage in tests:
        @patch("app.auth.AsyncClient", new_callable=create_mock_hdx_client)

    Args:
        token_name: The app/token name from HDX
        email_hash: The hashed email from HDX
        is_success: Whether the HDX authentication succeeds

    Returns:
        A callable factory that returns a mock AsyncClient usable as an async context
        manager

    """

    def factory(*args, **kwargs) -> AsyncMock:
        # Create the response mock
        response_mock = create_mock_hdx_response(
            token_name=token_name,
            email_hash=email_hash,
            is_success=is_success,
        )

        # Create the client mock with async context manager support
        client_mock = AsyncMock()
        client_mock.get.return_value = response_mock

        # Make the client itself work as an async context manager
        client_mock.__aenter__.return_value = client_mock
        client_mock.__aexit__.return_value = None

        return client_mock

    return factory
