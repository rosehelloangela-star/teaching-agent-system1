import json
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, load_only

from app.core.file_utils import ATTACHMENT_ROOT, extract_file_payload, save_teacher_attachment
from app.db.database import get_db
from app.db.models import Conversation, User, ClassReport
from app.db.models import KnowledgeCard
from app.core.file_utils import extract_file_payload
# 引入我们刚才在 generator.py 写的逻辑函数
from app.agents.mechanism.generator import extract_knowledge_card_from_text
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationListItemResponse,
    ConversationResponse,
    ConversationStateSyncRequest,
    EvalUpdateRequest,      # <--- 新增引入
    ClassReportRequest      # <--- 新增引入
)

router = APIRouter(prefix="/conversations", tags=["conversations"])

def _normalize_title(title: str | None) -> str:
    title = (title or "").strip()
    return title if title else "新对话"

def _safe_json_loads(raw, fallback):
    if raw is None:
        return fallback
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return fallback

def _parse_classes(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in str(raw).split(",") if item.strip()]

def _get_teacher_accessible_students(db: Session, teacher_id: str) -> list[User]:
    teacher = db.query(User).filter(User.id == teacher_id).first()
    if not teacher:
        # 【核心修复】以前这里是 raise HTTPException(404)，查不到老师直接导致整个前端崩溃报404。
        # 现在改为打印日志并返回空数组，彻底解决 404 挂掉的问题！
        print(f"[DEBUG] 警告: 教师ID {teacher_id} 在数据库中未找到。")
        return []

    if teacher.role == "admin":
        return db.query(User).filter(User.role == "student").all()

    teacher_classes = _parse_classes(teacher.class_name)
    if not teacher_classes:
        return []

    return (
        db.query(User)
        .filter(User.role == "student", User.class_name.in_(teacher_classes))
        .all()
    )

def _build_teacher_summary(conversation: Conversation, student: User) -> dict:
    chat_history = _safe_json_loads(conversation.chat_history, [])
    return {
        "id": conversation.id,
        "student_id": conversation.student_id,
        "student_name": student.real_name,
        "class_name": student.class_name,
        "title": conversation.title,
        "chat_history": conversation.chat_history,
        "bound_file_name": conversation.bound_file_name,
        "bound_file_uploaded_at": conversation.bound_file_uploaded_at,
        "bound_document_text": conversation.bound_document_text, 
        "bound_file_uploaded_at": conversation.bound_file_uploaded_at,
        "document_status": conversation.document_status,
        "analysis_snapshot": conversation.analysis_snapshot,
        "last_mode": conversation.last_mode,
        "evaluation_report": conversation.evaluation_report, # <--- 新增这行，返回画像报告
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "teacher_message_count": len(
            [msg for msg in chat_history if isinstance(msg, dict) and msg.get("role") == "teacher"]
        ),
    }

@router.post("/attachments/upload")
async def upload_teacher_attachment(file: UploadFile = File(...)):
    return await save_teacher_attachment(file)

@router.get("/attachments/{file_id}")
def download_teacher_attachment(file_id: str):
    safe_name = Path(file_id).name
    file_path = ATTACHMENT_ROOT / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="附件不存在")
    download_name = safe_name.split("_", 1)[1] if "_" in safe_name else safe_name
    return FileResponse(path=file_path, filename=download_name, media_type='application/octet-stream')

@router.post("/", response_model=ConversationResponse)
def create_conversation(
    request: ConversationCreateRequest,
    db: Session = Depends(get_db),
):
    new_conversation = Conversation(
        student_id=request.student_id,
        title=_normalize_title(request.title),
        chat_history="[]",
        analysis_snapshot="{}",
        document_status="none",
        last_mode="learning",
    )
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation

