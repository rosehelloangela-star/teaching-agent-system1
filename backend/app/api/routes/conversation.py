import json
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.file_utils import extract_file_payload
from app.db.database import get_db
from app.db.models import Conversation
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationResponse,
    ConversationStateSyncRequest,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _normalize_title(title: str | None) -> str:
    title = (title or "").strip()
    return title if title else "新对话"


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