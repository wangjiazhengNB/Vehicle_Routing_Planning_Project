"""数据库配置模块"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .settings import get_config


# 获取配置
config = get_config()

# 创建数据库引擎
engine = create_engine(
    config.database_url,
    pool_size=config.get("database.pool_size", 10),
    max_overflow=config.get("database.max_overflow", 20),
    pool_pre_ping=True,
    echo=config.debug  # 调试模式下输出SQL
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建ORM基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话（用于FastAPI等异步场景）
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session():
    """
    获取数据库会话（用于Flask等同步场景）

    Returns:
        Session: SQLAlchemy会话
    """
    return SessionLocal()


def init_db():
    """
    初始化数据库（创建所有表）

    注意: v3.0 不再使用 road_network 表，改用高德API实时获取路网数据
    """
    from ..models import route_result, address_cache

    Base.metadata.create_all(bind=engine)