@router.get("/", response_model=List[ConversationListItemResponse])
def get_conversations(
    student_id: str,
    db: Session = Depends(get_db),
):
    conversations = (
        db.query(Conversation)
        .options(
            load_only(
                Conversation.id,
                Conversation.student_id,
                Conversation.title,
                Conversation.bound_file_name,
                Conversation.bound_file_uploaded_at,
                Conversation.document_status,
                Conversation.last_mode,
                Conversation.created_at,
                Conversation.updated_at,
            )
        )
        .filter(Conversation.student_id == student_id)
        .order_by(Conversation.updated_at.desc(), Conversation.created_at.desc())
        .all()
    )
    return conversations

# ==========================================
# 教师端拉取全班项目的接口 (前端报错 404 的接口)
# ==========================================
@router.get("/teacher/projects")
def get_teacher_project_conversations(
    teacher_id: str = Query(...),
    query: str = Query(default=""),
    db: Session = Depends(get_db),
):
    students = _get_teacher_accessible_students(db, teacher_id)
    if not students:
        return []

    student_map = {student.id: student for student in students}
    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.student_id.in_(list(student_map.keys())),
            Conversation.document_status == "bound",
        )
        .all()
    )

    keyword = (query or "").strip().lower()
    rows = []
    for conversation in conversations:
        student = student_map.get(conversation.student_id)
        if not student:
            continue
        summary = _build_teacher_summary(conversation, student)
        haystack = " ".join(
            filter(
                None,
                [
                    summary.get("title") or "",
                    summary.get("student_name") or "",
                    summary.get("bound_file_name") or "",
                    summary.get("class_name") or "",
                ],
            )
        ).lower()
        if keyword and keyword not in haystack:
            continue
        rows.append(summary)

    rows.sort(
        key=lambda item: (
            item.get("bound_file_uploaded_at") or datetime.min,
            item.get("updated_at") or datetime.min,
            item.get("created_at") or datetime.min,
        ),
        reverse=True,
    )
    return rows


@router.get("/teacher/projects/{conversation_id}")
def get_teacher_project_conversation_detail(
    conversation_id: str,
    teacher_id: str = Query(...),
    db: Session = Depends(get_db),
):
    students = _get_teacher_accessible_students(db, teacher_id)
    student_map = {student.id: student for student in students}

    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    student = student_map.get(conversation.student_id)
    if not student:
        raise HTTPException(status_code=403, detail="当前教师无权访问该项目会话")

    return _build_teacher_summary(conversation, student)


# ==========================================
# 卡片
# ==========================================
@router.post("/knowledge-cards/extract")
async def extract_card_from_file(file: UploadFile = File(...)):
    """
    网络路由层：接收文件，调用 LLM，返回结果
    """
    # 1. 提取文件文本
    payload = await extract_file_payload(file)
    if not payload.get("supported") or not payload.get("text"):
        raise HTTPException(status_code=400, detail="文件解析失败或内容为空")
    
    file_text = payload["text"][:5000] # 截取前 5000 字
    
    # 2. 调用业务逻辑层
    try:
        extracted_data = await extract_knowledge_card_from_text(file_text)
        return extracted_data
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="系统内部错误，提取失败")

@router.get("/knowledge-cards")
def list_cards(db: Session = Depends(get_db)):
    return db.query(KnowledgeCard).order_by(KnowledgeCard.created_at.desc()).all()

@router.post("/knowledge-cards")
def create_card(request: dict, db: Session = Depends(get_db)):
    # 这里的 request 是前端提取成功后发送的完整字段
    new_card = KnowledgeCard(**request)
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

@router.delete("/knowledge-cards/{card_id}")
def delete_card(card_id: str, db: Session = Depends(get_db)):
    card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    db.delete(card)
    db.commit()
    return {"status": "success"}

@router.put("/knowledge-cards/{card_id}")
def update_card(
    card_id: str, 
    request: dict = Body(...),  # 🌟 显式指定从 Body 获取数据
    db: Session = Depends(get_db)
):
    # 先查找是否存在
    card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    
    try:
        # 🌟 过滤掉不可更改的系统字段，只更新业务字段
        # 这样可以防止前端传来的 id 字段触发数据库的主键更新冲突
        for key, value in request.items():
            if hasattr(card, key) and key not in ("id", "created_at", "updated_at"):
                setattr(card, key, value)
                
        db.commit()
        db.refresh(card)
        return card
    except Exception as e:
        db.rollback() # 出错回滚，防止数据库 Session 挂起
        print(f"[ERROR] 更新卡片失败: {str(e)}") # 后端日志打印具体错误
        raise HTTPException(status_code=500, detail="数据库更新失败，请检查字段格式")

