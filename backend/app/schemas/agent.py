# from typing import Any, Dict, List

# from pydantic import BaseModel, Field


# class AgentRunRequest(BaseModel):
#     user_input: str = Field(description="用户提交的文本内容")
#     current_mode: str = Field(default="learning", description="运行模式：learning/project/competition/instructor/assessment")
#     max_retry: int = Field(default=2, ge=0, le=5, description="结构校验失败后的最大重试次数")


# class AgentRunResponse(BaseModel):
#     current_mode: str
#     selected_role: str
#     critic_diagnosis: Dict[str, Any]
#     planned_tasks: List[Dict[str, Any]]
#     generated_content: Dict[str, Any]
#     validation_status: bool
#     validation_errors: str
#     attempt_count: int
#     thread_id: str

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    user_input: str = Field(description="用户提交的文本内容")
    current_mode: str = Field(default="learning", description="运行模式：learning/project/competition/instructor/assessment")
    max_retry: int = Field(default=2, ge=0, le=5, description="结构校验失败后的最大重试次数")


class AgentRunResponse(BaseModel):
    current_mode: str
    selected_role: str

    critic_diagnosis: Dict[str, Any]
    planned_tasks: List[Dict[str, Any]]
    generated_content: Dict[str, Any]

    validation_status: bool
    validation_errors: str
    attempt_count: int
    thread_id: str

    # 新增：供自由对话会话使用
    conversation_id: Optional[str] = None
    document_status: str = "none"
    bound_file_name: Optional[str] = None
    bound_file_uploaded_at: Optional[datetime] = None
    analysis_snapshot: Dict[str, Any] = Field(default_factory=dict)
    # 【新增】传递超图可视化数据到前端分析面板
    hypergraph_data: Dict[str, Any] = Field(default_factory=dict)