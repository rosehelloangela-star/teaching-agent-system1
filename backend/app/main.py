# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.api.routes.agent import router as agent_router
# from app.core.config import get_settings
# from app.api.routes.project import router as project_router
# from app.api.routes.auth import router as auth_router

# settings = get_settings()

# app = FastAPI(
#     title=settings.app_name,
#     debug=settings.app_debug,
# )

# from app.db.database import engine, Base
# from app.db import models
# Base.metadata.create_all(bind=engine)

# settings = get_settings()
# app = FastAPI(
#     title=settings.app_name,
#     debug=settings.app_debug,
# )

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


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.agent import router as agent_router
from app.api.routes.auth import router as auth_router
from app.api.routes.conversation import router as conversation_router
from app.api.routes.project import router as project_router
from app.core.config import get_settings
from app.db import models  # noqa: F401
from app.db.database import Base, engine

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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