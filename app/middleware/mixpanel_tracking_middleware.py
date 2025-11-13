import logging

from fastapi import BackgroundTasks, Request

from app.config import MIXPANEL, PREFIX
from app.middleware.util.util import track_api_call

logger = logging.getLogger(__name__)


async def mixpanel_tracking_middleware(request: Request, call_next):
    """Middleware to track Mixpanel events"""
    background_tasks = BackgroundTasks()

    response = await call_next(request)

    if MIXPANEL:
        if request.url.path.startswith(PREFIX):
            background_tasks.add_task(track_api_call, request, response)
    else:
        logger.warning("MIXPANEL_TOKEN environment variable is not set.")
    response.background = background_tasks

    return response
