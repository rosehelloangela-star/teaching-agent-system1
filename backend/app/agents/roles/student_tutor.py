from typing import List

from pydantic import BaseModel, Field


class StudentTutorOutput(BaseModel):
    concept_definition: str = Field(description="核心概念定义")
    examples: str = Field(description="正例与反例讲解")
    common_mistakes: List[str] = Field(description="该概念的常见错误")
    next_task: str = Field(description="唯一的下一步练习任务")


STUDENT_TUTOR_CONFIG = {
    "role_id": "student_tutor",
    "goal": "解决冷启动问题，帮助学生完善所有产物在格式与内容上的完整性，消除知识盲区。",
    "focus": "概念覆盖率与先修路径",
    "output_schema": StudentTutorOutput,
}