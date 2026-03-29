from pydantic import BaseModel, Field


class ProjectCoachOutput(BaseModel):
    logic_flaw: str = Field(description="一致性缺陷诊断报告")
    evidence_gap: str = Field(description="支撑诊断的逻辑缺口证据")
    only_one_task: str = Field(description="唯一最高优先级的修复任务")
    acceptance_criteria: str = Field(description="该任务的验证验收标准")


PROJECT_COACH_CONFIG = {
    "role_id": "project_coach",
    "goal": "对学生项目进行深层商业逻辑压力测试，确保项目证据链与逻辑链的一致性与闭环闭合。",
    "focus": "超图一致性规则与单任务推进",
    "output_schema": ProjectCoachOutput,
}