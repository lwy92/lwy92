# authwall

`authwall` 是一个基于认证动态放行 IP 的零信任访问控制系统：**登录即放行、退出即移除**。

## 核心能力

- ✅ 用户认证（随机令牌 + Redis）
- ✅ 登录自动放行 IP + 指定端口（SSH/HTTP 等）
- ✅ Redis Session + TTL，超时自动清理
- ✅ PostgreSQL 用户与上下线日志持久化
- ✅ 多用户、多 IP 并发会话
- ✅ 手动下线（踢出）
- ✅ 查看当前白名单会话/IP
- ✅ 统一控制台（FastAPI + Gradio）
- ✅ 用户管理（管理员）
- ✅ OpenAPI 自动文档

## 安全设计

- **安全入口可配置**：通过 `SECURE_ENTRY_PATH` 配置统一安全入口路径（默认 `/secure`）。
- **入口密钥可配置**：通过 `SECURE_ENTRY_KEY` 配置入口密钥，Gradio 控制台每次操作都会校验。
- **安全取 IP**：默认使用 `request.client.host`，仅在 `TRUST_X_FORWARDED_FOR=true` 且来源在 `TRUSTED_PROXIES` 时信任 `X-Forwarded-For`。
- **防暴力破解**：登录接口启用限流（`10/minute`，可配置）。
- **审计日志**：会话创建/终止写入 Redis 审计流，同时用户上下线写入 PostgreSQL。

## 项目结构

```text
authwall/
├── backend/
│   ├── app/
│   │   ├── api/               # auth/sessions/users
│   │   ├── core/              # config/security/deps
│   │   ├── firewall/          # iptables/nftables/firewalld driver
│   │   ├── services/          # user/session/audit/redis
│   │   ├── ui/                # gradio 控制台
│   │   ├── workers/           # cleanup worker
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── cli/
│   ├── authwall_cli/main.py
│   └── pyproject.toml
├── deploy/docker-compose.yml
└── scripts/dev-up.sh
```

## 快速开始（Docker）

```bash
./scripts/dev-up.sh
```

服务地址：

- Backend + API + Gradio: http://localhost:8000/secure
- OpenAPI: http://localhost:8000/docs
- Health: http://localhost:8000/healthz

> 若修改 `SECURE_ENTRY_PATH`，请将以上地址中的 `/secure` 替换为你的实际配置。

## 环境变量（Backend）

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `REDIS_URL` | `redis://redis:6379/0` | Redis 地址 |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@postgres:5432/authwall` | PostgreSQL 连接串 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | 会话有效期 |
| `TRUST_X_FORWARDED_FOR` | `false` | 是否信任代理头 |
| `TRUSTED_PROXIES` | `127.0.0.1,::1` | 可信代理列表 |
| `FIREWALL_BACKEND` | `iptables` | 防火墙后端（`iptables` / `nftables` / `firewalld` / `windows`） |
| `FIREWALL_CHAIN` | `AUTHWALL_CHAIN` | 独立链名称 |
| `FIREWALL_DRY_RUN` | `false` | 调试模式，不执行系统命令 |
| `SECURE_ENTRY_PATH` | `/secure` | 安全入口路径（同时作用于 API + Gradio） |
| `SECURE_ENTRY_KEY` | `` | 安全入口密钥（空字符串表示不启用） |

## API 入口规则

安全入口路径会同时影响 API 前缀，默认路径如下：

- `POST /secure/api/v1/auth/login`
- `POST /secure/api/v1/auth/logout/{session_id}`
- `GET /secure/api/v1/sessions`
- `DELETE /secure/api/v1/sessions/{session_id}`
- `GET /secure/api/v1/users`
- `POST /secure/api/v1/users`
- `PATCH /secure/api/v1/users/{username}`
- `DELETE /secure/api/v1/users/{username}`
- `GET /secure/api/v1/users/session-logs`

## Gradio 控制台功能

Gradio 页面已覆盖每个核心接口，提供：

- 认证接口（登录/退出）
- 会话接口（查询会话/强制下线）
- 用户接口（查询/创建/更新/删除）
- 会话日志接口（按用户名过滤 + limit）

## 默认账号

首次启动自动创建管理员：

- 用户名：`admin`
- 密码：`admin123!`

> 请在生产环境首次登录后立即修改。
