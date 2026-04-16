from app.firewall.base import FirewallDriver
from app.firewall.command import run_cmd


class NftablesDriver(FirewallDriver):
    async def bootstrap(self) -> None:
        await run_cmd('nft', 'add', 'table', 'inet', 'authwall')
        await run_cmd('nft', 'add', 'chain', 'inet', 'authwall', 'input', '{ type filter hook input priority 0; }')

    async def allow_ip(self, ip: str, port: int) -> None:
        await run_cmd('nft', 'add', 'rule', 'inet', 'authwall', 'input', 'tcp', 'dport', str(port), 'ip', 'saddr', ip, 'accept')

    async def revoke_ip(self, ip: str, port: int) -> None:
        await run_cmd('nft', 'delete', 'rule', 'inet', 'authwall', 'input', 'tcp', 'dport', str(port), 'ip', 'saddr', ip, 'accept')

    async def flush_chain(self) -> None:
        await run_cmd('nft', 'flush', 'chain', 'inet', 'authwall', 'input')
