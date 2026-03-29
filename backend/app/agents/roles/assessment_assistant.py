from typing import List

from pydantic import BaseModel, Field


class RubricEvaluation(BaseModel):
    dimension: str = Field(description="评分维度")
    score: int = Field(description="评分（0/1/3/5锚点）")
    evidence_trace: str = Field(description="可追溯的Evidence Trace片段（来源于学生文本）")


class AssessmentAssistantOutput(BaseModel):
    rubric_table: List[RubricEvaluation] = Field(description="包含证据链的Rubric表格")
    revision_suggestions: str = Field(description="具体的修订建议")
    feedback_templates: str = Field(description="供教师快速确认、一键发放的可选反馈话术")


ASSESSMENT_ASSISTANT_CONFIG = {
    "role_id": "assessment_assistant",
    "goal": "面向单份作业提供可复核的评价依据，实现可追溯、可复核的评价闭环。",
    "focus": "Rubric表格输出、Evidence Trace追踪与可发放反馈",
    "output_schema": AssessmentAssistantOutput,
}