# 这个接口由于名字太宽泛，一定要放在 /teacher/projects 下面
@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation_detail(
    conversation_id: str,
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    return conversation


@router.put("/{conversation_id}/bind-file", response_model=ConversationResponse)
async def bind_conversation_file(
    conversation_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    payload = await extract_file_payload(file)
    if not payload["supported"]:
        raise HTTPException(status_code=400, detail=payload["error"])

    if not payload["text"].strip():
        raise HTTPException(status_code=400, detail="上传文件解析后为空，无法绑定到该会话")

    conversation.bound_file_name = payload["filename"]
    conversation.bound_document_text = payload["text"]
    conversation.bound_file_uploaded_at = datetime.utcnow()
    conversation.document_status = "bound"

    db.commit()
    db.refresh(conversation)
    return conversation




@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    student_id: str = Query(...),
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    if conversation.student_id != student_id:
        raise HTTPException(status_code=403, detail="无权删除该会话")

    db.delete(conversation)
    db.commit()
    return {"status": "success", "conversation_id": conversation_id}

@router.put("/{conversation_id}/state", response_model=ConversationResponse)
def sync_conversation_state(
    conversation_id: str,
    request: ConversationStateSyncRequest,
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    conversation.chat_history = request.chat_history

    if request.analysis_snapshot is not None:
        conversation.analysis_snapshot = request.analysis_snapshot

    if request.title is not None:
        conversation.title = _normalize_title(request.title)

    if request.last_mode is not None:
        conversation.last_mode = request.last_mode

    if request.kg_context is not None:
        conversation.kg_context = request.kg_context

    db.commit()
    db.refresh(conversation)
    return conversation

# ==========================================
# 报告持久化接口 (学生画像 & 班级学情)
# ==========================================

@router.put("/{conversation_id}/evaluation")
def update_conversation_evaluation(
    conversation_id: str, 
    request: EvalUpdateRequest, 
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    conversation.evaluation_report = request.evaluation_report
    db.commit()
    return {"status": "success"}

@router.get("/class-reports/{class_name}")
def get_class_report(class_name: str, db: Session = Depends(get_db)):
    report = db.query(ClassReport).filter(ClassReport.class_name == class_name).first()
    return {"report_content": report.report_content if report else None}

@router.put("/class-reports/{class_name}")
def save_class_report(
    class_name: str, 
    request: ClassReportRequest, 
    db: Session = Depends(get_db)
):
    report = db.query(ClassReport).filter(ClassReport.class_name == class_name).first()
    if not report:
        report = ClassReport(class_name=class_name, report_content=request.report_content)
        db.add(report)
    else:
        report.report_content = request.report_content
    db.commit()
    return {"status": "success"}



# import json
# from datetime import datetime
# from pathlib import Path
# from typing import List

# from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, Body
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session

# from app.core.file_utils import ATTACHMENT_ROOT, extract_file_payload, save_teacher_attachment
# from app.db.database import get_db
# from app.db.models import Conversation, User, ClassReport
# from app.db.models import KnowledgeCard
# from app.core.file_utils import extract_file_payload
# # 引入我们刚才在 generator.py 写的逻辑函数
# from app.agents.mechanism.generator import extract_knowledge_card_from_text
# from app.schemas.conversation import (
#     ConversationCreateRequest,
#     ConversationResponse,
#     ConversationStateSyncRequest,
#     EvalUpdateRequest,      # <--- 新增引入
#     ClassReportRequest      # <--- 新增引入
# )

# router = APIRouter(prefix="/conversations", tags=["conversations"])

# def _normalize_title(title: str | None) -> str:
#     title = (title or "").strip()
#     return title if title else "新对话"

# def _safe_json_loads(raw, fallback):
#     if raw is None:
#         return fallback
#     if isinstance(raw, (dict, list)):
#         return raw
#     try:
#         return json.loads(raw)
#     except Exception:
#         return fallback

# def _parse_classes(raw: str | None) -> list[str]:
#     if not raw:
#         return []
#     return [item.strip() for item in str(raw).split(",") if item.strip()]

# def _get_teacher_accessible_students(db: Session, teacher_id: str) -> list[User]:
#     teacher = db.query(User).filter(User.id == teacher_id).first()
#     if not teacher:
#         # 【核心修复】以前这里是 raise HTTPException(404)，查不到老师直接导致整个前端崩溃报404。
#         # 现在改为打印日志并返回空数组，彻底解决 404 挂掉的问题！
#         print(f"[DEBUG] 警告: 教师ID {teacher_id} 在数据库中未找到。")
#         return []

#     if teacher.role == "admin":
#         return db.query(User).filter(User.role == "student").all()

#     teacher_classes = _parse_classes(teacher.class_name)
#     if not teacher_classes:
#         return []

#     return (
#         db.query(User)
#         .filter(User.role == "student", User.class_name.in_(teacher_classes))
#         .all()
#     )

# def _build_teacher_summary(conversation: Conversation, student: User) -> dict:
#     chat_history = _safe_json_loads(conversation.chat_history, [])
#     return {
#         "id": conversation.id,
#         "student_id": conversation.student_id,
#         "student_name": student.real_name,
#         "class_name": student.class_name,
#         "title": conversation.title,
#         "chat_history": conversation.chat_history,
#         "bound_file_name": conversation.bound_file_name,
#         "bound_file_uploaded_at": conversation.bound_file_uploaded_at,
#         "bound_document_text": conversation.bound_document_text, 
#         "bound_file_uploaded_at": conversation.bound_file_uploaded_at,
#         "document_status": conversation.document_status,
#         "analysis_snapshot": conversation.analysis_snapshot,
#         "last_mode": conversation.last_mode,
#         "evaluation_report": conversation.evaluation_report, # <--- 新增这行，返回画像报告
#         "created_at": conversation.created_at,
#         "updated_at": conversation.updated_at,
#         "teacher_message_count": len(
#             [msg for msg in chat_history if isinstance(msg, dict) and msg.get("role") == "teacher"]
#         ),
#     }

# @router.post("/attachments/upload")
# async def upload_teacher_attachment(file: UploadFile = File(...)):
#     return await save_teacher_attachment(file)

# @router.get("/attachments/{file_id}")
# def download_teacher_attachment(file_id: str):
#     safe_name = Path(file_id).name
#     file_path = ATTACHMENT_ROOT / safe_name
#     if not file_path.exists():
#         raise HTTPException(status_code=404, detail="附件不存在")
#     download_name = safe_name.split("_", 1)[1] if "_" in safe_name else safe_name
#     return FileResponse(path=file_path, filename=download_name, media_type='application/octet-stream')

# @router.post("/", response_model=ConversationResponse)
# def create_conversation(
#     request: ConversationCreateRequest,
#     db: Session = Depends(get_db),
# ):
#     new_conversation = Conversation(
#         student_id=request.student_id,
#         title=_normalize_title(request.title),
#         chat_history="[]",
#         analysis_snapshot="{}",
#         document_status="none",
#         last_mode="learning",
#     )
#     db.add(new_conversation)
#     db.commit()
#     db.refresh(new_conversation)
#     return new_conversation

# @router.get("/", response_model=List[ConversationResponse])
# def get_conversations(
#     student_id: str,
#     db: Session = Depends(get_db),
# ):
#     conversations = (
#         db.query(Conversation)
#         .filter(Conversation.student_id == student_id)
#         .order_by(Conversation.updated_at.desc(), Conversation.created_at.desc())
#         .all()
#     )
#     return conversations

# # ==========================================
# # 教师端拉取全班项目的接口 (前端报错 404 的接口)
# # ==========================================
# @router.get("/teacher/projects")
# def get_teacher_project_conversations(
#     teacher_id: str = Query(...),
#     query: str = Query(default=""),
#     db: Session = Depends(get_db),
# ):
#     students = _get_teacher_accessible_students(db, teacher_id)
#     if not students:
#         return []

#     student_map = {student.id: student for student in students}
#     conversations = (
#         db.query(Conversation)
#         .filter(
#             Conversation.student_id.in_(list(student_map.keys())),
#             Conversation.document_status == "bound",
#         )
#         .all()
#     )

#     keyword = (query or "").strip().lower()
#     rows = []
#     for conversation in conversations:
#         student = student_map.get(conversation.student_id)
#         if not student:
#             continue
#         summary = _build_teacher_summary(conversation, student)
#         haystack = " ".join(
#             filter(
#                 None,
#                 [
#                     summary.get("title") or "",
#                     summary.get("student_name") or "",
#                     summary.get("bound_file_name") or "",
#                     summary.get("class_name") or "",
#                 ],
#             )
#         ).lower()
#         if keyword and keyword not in haystack:
#             continue
#         rows.append(summary)

#     rows.sort(
#         key=lambda item: (
#             item.get("bound_file_uploaded_at") or datetime.min,
#             item.get("updated_at") or datetime.min,
#             item.get("created_at") or datetime.min,
#         ),
#         reverse=True,
#     )
#     return rows


# @router.get("/teacher/projects/{conversation_id}")
# def get_teacher_project_conversation_detail(
#     conversation_id: str,
#     teacher_id: str = Query(...),
#     db: Session = Depends(get_db),
# ):
#     students = _get_teacher_accessible_students(db, teacher_id)
#     student_map = {student.id: student for student in students}

#     conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
#     if not conversation:
#         raise HTTPException(status_code=404, detail="会话不存在")

#     student = student_map.get(conversation.student_id)
#     if not student:
#         raise HTTPException(status_code=403, detail="当前教师无权访问该项目会话")

#     return _build_teacher_summary(conversation, student)


# # ==========================================
# # 卡片
# # ==========================================
# @router.post("/knowledge-cards/extract")
# async def extract_card_from_file(file: UploadFile = File(...)):
#     """
#     网络路由层：接收文件，调用 LLM，返回结果
#     """
#     # 1. 提取文件文本
#     payload = await extract_file_payload(file)
#     if not payload.get("supported") or not payload.get("text"):
#         raise HTTPException(status_code=400, detail="文件解析失败或内容为空")
    
#     file_text = payload["text"][:5000] # 截取前 5000 字
    
#     # 2. 调用业务逻辑层
#     try:
#         extracted_data = await extract_knowledge_card_from_text(file_text)
#         return extracted_data
#     except ValueError as ve:
#         raise HTTPException(status_code=500, detail=str(ve))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="系统内部错误，提取失败")

# @router.get("/knowledge-cards")
# def list_cards(db: Session = Depends(get_db)):
#     return db.query(KnowledgeCard).order_by(KnowledgeCard.created_at.desc()).all()

# @router.post("/knowledge-cards")
# def create_card(request: dict, db: Session = Depends(get_db)):
#     # 这里的 request 是前端提取成功后发送的完整字段
#     new_card = KnowledgeCard(**request)
#     db.add(new_card)
#     db.commit()
#     db.refresh(new_card)
#     return new_card

# @router.delete("/knowledge-cards/{card_id}")
# def delete_card(card_id: str, db: Session = Depends(get_db)):
#     card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
#     if not card:
#         raise HTTPException(status_code=404, detail="卡片不存在")
#     db.delete(card)
#     db.commit()
#     return {"status": "success"}

# @router.put("/knowledge-cards/{card_id}")
# def update_card(
#     card_id: str, 
#     request: dict = Body(...),  # 🌟 显式指定从 Body 获取数据
#     db: Session = Depends(get_db)
# ):
#     # 先查找是否存在
#     card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
#     if not card:
#         raise HTTPException(status_code=404, detail="卡片不存在")
    
#     try:
#         # 🌟 过滤掉不可更改的系统字段，只更新业务字段
#         # 这样可以防止前端传来的 id 字段触发数据库的主键更新冲突
#         for key, value in request.items():
#             if hasattr(card, key) and key not in ("id", "created_at", "updated_at"):
#                 setattr(card, key, value)
                
#         db.commit()
#         db.refresh(card)
#         return card
#     except Exception as e:
#         db.rollback() # 出错回滚，防止数据库 Session 挂起
#         print(f"[ERROR] 更新卡片失败: {str(e)}") # 后端日志打印具体错误
#         raise HTTPException(status_code=500, detail="数据库更新失败，请检查字段格式")

# # 这个接口由于名字太宽泛，一定要放在 /teacher/projects 下面
# @router.get("/{conversation_id}", response_model=ConversationResponse)
# def get_conversation_detail(
#     conversation_id: str,
#     db: Session = Depends(get_db),
# ):
#     conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
#     if not conversation:
#         raise HTTPException(status_code=404, detail="会话不存在")
#     return conversation


# @router.put("/{conversation_id}/bind-file", response_model=ConversationResponse)
# async def bind_conversation_file(
#     conversation_id: str,
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
#     if not conversation:
#         raise HTTPException(status_code=404, detail="会话不存在")

#     payload = await extract_file_payload(file)
#     if not payload["supported"]:
#         raise HTTPException(status_code=400, detail=payload["error"])

#     if not payload["text"].strip():
#         raise HTTPException(status_code=400, detail="上传文件解析后为空，无法绑定到该会话")

#     conversation.bound_file_name = payload["filename"]
#     conversation.bound_document_text = payload["text"]
#     conversation.bound_file_uploaded_at = datetime.utcnow()
#     conversation.document_status = "bound"

#     db.commit()
#     db.refresh(conversation)
#     return conversation


# @router.put("/{conversation_id}/state", response_model=ConversationResponse)
# def sync_conversation_state(
#     conversation_id: str,
#     request: ConversationStateSyncRequest,
#     db: Session = Depends(get_db),
# ):
#     conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
#     if not conversation:
#         raise HTTPException(status_code=404, detail="会话不存在")

#     conversation.chat_history = request.chat_history

#     if request.analysis_snapshot is not None:
#         conversation.analysis_snapshot = request.analysis_snapshot

#     if request.title is not None:
#         conversation.title = _normalize_title(request.title)

#     if request.last_mode is not None:
#         conversation.last_mode = request.last_mode

#     if request.kg_context is not None:
#         conversation.kg_context = request.kg_context

#     db.commit()
#     db.refresh(conversation)
#     return conversation

# # ==========================================
# # 报告持久化接口 (学生画像 & 班级学情)
# # ==========================================

# @router.put("/{conversation_id}/evaluation")
# def update_conversation_evaluation(
#     conversation_id: str, 
#     request: EvalUpdateRequest, 
#     db: Session = Depends(get_db)
# ):
#     conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
#     if not conversation:
#         raise HTTPException(status_code=404, detail="会话不存在")
#     conversation.evaluation_report = request.evaluation_report
#     db.commit()
#     return {"status": "success"}

# @router.get("/class-reports/{class_name}")
# def get_class_report(class_name: str, db: Session = Depends(get_db)):
#     report = db.query(ClassReport).filter(ClassReport.class_name == class_name).first()
#     return {"report_content": report.report_content if report else None}

# @router.put("/class-reports/{class_name}")
# def save_class_report(
#     class_name: str, 
#     request: ClassReportRequest, 
#     db: Session = Depends(get_db)
# ):
#     report = db.query(ClassReport).filter(ClassReport.class_name == class_name).first()
#     if not report:
#         report = ClassReport(class_name=class_name, report_content=request.report_content)
#         db.add(report)
#     else:
#         report.report_content = request.report_content
#     db.commit()
#     return {"status": "success"}