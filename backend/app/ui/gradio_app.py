import json
from datetime import timedelta

import gradio as gr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import AccessTokenService, verify_password
from app.db import AsyncSessionLocal
from app.services.session_service import SessionService
from app.services.user_service import UserService
from app.services.user_session_log_service import UserSessionLogService


def _parse_ports(raw: str) -> list[int]:
    text = (raw or '').strip()
    if not text:
        return [22]

    ports: list[int] = []
    for part in text.split(','):
        item = part.strip()
        if not item:
            continue
        port = int(item)
        if port <= 0 or port > 65535:
            raise ValueError(f'非法端口: {port}')
        ports.append(port)

    if not ports:
        return [22]
    return ports


async def _get_current_user_by_token(token: str, db: AsyncSession) -> dict:
    username = await AccessTokenService.get_subject(token)
    if not username:
        raise ValueError('Token 无效或已过期，请重新登录')

    user = await UserService.get_user(db, username)
    if not user:
        raise ValueError('用户不存在或已失效')
    return user


def _require_entry_key(key: str) -> None:
    expected = settings.secure_entry_key.strip()
    if expected and key.strip() != expected:
        raise ValueError('安全入口验证失败，请检查入口密钥')


def _pretty(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


async def login(entry_key: str, username: str, password: str, ports: str):
    _require_entry_key(entry_key)
    ports_value = _parse_ports(ports)

    async with AsyncSessionLocal() as db:
        user = await UserService.get_user(db, username)
        if not user or not user['is_active'] or not verify_password(password, user['password_hash']):
            raise ValueError('用户名或密码错误')

        session_id, ip = await SessionService.create_session(user['username'], 'gradio-ui', ports_value, db=db)
        token = await AccessTokenService.create_access_token(
            subject=user['username'],
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )

    message = {
        'message': '登录成功',
        'username': username,
        'session_id': session_id,
        'ip': ip,
        'ports': ports_value,
        'token': token,
    }
    return token, session_id, _pretty(message)


async def logout(entry_key: str, token: str, session_id: str):
    _require_entry_key(entry_key)
    if not token or not session_id:
        raise ValueError('请先登录，或填写要退出的 session_id')

    async with AsyncSessionLocal() as db:
        await _get_current_user_by_token(token, db)
        await SessionService.terminate_session(session_id, actor='user', db=db)
    return _pretty({'ok': True, 'session_id': session_id})


async def list_sessions(entry_key: str, token: str):
    _require_entry_key(entry_key)
    if not token:
        raise ValueError('请先登录')

    async with AsyncSessionLocal() as db:
        await _get_current_user_by_token(token, db)
        sessions = await SessionService.list_sessions()
    return _pretty(sessions)


async def force_offline(entry_key: str, token: str, session_id: str):
    _require_entry_key(entry_key)
    if not token or not session_id:
        raise ValueError('请提供 token 和 session_id')

    async with AsyncSessionLocal() as db:
        user = await _get_current_user_by_token(token, db)
        await SessionService.terminate_session(session_id, actor=user['username'], db=db)
    return _pretty({'ok': True, 'session_id': session_id})


async def list_users(entry_key: str, token: str):
    _require_entry_key(entry_key)
    if not token:
        raise ValueError('请先登录')

    async with AsyncSessionLocal() as db:
        user = await _get_current_user_by_token(token, db)
        if not user['is_admin']:
            raise ValueError('需要管理员权限')
        users = await UserService.list_users(db)
    return _pretty(users)


async def create_user(entry_key: str, token: str, username: str, password: str, is_admin: bool):
    _require_entry_key(entry_key)
    if not token:
        raise ValueError('请先登录')

    async with AsyncSessionLocal() as db:
        user = await _get_current_user_by_token(token, db)
        if not user['is_admin']:
            raise ValueError('需要管理员权限')
        await UserService.upsert_user(db, username, password, is_admin)
    return _pretty({'ok': True, 'username': username, 'is_admin': is_admin})


async def update_user(entry_key: str, token: str, username: str, password: str, is_active: str, is_admin: str):
    _require_entry_key(entry_key)
    if not token:
        raise ValueError('请先登录')

    def _to_optional_bool(value: str):
        val = (value or '').strip().lower()
        if not val:
            return None
        if val in {'true', '1', 'yes'}:
            return True
        if val in {'false', '0', 'no'}:
            return False
        raise ValueError(f'布尔值格式错误: {value}')

    async with AsyncSessionLocal() as db:
        user = await _get_current_user_by_token(token, db)
        if not user['is_admin']:
            raise ValueError('需要管理员权限')

        ok = await UserService.update_user(
            db=db,
            username=username,
            password=password or None,
            is_active=_to_optional_bool(is_active),
            is_admin=_to_optional_bool(is_admin),
        )
        if not ok:
            raise ValueError('用户不存在')

    return _pretty({'ok': True, 'username': username})


async def delete_user(entry_key: str, token: str, username: str):
    _require_entry_key(entry_key)
    if not token:
        raise ValueError('请先登录')

    async with AsyncSessionLocal() as db:
        user = await _get_current_user_by_token(token, db)
        if not user['is_admin']:
            raise ValueError('需要管理员权限')
        ok = await UserService.delete_user(db, username)
        if not ok:
            raise ValueError('用户不存在')

    return _pretty({'ok': True, 'username': username})


async def list_session_logs(entry_key: str, token: str, username: str, limit: int):
    _require_entry_key(entry_key)
    if not token:
        raise ValueError('请先登录')

    async with AsyncSessionLocal() as db:
        user = await _get_current_user_by_token(token, db)
        if not user['is_admin']:
            raise ValueError('需要管理员权限')
        logs = await UserSessionLogService.list_logs(db, username=username or None, limit=limit)
    return _pretty(logs)


def build_gradio_app() -> gr.Blocks:
    with gr.Blocks(title='AuthWall 安全控制台') as demo:
        gr.Markdown('## AuthWall 控制台（Gradio）')
        gr.Markdown('> 说明：可通过 `SECURE_ENTRY_PATH` 配置入口路径，通过 `SECURE_ENTRY_KEY` 配置入口密钥。')

        with gr.Row():
            entry_key = gr.Textbox(label='安全入口密钥（可选）', type='password', scale=2)
            token = gr.Textbox(label='Access Token', lines=2, scale=5)
            current_session_id = gr.Textbox(label='当前 Session ID', scale=3)

        common_output = gr.Code(label='执行结果', language='json', lines=18)

        with gr.Tab('认证接口 /auth'):
            login_username = gr.Textbox(label='用户名', value='admin')
            login_password = gr.Textbox(label='密码', type='password', value='admin123!')
            login_ports = gr.Textbox(label='端口列表（逗号分隔）', value='22')
            with gr.Row():
                login_btn = gr.Button('登录并放行')
                logout_btn = gr.Button('退出登录')

            login_btn.click(
                fn=login,
                inputs=[entry_key, login_username, login_password, login_ports],
                outputs=[token, current_session_id, common_output],
            )
            logout_btn.click(
                fn=logout,
                inputs=[entry_key, token, current_session_id],
                outputs=[common_output],
            )

        with gr.Tab('会话接口 /sessions'):
            session_id_input = gr.Textbox(label='Session ID（用于强制下线）')
            with gr.Row():
                list_sessions_btn = gr.Button('查询当前会话')
                force_offline_btn = gr.Button('强制下线')

            list_sessions_btn.click(
                fn=list_sessions,
                inputs=[entry_key, token],
                outputs=[common_output],
            )
            force_offline_btn.click(
                fn=force_offline,
                inputs=[entry_key, token, session_id_input],
                outputs=[common_output],
            )

        with gr.Tab('用户接口 /users'):
            with gr.Group():
                gr.Markdown('### 查询用户')
                list_users_btn = gr.Button('查询用户列表')
            with gr.Group():
                gr.Markdown('### 创建用户')
                create_username = gr.Textbox(label='用户名')
                create_password = gr.Textbox(label='密码', type='password')
                create_admin = gr.Checkbox(label='管理员', value=False)
                create_btn = gr.Button('创建用户')
            with gr.Group():
                gr.Markdown('### 更新用户')
                update_username = gr.Textbox(label='用户名')
                update_password = gr.Textbox(label='新密码（留空不修改）', type='password')
                update_is_active = gr.Textbox(label='is_active（true/false，留空不修改）')
                update_is_admin = gr.Textbox(label='is_admin（true/false，留空不修改）')
                update_btn = gr.Button('更新用户')
            with gr.Group():
                gr.Markdown('### 删除用户')
                delete_username_input = gr.Textbox(label='用户名')
                delete_btn = gr.Button('删除用户')

            list_users_btn.click(fn=list_users, inputs=[entry_key, token], outputs=[common_output])
            create_btn.click(
                fn=create_user,
                inputs=[entry_key, token, create_username, create_password, create_admin],
                outputs=[common_output],
            )
            update_btn.click(
                fn=update_user,
                inputs=[entry_key, token, update_username, update_password, update_is_active, update_is_admin],
                outputs=[common_output],
            )
            delete_btn.click(fn=delete_user, inputs=[entry_key, token, delete_username_input], outputs=[common_output])

        with gr.Tab('会话日志 /users/session-logs'):
            logs_username = gr.Textbox(label='按用户名过滤（可选）')
            logs_limit = gr.Slider(label='返回条数', minimum=1, maximum=500, step=1, value=100)
            logs_btn = gr.Button('查询日志')
            logs_btn.click(
                fn=list_session_logs,
                inputs=[entry_key, token, logs_username, logs_limit],
                outputs=[common_output],
            )

    return demo
