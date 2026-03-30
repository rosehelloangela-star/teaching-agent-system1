from pydantic import BaseModel, Field

class StudentTutorOutput(BaseModel):
    is_refused: bool = Field(description="是否检测到直接代写请求，如果是则设为 true")
    reply: str = Field(description="智能体的完整回复内容。使用 Markdown 分点分段排版，清晰包含概念、案例、任务或启发式提问。")

STUDENT_TUTOR_CONFIG = {
    "role_id": "student_tutor",
    "goal": "充当“知识布道者”。负责解答专业概念、调用图谱提供真实案例、布置单项实操任务。自带严格的“反代写”安全护栏。",
    "focus": "启发式教学、反代写拦截与 Markdown 结构化文本输出",
    "output_schema": StudentTutorOutput,
}

# from typing import List

# from pydantic import BaseModel, Field


# class StudentTutorOutput(BaseModel):
#     concept_definition: str = Field(description="核心概念定义")
#     examples: str = Field(description="正例与反例讲解")
#     common_mistakes: List[str] = Field(description="该概念的常见错误")
#     next_task: str = Field(description="唯一的下一步练习任务")


# STUDENT_TUTOR_CONFIG = {
#     "role_id": "student_tutor",
#     "goal": "解决冷启动问题，帮助学生完善所有产物在格式与内容上的完整性，消除知识盲区。",
#     "focus": "概念覆盖率与先修路径",
#     "output_schema": StudentTutorOutput,
# }