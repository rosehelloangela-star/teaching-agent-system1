from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.agent import router as agent_router
from app.api.routes.auth import router as auth_router
from app.api.routes.conversation import router as conversation_router
from app.api.routes.project import router as project_router
from app.api.routes.admin import router as admin_router
from app.core.config import get_settings
from app.db import models  # noqa: F401
# 补充引入 SessionLocal 和 User 模型
from app.db.database import Base, engine, SessionLocal 
from app.db.models import User 

settings = get_settings()

# ================= 新增：定义启动事件，自动创建默认账号 =================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 启动时执行：连接数据库
    db = SessionLocal()
    try:
        # 定义你需要的默认账号
        default_users = [
            {"username": "admin", "password": "123456", "real_name": "系统管理员", "role": "admin"},
            {"username": "teacher", "password": "123", "real_name": "初始教师", "role": "teacher"},
            {"username": "stu001", "password": "123", "real_name": "初始学生", "class_name": "1班", "role": "student"}
        ]
        
        # 遍历检查，如果没有对应的 username 就存入数据库
        for user_data in default_users:
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing_user:
                db.add(User(**user_data))
                
        db.commit()
        print("✅ 默认账号 (admin, teacher, stu001) 检查/初始化完成！")
    except Exception as e:
        print(f"❌ 初始化默认账号失败: {e}")
        db.rollback()
    finally:
        db.close()
        
    # 2. 挂起，让应用正常运行
    yield 
# ======================================================================

# 将 lifespan 绑定到你的 FastAPI 实例上
app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    lifespan=lifespan
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://121.14.82.109:8060",
        "http://localhost:8060",
        "http://127.0.0.1:8060",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {
        "message": "Teaching Agent System backend is running",
        "env": settings.app_env,
    }


app.include_router(agent_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(conversation_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.api.routes.agent import router as agent_router
# from app.api.routes.auth import router as auth_router
# from app.api.routes.conversation import router as conversation_router
# from app.api.routes.project import router as project_router
# from app.api.routes.admin import router as admin_router
# from app.core.config import get_settings
# from app.db import models  # noqa: F401
# from app.db.database import Base, engine

# settings = get_settings()

# app = FastAPI(
#     title=settings.app_name,
#     debug=settings.app_debug,
# )

# Base.metadata.create_all(bind=engine)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.get("/")
# def root() -> dict:
#     return {
#         "message": "Teaching Agent System backend is running",
#         "env": settings.app_env,
#     }


# app.include_router(agent_router, prefix="/api/v1")
# app.include_router(project_router, prefix="/api/v1")
# app.include_router(auth_router, prefix="/api/v1")
# app.include_router(conversation_router, prefix="/api/v1")
# app.include_router(admin_router, prefix="/api/v1")