from typing import List

from pydantic import BaseModel, Field


class ImprovementTask(BaseModel):
    task_desc: str = Field(description="任务描述")
    roi_reason: str = Field(description="高性价比提分理由（权重×提分空间/成本）")
    template_example: str = Field(description="对应的模板或示例")
    timeframe: str = Field(description="24h或72h快速补救方案")


class CompetitionAdvisorOutput(BaseModel):
    rubric_scores: str = Field(description="Rubric分数表（各维度得分）")
    deduction_evidence: str = Field(description="扣分点证据与解释")
    top_tasks: List[ImprovementTask] = Field(
        description="Top提分任务清单（最多3条），强调短周期可提升",
        max_length=3,
    )


COMPETITION_ADVISOR_CONFIG = {
    "role_id": "competition_advisor",
    "goal": "帮助学生快速对标并适配特定竞赛，提供扣分证据与高性价比提分策略，强调短周期可提升。",
    "focus": "目标对标、证据扣分与高性价比提分",
    "output_schema": CompetitionAdvisorOutput,
}