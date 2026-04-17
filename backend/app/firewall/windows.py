from app.core.config import settings
from app.firewall.base import FirewallDriver
from app.firewall.command import run_cmd


class WindowsFirewallDriver(FirewallDriver):
    def _rule_name(self, ip: str, port: int) -> str:
        return f'{settings.firewall_chain}_{ip}_{port}'

    async def bootstrap(self) -> None:
        return

    async def allow_ip(self, ip: str, port: int) -> None:
        await run_cmd(
            'netsh',
            'advfirewall',
            'firewall',
            'add',
            'rule',
            f'name={self._rule_name(ip, port)}',
            'dir=in',
            'action=allow',
            'protocol=TCP',
            f'remoteip={ip}',
            f'localport={port}',
        )

    async def revoke_ip(self, ip: str, port: int) -> None:
        await run_cmd(
            'netsh',
            'advfirewall',
            'firewall',
            'delete',
            'rule',
            f'name={self._rule_name(ip, port)}',
            f'remoteip={ip}',
            f'localport={port}',
            'protocol=TCP',
        )

    async def flush_chain(self) -> None:
        await run_cmd(
            'netsh',
            'advfirewall',
            'firewall',
            'delete',
            'rule',
            f'name={settings.firewall_chain}_*',
        )
