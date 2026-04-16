from abc import ABC, abstractmethod


class FirewallDriver(ABC):
    @abstractmethod
    async def bootstrap(self) -> None: ...

    @abstractmethod
    async def allow_ip(self, ip: str, port: int) -> None: ...

    @abstractmethod
    async def revoke_ip(self, ip: str, port: int) -> None: ...

    @abstractmethod
    async def flush_chain(self) -> None: ...
