from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.database import get_db
from app.db.models import User, Project, Conversation

router = APIRouter(prefix="/admin", tags=["admin"])

# --- 请求体 Schemas ---
class UserCreate(BaseModel):
    username: str
    real_name: str
    class_name: Optional[str] = None
    role: str = "student"
    password: str

class BatchUserCreate(BaseModel):
    users: List[UserCreate]

class PasswordReset(BaseModel):
    new_password: str

class RoleUpdate(BaseModel):
    role: str

# --- 接口定义 ---
@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    """获取全校所有用户数据"""
    users = db.query(User).all()
    # 过滤掉密码，避免泄露
    return [{"id": u.id, "username": u.username, "real_name": u.real_name, "class_name": u.class_name, "role": u.role, "created_at": u.created_at} for u in users]

@router.post("/users/batch")
def batch_create_users(request: BatchUserCreate, db: Session = Depends(get_db)):
    """批量注册账号"""
    created_count = 0
    for u in request.users:
        if not db.query(User).filter(User.username == u.username).first():
            new_user = User(
                username=u.username, 
                password=u.password, 
                real_name=u.real_name, 
                class_name=u.class_name, 
                role=u.role
            )
            db.add(new_user)
            created_count += 1
    db.commit()
    return {"message": f"成功批量注册 {created_count} 个账号"}

@router.delete("/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """删除指定账号"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return {"message": "账号删除成功"}
    raise HTTPException(status_code=404, detail="用户不存在")

@router.put("/users/{user_id}/password")
def reset_password(user_id: str, request: PasswordReset, db: Session = Depends(get_db)):
    """重置/设置初始密码"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.password = request.new_password
        db.commit()
        return {"message": "密码重置成功"}
    raise HTTPException(status_code=404, detail="用户不存在")

@router.put("/users/{user_id}/role")
def update_role(user_id: str, request: RoleUpdate, db: Session = Depends(get_db)):
    """更改账号角色权限"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.role = request.role
        db.commit()
        return {"message": f"角色已更新为 {request.role}"}
    raise HTTPException(status_code=404, detail="用户不存在")

@router.get("/stats")
def get_global_stats(db: Session = Depends(get_db)):
    """全局数据监控与宏观统计"""
    user_count = db.query(User).count()
    project_count = db.query(Project).count()
    conversation_count = db.query(Conversation).count()
    
    # 此处模拟聚合各学院的高频触发 Top 3 漏洞看板（由于真实聚合需要遍历所有JSON快照，此处暂用统计数据模型返回）
    # 如果要深入，可以从 conversation.analysis_snapshot 中通过 json 提取逻辑缺陷
    return {
        "total_users": user_count,
        "total_projects": project_count,
        "total_conversations": conversation_count,
        "overall_health_score": 78,
        "top_flaws": [
            {"name": "TAM替代SOM，市场规模虚高", "frequency": "45%", "severity": "High"},
            {"name": "单位经济模型倒挂(LTV < CAC)", "frequency": "32%", "severity": "Critical"},
            {"name": "渠道与客群物理脱节", "frequency": "28%", "severity": "High"}
        ]
    }