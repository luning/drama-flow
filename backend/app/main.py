from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(dramas.router, prefix="/api", tags=["Dramas"])
app.include_router(episodes.router, prefix="/api", tags=["Episodes"])
app.include_router(watch_records.router, prefix="/api", tags=["Watch Records"])


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
