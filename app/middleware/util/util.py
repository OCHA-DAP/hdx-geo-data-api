import hashlib
import time
from urllib.parse import parse_qs, unquote, urlparse
from venv import logger

import ua_parser.user_agent_parser as useragent
from fastapi import Request, Response

from app.config import MIXPANEL


async def track_api_call(request: Request, response: Response):
    is_nginx_verify_request = getattr(request.state, "is_nginx_verify_request", False)

    if is_nginx_verify_request:
        endpoint, query_params_keys, current_url = _parse_nginx_header(request)
    else:
        endpoint, query_params_keys, current_url = _parse_fastapi_request(request)

    user_agent_string = request.headers.get("user-agent", "")
    ip_address = request.headers.get("x-forwarded-for", "")
    response_code = response.status_code

    distinct_id = HashCodeGenerator(
        {"ip": ip_address, "ua": user_agent_string},
    ).compute_hash()
    event_time = time.time()

    ua_os, ua_browser, ua_browser_version = _parse_user_agent(user_agent_string)

    mixpanel_dict = {
        "endpoint path": endpoint,
        "query params": query_params_keys,
        "time": event_time,
        "request type": "nginx" if is_nginx_verify_request else "standard",
        "server side": True,
        "response code": response_code,
        "user agent": user_agent_string,
        "ip": ip_address,
        "$os": ua_os,
        "$browser": ua_browser,
        "$browser_version": ua_browser_version,
        "$current_url": current_url,
    }
    await send_mixpanel_event("geodata api call", distinct_id, mixpanel_dict)


async def send_mixpanel_event(event_name: str, distinct_id: str, event_data: dict):
    MIXPANEL.track(distinct_id, event_name, event_data)


def extract_path_identifier_and_query_params(
    original_url: str,
) -> tuple[str, str | None, dict]:
    """Extract the path and query parameters from the Nginx header.

    Args:
        original_url: The original URL from the Nginx header
    Returns:
        Tuple of path and query parameters

    """
    parsed_url = urlparse(original_url)
    path = parsed_url.path
    query_params = parse_qs(parsed_url.query)
    return path, query_params


def _parse_fastapi_request(request: Request) -> tuple[str, list[str], str, str, str]:
    """Parse the FastAPI request to extract data needed for analytics.

    Args:
        request: The FastAPI request object

    Returns:
        Tuple containing endpoint, query_params_keys and current_url

    """
    endpoint = request.url.path

    query_params_keys = list(request.query_params.keys())

    current_url = unquote(str(request.url))

    return endpoint, query_params_keys, current_url


def _parse_nginx_header(request: Request) -> tuple[str, list[str], str, str, str]:
    """Parse nginx headers to extract data needed for analytics.

    Args:
        request: The FastAPI request object.

    Returns:
        Tuple containing endpoint, query_params_keys and current_url

    """
    original_uri_from_nginx = request.headers.get("X-Original-URI")
    assert original_uri_from_nginx is not None
    endpoint, query_params = extract_path_identifier_and_query_params(
        original_uri_from_nginx,
    )

    query_params_keys = list(query_params.keys())

    protocol = request.headers.get("x-forwarded-proto", "")
    host = request.headers.get("x-forwarded-host", "")
    current_url = unquote(f"{protocol}://{host}{original_uri_from_nginx}")

    return endpoint, query_params_keys, current_url


def _parse_user_agent(
    user_agent: str,
) -> tuple[str | None, str | None, str | None]:
    """Parse the user agent string to extract the operating system, browser, and browser version.

    Args:
        user_agent: The user agent string to be parsed

    Returns:
        A tuple containing the operating system, browser, and browser version

    """
    ua_dict = useragent.Parse(user_agent)
    ua_os = ua_dict.get("os", {}).get("family")
    ua_browser = ua_dict.get("user_agent", {}).get("family")
    ua_browser_version = ua_dict.get("user_agent", {}).get("major")

    return ua_os, ua_browser, ua_browser_version


class HashCodeGenerator:
    """Works only on simple dictionaries (not nested). At least the specified fields need to not be nested."""

    def __init__(self, src_dict, field_list=None):
        if not field_list and src_dict:
            field_list = list(src_dict.keys())

        assert field_list is not None
        field_list.sort()
        try:
            self.__inner_string = ""
            if field_list and src_dict:
                for field in field_list:
                    self.__inner_string += f"{field}-{src_dict.get(field)},"
            else:
                raise Exception("Either field list or source dict are null")
        except Exception:
            raise Exception("Exception while trying to generate hash code")

    def compute_hash(self):
        hash_builder = hashlib.md5()
        hash_builder.update(self.__inner_string.encode())
        hash_code = hash_builder.hexdigest()
        logger.debug(
            f"Generated code for {self.__inner_string} is {hash_code}",
        )
        return hash_code
