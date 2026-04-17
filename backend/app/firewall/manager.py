import logging

from app.core.config import settings
from app.firewall.base import FirewallDriver
from app.firewall.firewalld import FirewalldDriver
from app.firewall.iptables import IptablesDriver
from app.firewall.nftables import NftablesDriver
from app.firewall.windows import WindowsFirewallDriver

logger = logging.getLogger(__name__)


def get_driver() -> FirewallDriver:
    if settings.firewall_backend == 'iptables':
        return IptablesDriver()
    if settings.firewall_backend == 'nftables':
        return NftablesDriver()
    if settings.firewall_backend == 'firewalld':
        return FirewalldDriver()
    if settings.firewall_backend == 'windows':
        return WindowsFirewallDriver()
    raise ValueError(f'Unsupported firewall backend: {settings.firewall_backend}')


class FirewallManager:
    def __init__(self) -> None:
        self.driver = get_driver()

    async def bootstrap(self) -> None:
        try:
            await self.driver.bootstrap()
        except Exception as exc:  # noqa: BLE001
            logger.warning('Firewall bootstrap warning: %s', exc)

    async def startup_cleanup(self) -> None:
        try:
            await self.driver.flush_chain()
        except Exception as exc:  # noqa: BLE001
            logger.warning('Firewall cleanup warning: %s', exc)

    async def allow_ip_port(self, ip: str, port: int) -> None:
        try:
            await self.driver.allow_ip(ip, port)
        except Exception as exc:  # noqa: BLE001
            message = str(exc)
            if 'No such' in message or 'already exists' in message or 'An object already exists' in message:
                return
            raise

    async def revoke_ip_port(self, ip: str, port: int) -> None:
        try:
            await self.driver.revoke_ip(ip, port)
        except Exception as exc:  # noqa: BLE001
            message = str(exc)
            if 'Bad rule' in message or 'No such' in message or 'No rules match the specified criteria' in message:
                return
            raise
