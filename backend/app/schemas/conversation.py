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


class ConversationResponse(BaseModel):
    id: str
    student_id: str
    title: str

    chat_history: str = "[]"

    bound_file_name: Optional[str] = None
    bound_file_uploaded_at: Optional[datetime] = None
    document_status: str = "none"

    analysis_snapshot: str = "{}"
    last_mode: str = "learning"
    
    # 【新增字段】：用于返回已保存的学生画像报告
    evaluation_report: Optional[str] = None 

    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# 【新增模型】：用于保存画像和班级报告的请求体
class EvalUpdateRequest(BaseModel):
    evaluation_report: str

class ClassReportRequest(BaseModel):
    report_content: str