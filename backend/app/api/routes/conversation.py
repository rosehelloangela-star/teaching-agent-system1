# import json
# from datetime import datetime
# from typing import List

# from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
# from sqlalchemy.orm import Session

# from app.core.file_utils import extract_file_payload
# from app.db.database import get_db
# from app.db.models import Conversation, User
# from app.schemas.conversation import (
#     ConversationCreateRequest,
#     ConversationResponse,
#     ConversationStateSyncRequest,
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
#         raise HTTPException(status_code=404, detail="教师不存在")

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
#         "document_status": conversation.document_status,
#         "analysis_snapshot": conversation.analysis_snapshot,
#         "last_mode": conversation.last_mode,
#         "created_at": conversation.created_at,
#         "updated_at": conversation.updated_at,
#         "teacher_message_count": len(
#             [msg for msg in chat_history if isinstance(msg, dict) and msg.get("role") == "teacher"]
#         ),
#     }


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

#     db.commit()
#     db.refresh(conversation)
#     return conversation



import json
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.file_utils import ATTACHMENT_ROOT, extract_file_payload, save_teacher_attachment
from app.db.database import get_db
from app.db.models import Conversation, User
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationResponse,
    ConversationStateSyncRequest,
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
        raise HTTPException(status_code=404, detail="教师不存在")

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
        "document_status": conversation.document_status,
        "analysis_snapshot": conversation.analysis_snapshot,
        "last_mode": conversation.last_mode,
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


@router.get("/", response_model=List[ConversationResponse])
def get_conversations(
    student_id: str,
    db: Session = Depends(get_db),
):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.student_id == student_id)
        .order_by(Conversation.updated_at.desc(), Conversation.created_at.desc())
        .all()
    )
    return conversations


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

    db.commit()
    db.refresh(conversation)
    return conversation
