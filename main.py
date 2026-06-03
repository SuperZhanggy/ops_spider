import os
import time
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.routes import screenshot, authentication
from config.logging import InterceptHandler, configure_loguru

# 确保 logs 目录存在
os.makedirs("logs", exist_ok=True)
configure_loguru()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # uvicorn 启动后重新配置日志拦截器，防止被覆盖
    from loguru import logger

    root = logging.getLogger()
    if not root.handlers or not isinstance(root.handlers[0], InterceptHandler):
        root.handlers = [InterceptHandler()]
        for logger_name in ("uvicorn.asgi", "uvicorn.access"):
            lg = logging.getLogger(logger_name)
            lg.handlers = [InterceptHandler()]
            lg.propagate = False

    logger.info("服务启动成功，监听 0.0.0.0:8031")
    yield


app = FastAPI(title="Playwright Service", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    from loguru import logger
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    logger.info(f"{request.method} {request.url.path} {response.status_code} {elapsed*1000:.0f}ms")
    return response

app.include_router(authentication.router, prefix="/api/auth")
app.include_router(screenshot.router, prefix="/api/screenshot")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8031, reload=True)