from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'authwall'
    env: str = 'dev'
    access_token_expire_minutes: int = 30

    redis_url: str = 'redis://redis:6379/0'
    database_url: str = 'postgresql+asyncpg://postgres:postgres@postgres:5432/authwall'

    trusted_proxies: str = '127.0.0.1,::1'
    trust_x_forwarded_for: bool = False

    firewall_backend: str = 'iptables'  # iptables | nftables | firewalld
    firewall_chain: str = 'AUTHWALL_CHAIN'
    firewall_dry_run: bool = False

    cleanup_interval_seconds: int = 5
    login_rate_limit: str = '10/minute'


settings = Settings()
