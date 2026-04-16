import asyncio
import logging

from app.core.config import settings
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)


async def cleanup_worker(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        cleaned = await SessionService.cleanup_expired()
        if cleaned:
            logger.info('cleanup worker revoked %s expired session(s)', cleaned)
        await asyncio.sleep(settings.cleanup_interval_seconds)
