from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# 用于规范前端发来的聊天记录数据
class ChatSyncRequest(BaseModel):
    chat_history: str  # 接收 JSON 字符串

class ProjectResponse(BaseModel):
    id: str
    name: str
    student_id: str
    content: Optional[str] = None
    file_name: Optional[str] = None
    chat_history: Optional[str] = "[]" # 【新增这行】
    status: str
    instructor_notes: Optional[str] = None
    assessment_result: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)