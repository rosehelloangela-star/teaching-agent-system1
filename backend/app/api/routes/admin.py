import json
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.database import get_db
from app.db.models import User, Project, Conversation

router = APIRouter(prefix="/admin", tags=["admin"])

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

class ClassAssign(BaseModel):
    classes: str

@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "real_name": u.real_name, "class_name": u.class_name, "role": u.role, "created_at": u.created_at} for u in users]

@router.post("/users/batch")
def batch_create_users(request: BatchUserCreate, db: Session = Depends(get_db)):
    created_count = 0
    for u in request.users:
        if not db.query(User).filter(User.username == u.username).first():
            new_user = User(
                username=u.username, password=u.password, 
                real_name=u.real_name, class_name=u.class_name, role=u.role
            )
            db.add(new_user)
            created_count += 1
    db.commit()
    return {"message": f"成功批量注册 {created_count} 个账号"}

@router.delete("/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return {"message": "账号删除成功"}
    raise HTTPException(status_code=404, detail="用户不存在")

@router.put("/users/{user_id}/password")
def reset_password(user_id: str, request: PasswordReset, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.password = request.new_password
        db.commit()
        return {"message": "密码重置成功"}
    raise HTTPException(status_code=404, detail="用户不存在")

@router.put("/users/{user_id}/role")
def update_role(user_id: str, request: RoleUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.role = request.role
        db.commit()
        return {"message": f"角色已更新为 {request.role}"}
    raise HTTPException(status_code=404, detail="用户不存在")

@router.put("/users/{user_id}/classes")
def assign_classes_to_user(user_id: str, request: ClassAssign, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        # 去掉了 "只能给导师分配班级" 的拦截逻辑
        user.class_name = request.classes
        db.commit()
        
        role_label = "导师" if user.role == "teacher" else "学生" if user.role == "student" else "用户"
        return {"message": f"成功为{role_label}分配班级：{request.classes}"}
        
    raise HTTPException(status_code=404, detail="用户不存在")

@router.get("/classes/stats")
def get_class_statistics(db: Session = Depends(get_db)):
    students = db.query(User).filter(User.role == "student").all()
    class_stats = {}
    for stu in students:
        c_name = stu.class_name or "未分班"
        if c_name not in class_stats:
            class_stats[c_name] = {"student_count": 0, "project_count": 0}
        
        class_stats[c_name]["student_count"] += 1
        bound_conversations = db.query(Conversation).filter(
            Conversation.student_id == stu.id,
            Conversation.document_status == 'bound'
        ).count()
        class_stats[c_name]["project_count"] += bound_conversations

    result = [{"class_name": k, "student_count": v["student_count"], "project_count": v["project_count"]} 
              for k, v in class_stats.items()]
    result.sort(key=lambda x: x["class_name"])
    return result

@router.get("/stats")
def get_global_stats(db: Session = Depends(get_db)):
    """【全校真实数据打通】遍历所有快照解析超图数据"""
    user_count = db.query(User).count()
    
    # 真实项目数 = 绑定了文档的会话数量
    conversations = db.query(Conversation).filter(Conversation.document_status == 'bound').all()
    real_project_count = len(conversations)
    total_conversations = db.query(Conversation).count()
    
    # 增加 rule 字段记录
    flaw_counter = defaultdict(lambda: {"count": 0, "severity": "High", "rule": ""})
    total_alerts = 0

    for conv in conversations:
        try:
            snap = json.loads(conv.analysis_snapshot)
            # 提取 project 模式下的 hypergraph 报错记录
            alerts = snap.get("project", {}).get("hypergraph_data", {}).get("alerts", [])
            for alert in alerts:
                name = alert.get("name", "未知逻辑断层")
                rule_id = alert.get("rule", "未知规则") # 提取 R1, R2...
                severity = alert.get("severity", "high").capitalize()
                
                flaw_counter[name]["count"] += 1
                flaw_counter[name]["severity"] = severity
                flaw_counter[name]["rule"] = rule_id
                total_alerts += 1
        except Exception:
            pass
    
    # 按触发频次从高到低排序
    sorted_flaws = sorted(flaw_counter.items(), key=lambda x: x[1]["count"], reverse=True)
    all_flaws = []
    
    # 移除原本的 [:3] 切片，返回所有规则
    for name, data in sorted_flaws:
        freq = round((data["count"] / real_project_count) * 100, 1) if real_project_count > 0 else 0
        all_flaws.append({
            "rule": data["rule"],     # 返回规则 ID
            "name": name,
            "frequency": f"{freq}%",
            "severity": data["severity"]
        })
    
    if not all_flaws:
        all_flaws = [{"rule": "-", "name": "暂无足够数据触发超图规则", "frequency": "0%", "severity": "Info"}]

    # 基于平均漏洞数量扣减模型健康度（每个项目平均多一个漏洞，健康度扣10分）
    avg_alerts = total_alerts / real_project_count if real_project_count > 0 else 0
    health_score = max(0, min(100, int(100 - avg_alerts * 10)))
    if real_project_count == 0:
        health_score = 100

    return {
        "total_users": user_count,
        "total_projects": real_project_count,
        "total_conversations": total_conversations,
        "overall_health_score": health_score,
        "top_flaws": all_flaws # 这里返回的是从高到低排好序的全部数据
    }