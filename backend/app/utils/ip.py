from ipaddress import ip_address
from fastapi import Request, HTTPException

from app.core.config import settings


def _trusted_proxy_set() -> set[str]:
    return {ip.strip() for ip in settings.trusted_proxies.split(',') if ip.strip()}


def get_client_ip(request: Request) -> str:
    client_host = request.client.host if request.client else None
    if not client_host:
        raise HTTPException(status_code=400, detail='Cannot determine client IP')

    if settings.trust_x_forwarded_for:
        trusted = _trusted_proxy_set()
        if client_host in trusted:
            forwarded_for = request.headers.get('x-forwarded-for', '')
            if forwarded_for:
                raw_ip = forwarded_for.split(',')[0].strip()
                ip_address(raw_ip)
                return raw_ip
    ip_address(client_host)
    return client_host
