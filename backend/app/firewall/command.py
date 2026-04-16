import asyncio
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


async def run_cmd(*cmd: str) -> None:
    if settings.firewall_dry_run:
        logger.info('DRY-RUN firewall command: %s', ' '.join(cmd))
        return
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f'Firewall command failed: {" ".join(cmd)} / {stderr.decode().strip()}')
