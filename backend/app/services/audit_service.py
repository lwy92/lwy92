import json
from datetime import datetime, timezone

from app.services.redis_client import redis


class AuditService:
    @staticmethod
    async def log(event: str, payload: dict) -> None:
        record = {'event': event, 'payload': payload, 'ts': datetime.now(timezone.utc).isoformat()}
        await redis.lpush('audit:events', json.dumps(record))
        await redis.ltrim('audit:events', 0, 999)
