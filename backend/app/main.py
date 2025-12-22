"""
Nebula KTV FastAPI 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import init_db, close_db
from app.api.songs import router as songs_router
from app.api.stream import router as stream_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库连接池
    await init_db()
    yield
    # 关闭时清理数据库连接
    await close_db()


# 创建 FastAPI 应用实例
app = FastAPI(
    title="Nebula KTV API",
    description="AI 驱动的私有化车载 KTV 系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(songs_router)
app.include_router(stream_router)


@app.get("/")
async def root():
    """健康检查端点"""
    return {"message": "Nebula KTV API is running"}


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)