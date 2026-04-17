from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreateRequest(BaseModel):
    student_id: str
    title: str = Field(default="新对话")


class ConversationStateSyncRequest(BaseModel):
    chat_history: str
    analysis_snapshot: Optional[str] = None
    title: Optional[str] = None
    last_mode: Optional[str] = None
    kg_context: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    student_id: str
    title: str

    chat_history: str = "[]"

    bound_file_name: Optional[str] = None
    bound_document_text: str | None = None 
    bound_file_uploaded_at: datetime | None = None
    document_status: str = "none"

    analysis_snapshot: str = "{}"
    last_mode: str = "learning"

    created_at: datetime
    updated_at: Optional[datetime] = None
    kg_context: str | None = None

    model_config = ConfigDict(from_attributes=True)

class EvalUpdateRequest(BaseModel):
    evaluation_report: str  # 接收前端传来的 JSON 字符串或文本

class ClassReportRequest(BaseModel):
    report_content: str     # 接收前端传来的班级报告内容