from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models import Project
from app.schemas.project import ProjectResponse
from app.schemas.project import ChatSyncRequest # 顶部记得引入刚才写的 schema

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse)
async def create_project(
    name: str = Form(...),
    student_id: str = Form(...),
    content: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """
    新建项目：接收前端表单数据和文件，存入数据库
    """
    file_name = file.filename if file else None
    
    # 构建数据库映射对象
    new_project = Project(
        name=name,
        student_id=student_id,
        content=content,
        file_name=file_name,
        status="pending"
    )
    
    # 存入数据库并保存
    db.add(new_project)
    db.commit()
    db.refresh(new_project) # 获取数据库自动生成的 id 和时间戳
    
    return new_project


@router.get("/", response_model=List[ProjectResponse])
def get_projects(
    student_id: str = None, 
    db: Session = Depends(get_db)
):
    """
    拉取项目列表：如果传了 student_id，就只返回该学生的数据，否则返回所有数据（供教师端使用）
    """
    query = db.query(Project)
    
    if student_id:
        query = query.filter(Project.student_id == student_id)
        
    # 按时间倒序排列（最新的在最上面）
    projects = query.order_by(Project.created_at.desc()).all()
    
    return projects

@router.put("/{project_id}/chat", response_model=ProjectResponse)
def sync_chat_history(
    project_id: str,
    request: ChatSyncRequest,
    db: Session = Depends(get_db)
):
    """
    同步更新指定项目的聊天记录
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目未找到")
    
    project.chat_history = request.chat_history
    db.commit()
    db.refresh(project)
    
    return project