from app.core.config import settings
from app.firewall.base import FirewallDriver
from app.firewall.command import run_cmd


class IptablesDriver(FirewallDriver):
    async def bootstrap(self) -> None:
        await run_cmd('iptables', '-N', settings.firewall_chain)
        await run_cmd('iptables', '-C', 'INPUT', '-j', settings.firewall_chain)

    async def allow_ip(self, ip: str, port: int) -> None:
        await run_cmd(
            'iptables',
            '-C',
            settings.firewall_chain,
            '-p',
            'tcp',
            '-s',
            ip,
            '--dport',
            str(port),
            '-j',
            'ACCEPT',
        )
        await run_cmd(
            'iptables',
            '-A',
            settings.firewall_chain,
            '-p',
            'tcp',
            '-s',
            ip,
            '--dport',
            str(port),
            '-j',
            'ACCEPT',
        )

    async def revoke_ip(self, ip: str, port: int) -> None:
        await run_cmd(
            'iptables',
            '-D',
            settings.firewall_chain,
            '-p',
            'tcp',
            '-s',
            ip,
            '--dport',
            str(port),
            '-j',
            'ACCEPT',
        )

    async def flush_chain(self) -> None:
        await run_cmd('iptables', '-F', settings.firewall_chain)
