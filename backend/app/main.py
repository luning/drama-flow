from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.api import auth, dramas, episodes, watch_records
from app.db.database import engine, Base

app = FastAPI(
    title="DramaFlow API",
    description="海外短剧 APP 后端服务",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unified_error_handler(request: Request, exc: Exception):
    """
    统一错误格式：所有未捕获异常返回 { detail, code, path } 结构。
    前端可根据 code 做统一错误处理，无需逐个接口定制。
    """
    status_code = 500
    detail = "服务器内部错误"

    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        detail = exc.detail

    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "code": status_code,
            "path": request.url.path,
        },
    )


# 挂载本地媒体文件（LOCAL_MEDIA=true 时供开发环境使用）
mp4_dir = Path(__file__).parent.parent.parent / "mp4"
if mp4_dir.exists():
    app.mount("/media", StaticFiles(directory=str(mp4_dir)), name="media")

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(dramas.router, prefix="/api", tags=["Dramas"])
app.include_router(episodes.router, prefix="/api", tags=["Episodes"])
app.include_router(watch_records.router, prefix="/api", tags=["Watch Records"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


# 挂载 H5 静态文件，供 Android WebView / 浏览器直接访问
h5_dist = Path(__file__).parent.parent.parent / "h5" / "dist"
if h5_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(h5_dist / "assets")), name="h5_assets")

    @app.get("/")
    async def serve_h5():
        return HTMLResponse(content=(h5_dist / "index.html").read_text(encoding="utf-8"))

    @app.get("/{path:path}")
    async def serve_h5_spa(path: str):
        if path.startswith("api/"):
            raise HTTPException(status_code=404)
        return HTMLResponse(content=(h5_dist / "index.html").read_text(encoding="utf-8"))
