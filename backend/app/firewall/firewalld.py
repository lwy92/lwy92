from app.firewall.base import FirewallDriver
from app.firewall.command import run_cmd


class FirewalldDriver(FirewallDriver):
    async def bootstrap(self) -> None:
        return

    async def allow_ip(self, ip: str, port: int) -> None:
        await run_cmd('firewall-cmd', '--permanent', '--add-rich-rule', f'rule family="ipv4" source address="{ip}" port protocol="tcp" port="{port}" accept')
        await run_cmd('firewall-cmd', '--reload')

    async def revoke_ip(self, ip: str, port: int) -> None:
        await run_cmd('firewall-cmd', '--permanent', '--remove-rich-rule', f'rule family="ipv4" source address="{ip}" port protocol="tcp" port="{port}" accept')
        await run_cmd('firewall-cmd', '--reload')

    async def flush_chain(self) -> None:
        return
