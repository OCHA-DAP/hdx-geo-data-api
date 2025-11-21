import logging
from collections.abc import Callable

from fastapi import BackgroundTasks, Request, Response

from ..config import PREFIX, mixpanel
from .utils import track_api_call

logger = logging.getLogger(__name__)


async def mixpanel_tracking(request: Request, call_next: Callable) -> Response:
    """Middleware to track Mixpanel events."""
    response = await call_next(request)
    if not mixpanel:
        logger.error("MIXPANEL_TOKEN environment variable is not set.")
    if request.url.path.startswith(PREFIX):
        background_tasks = BackgroundTasks()
        background_tasks.add_task(track_api_call, request, response)
        response.background = background_tasks
    return response
