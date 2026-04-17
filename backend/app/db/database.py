from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 1. 确保目录存在（防止启动时报错）
db_dir = "./app/data"
if not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

# 2. 修改路径：将数据库放在这个目录下
# 注意：这里的 ./app/data/ 对应容器内部的路径
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_dir}/teaching_agent.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()