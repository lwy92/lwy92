import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gradio import mount_gradio_app

from app.api import auth, sessions, users
from app.core.config import settings
from app.db import AsyncSessionLocal, engine
from app.firewall.manager import FirewallManager
from app.models.db_models import Base
from app.services.user_service import UserService
from app.ui.gradio_app import build_gradio_app
from app.workers.cleanup import cleanup_worker

cleanup_stop_event = asyncio.Event()
worker_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global worker_task

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    fw = FirewallManager()
    await fw.bootstrap()
    await fw.startup_cleanup()

    async with AsyncSessionLocal() as db:
        await UserService.init_admin(db)

    worker_task = asyncio.create_task(cleanup_worker(cleanup_stop_event))
    yield

    cleanup_stop_event.set()
    if worker_task:
        await worker_task


app = FastAPI(title=settings.app_name, version='0.1.0', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

api_prefix = f"{settings.secure_entry_path.rstrip('/')}/api/v1"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(sessions.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)

app = mount_gradio_app(app, build_gradio_app(), path=settings.secure_entry_path)


@app.get('/healthz')
async def healthz() -> dict:
    return {'status': 'ok'}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
