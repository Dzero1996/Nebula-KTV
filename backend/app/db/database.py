"""
数据库连接和会话管理
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator


class Base(DeclarativeBase):
    """SQLAlchemy 基础模型类"""
    pass


# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:password@localhost:5432/nebula_ktv"
)

# 创建异步数据库引擎 (仅在非测试环境下)
engine = None
if not os.getenv("TESTING"):
    try:
        engine = create_async_engine(
            DATABASE_URL,
            echo=True,  # 开发环境下打印 SQL 语句
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
    except ImportError:
        # asyncpg 未安装时跳过
        pass

# 创建异步会话工厂
AsyncSessionLocal = None
if engine:
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def init_db():
    """初始化数据库连接池"""
    # 这里可以添加数据库初始化逻辑
    pass


async def close_db():
    """关闭数据库连接"""
    if engine:
        await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖注入函数"""
    if not AsyncSessionLocal:
        raise RuntimeError("Database not initialized")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()