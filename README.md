# authwall

`authwall` 是一个基于认证动态放行 IP 的零信任访问控制系统：**登录即放行、退出即移除**。

## 核心能力

- ✅ 用户认证（随机令牌 + Redis）
- ✅ 登录自动放行 IP + 指定端口（SSH/HTTP 等）
- ✅ Redis Session + TTL，超时自动清理
- ✅ 多用户、多 IP 并发会话
- ✅ 手动下线（踢出）
- ✅ 查看当前白名单会话/IP
- ✅ 前后端分离（FastAPI + Vue + Element Plus）
- ✅ 用户管理（管理员）
- ✅ OpenAPI 自动文档（`/docs`）

## 安全设计

- **安全取 IP**：默认使用 `request.client.host`，仅在 `TRUST_X_FORWARDED_FOR=true` 且来源在 `TRUSTED_PROXIES` 时信任 `X-Forwarded-For`。
- **防暴力破解**：登录接口启用限流（`10/minute`，可配置）。
- **审计日志**：会话创建/终止写入 Redis 审计流。
- **RBAC 预留**：用户对象含 `is_admin`，后续可扩展 role/permission 模型。

## 项目结构

```text
authwall/
├── backend/
│   ├── app/
│   │   ├── api/               # auth/sessions/users
│   │   ├── core/              # config/security/deps
│   │   ├── firewall/          # iptables/nftables/firewalld driver
│   │   ├── services/          # user/session/audit/redis
│   │   ├── workers/           # cleanup worker
│   │   ├── utils/             # secure client IP
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── cli/
│   ├── authwall_cli/main.py
│   └── pyproject.toml
├── deploy/docker-compose.yml
└── scripts/dev-up.sh
```

## 核心流程

1. 用户调用 `/api/v1/auth/login`。
2. 后端校验密码并安全识别来源 IP。
3. 创建 Redis 会话（TTL），写入过期索引 `session:expires`。
4. 调用 firewall driver 将 `ip:port` 加入独立链规则。
5. 用户退出或会话超时：后台 worker 清理规则并删除会话。

## 防火墙策略（独立链）

- **iptables**：使用 `AUTHWALL_CHAIN`（可配置）独立链。
- **nftables**：使用 `inet authwall` 表与 `input` 链。
- **firewalld**：使用 rich-rule。
- 系统启动执行链清理，避免残留规则污染。
- 操作幂等：重复加入/删除不会导致业务失败。

> 生产环境建议结合最小权限、主机基线与变更审计策略。

## 快速开始（Docker）

```bash
./scripts/dev-up.sh
```

服务地址：

- Backend: http://localhost:8000
- OpenAPI: http://localhost:8000/docs
- Frontend: http://localhost:5173

## 环境变量（Backend）

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `REDIS_URL` | `redis://redis:6379/0` | Redis 地址 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | 会话有效期 |
| `TRUST_X_FORWARDED_FOR` | `false` | 是否信任代理头 |
| `TRUSTED_PROXIES` | `127.0.0.1,::1` | 可信代理列表 |
| `FIREWALL_BACKEND` | `iptables` | 防火墙后端 |
| `FIREWALL_CHAIN` | `AUTHWALL_CHAIN` | 独立链名称 |
| `FIREWALL_DRY_RUN` | `false` | 调试模式，不执行系统命令 |

## REST API 摘要

- `POST /api/v1/auth/login` 登录并放行 IP
- `POST /api/v1/auth/logout/{session_id}` 退出并移除规则
- `GET /api/v1/sessions` 查看当前白名单会话
- `DELETE /api/v1/sessions/{session_id}` 手动下线
- `GET /api/v1/users` 管理员查看用户
- `POST /api/v1/users` 管理员创建用户

## CLI 示例

```bash
cd cli
pip install -e .

authwall-cli sessions --base-url http://localhost:8000
authwall-cli force-offline <session_id> --token <access_token>
```

## 默认账号

首次启动自动创建管理员：

- 用户名：`admin`
- 密码：`admin123!`

> 请在生产环境首次登录后立即修改。

## 开发建议

- 将 firewall driver 与策略引擎解耦（后续支持 eBPF/云防火墙）。
- 审计日志接入 ELK/Loki。
- 引入 Casbin/OPA 实现细粒度 RBAC。
- 对接 SSO（OIDC/SAML）。
