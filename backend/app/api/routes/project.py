from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from sqlalchemy.orm import Session
from typing import List
import json
from collections import defaultdict

from app.db.database import get_db
from app.db.models import Project, User, Conversation
from app.schemas.project import ProjectResponse, ChatSyncRequest

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse)
async def create_project(
    name: str = Form(...),
    student_id: str = Form(...),
    content: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    file_name = file.filename if file else None
    new_project = Project(
        name=name,
        student_id=student_id,
        content=content,
        file_name=file_name,
        status="pending"
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/", response_model=List[ProjectResponse])
def get_projects(student_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Project)
    if student_id:
        query = query.filter(Project.student_id == student_id)
    return query.order_by(Project.created_at.desc()).all()

@router.put("/{project_id}/chat", response_model=ProjectResponse)
def sync_chat_history(project_id: str, request: ChatSyncRequest, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目未找到")
    project.chat_history = request.chat_history
    db.commit()
    db.refresh(project)
    return project

@router.get("/class-insights")
def get_class_insights(class_name: str, db: Session = Depends(get_db)):
    """【班级真实学情洞察】聚合超图规则、竞赛得分、高风险项目"""
    students = db.query(User).filter(User.role == "student", User.class_name == class_name).all()
    student_ids = [s.id for s in students]
    
    if not student_ids:
        # 确保哪怕没有数据，也返回匹配前端结构的安全空字典
        return {"total_projects": 0, "hypergraph_alerts": [], "competitions": {}, "high_risk_projects": []}
    
    conversations = db.query(Conversation).filter(
        Conversation.student_id.in_(student_ids),
        Conversation.document_status == "bound"
    ).all()

    total_projects = len(conversations)
    alert_counter = defaultdict(int)
    competition_data = defaultdict(list)
    high_risk_projects = []

    for conv in conversations:
        try:
            snap = json.loads(conv.analysis_snapshot)
            student_name = db.query(User).filter(User.id == conv.student_id).first().real_name
            project_title = conv.bound_file_name or conv.title
            
            # 1. 解析超图预警数据
            proj_alerts = snap.get("project", {}).get("hypergraph_data", {}).get("alerts", [])
            alert_count = len(proj_alerts)
            for a in proj_alerts:
                rule_name = f"[{a.get('rule', '-')}] {a.get('name', '未知')}"
                alert_counter[rule_name] += 1
                
            # 2. 解析竞赛得分数据
            comp_snap = snap.get("competition", {})
            if comp_snap:
                meta = comp_snap.get("competition_meta", {})
                summary = comp_snap.get("score_summary", {})
                comp_name = meta.get("short_name", "未知赛事")
                score = summary.get("weighted_score_pct", 0)
                
                competition_data[comp_name].append({
                    "project_name": project_title,
                    "student_name": student_name,
                    "score": score
                })
            
            # 3. 抓取高危项目 (触发 2 条及以上断层判定为高风险)
            if alert_count >= 2:
                issues = [a.get("name") for a in proj_alerts[:2]]
                high_risk_projects.append({
                    "project_name": project_title,
                    "student_name": student_name,
                    "alert_count": alert_count,
                    "issues": "、".join(issues) + ("等" if alert_count > 2 else "")
                })

        except Exception:
            pass

    # 排序与格式化
    sorted_alerts = [
        {"rule": k, "count": v, "percentage": round((v/total_projects)*100, 1) if total_projects else 0} 
        for k, v in sorted(alert_counter.items(), key=lambda x: x[1], reverse=True)
    ]
    
    # 竞赛项目按分数倒序
    for comp in competition_data:
        competition_data[comp] = sorted(competition_data[comp], key=lambda x: x["score"], reverse=True)

    return {
        "total_projects": total_projects,
        "hypergraph_alerts": sorted_alerts,
        "competitions": competition_data,
        "high_risk_projects": sorted(high_risk_projects, key=lambda x: x["alert_count"], reverse=True)
    }

# from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
# from sqlalchemy.orm import Session
# from typing import List
# import json
# from collections import defaultdict
# from app.db.models import User, Conversation
# from app.db.database import get_db
# from app.db.models import Project
# from app.schemas.project import ProjectResponse
# from app.schemas.project import ChatSyncRequest # 顶部记得引入刚才写的 schema

# router = APIRouter(prefix="/projects", tags=["projects"])

# @router.post("/", response_model=ProjectResponse)
# async def create_project(
#     name: str = Form(...),
#     student_id: str = Form(...),
#     content: str = Form(None),
#     file: UploadFile = File(None),
#     db: Session = Depends(get_db)
# ):
#     """
#     新建项目：接收前端表单数据和文件，存入数据库
#     """
#     file_name = file.filename if file else None
    
#     # 构建数据库映射对象
#     new_project = Project(
#         name=name,
#         student_id=student_id,
#         content=content,
#         file_name=file_name,
#         status="pending"
#     )
    
#     # 存入数据库并保存
#     db.add(new_project)
#     db.commit()
#     db.refresh(new_project) # 获取数据库自动生成的 id 和时间戳
    
#     return new_project


# @router.get("/", response_model=List[ProjectResponse])
# def get_projects(
#     student_id: str = None, 
#     db: Session = Depends(get_db)
# ):
#     """
#     拉取项目列表：如果传了 student_id，就只返回该学生的数据，否则返回所有数据（供教师端使用）
#     """
#     query = db.query(Project)
    
#     if student_id:
#         query = query.filter(Project.student_id == student_id)
        
#     # 按时间倒序排列（最新的在最上面）
#     projects = query.order_by(Project.created_at.desc()).all()
    
#     return projects
