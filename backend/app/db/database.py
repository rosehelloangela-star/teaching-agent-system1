from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 数据库文件的存放路径，会在 backend 根目录下生成一个 teaching_agent.db 文件
SQLALCHEMY_DATABASE_URL = "sqlite:///./teaching_agent.db"

# 创建数据库引擎 (check_same_thread=False 是 SQLite 在 FastAPI 中使用的特殊配置)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类，后面所有的数据库模型（表）都要继承这个基类
Base = declarative_base()

# 依赖注入函数：每次有 API 请求时，帮我们打开数据库连接，请求结束自动关闭
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()