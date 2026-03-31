from typing import List

from pydantic import BaseModel, Field


class ImprovementTask(BaseModel):
    task_desc: str = Field(description="任务描述")
    roi_reason: str = Field(description="高性价比提分理由（权重×提分空间/成本）")
    template_example: str = Field(description="对应的模板或示例")
    timeframe: str = Field(description="24h或72h快速补救方案")


class CompetitionRubricAssessment(BaseModel):
    dimension_id: str = Field(description="Rubric 维度ID，必须与系统提供的模板维度一致")
    estimated_score: float = Field(description="0到5之间的预估得分", ge=0, le=5)
    score_reason: str = Field(description="该维度的评分解释")
    missing_evidence: List[str] = Field(
        default_factory=list,
        description="若不是高分，必须明确指出当前材料缺少的客观支撑",
    )
    minimal_fix_24h: str = Field(description="24小时内最小可交付修复")
    minimal_fix_72h: str = Field(description="72小时内增强版修复")


class CompetitionAdvisorOutput(BaseModel):
    is_refused: bool = Field(default=False, description="是否触发安全护栏")
    reply: str = Field(description="对学生展示的 Markdown 富文本回复")
    rubric_items: List[CompetitionRubricAssessment] = Field(
        description="逐维度结构化评分结果",
        min_length=8,
        max_length=12,
    )
    top_tasks: List[ImprovementTask] = Field(
        description="Top提分任务清单（最多3条），强调短周期可提升",
        max_length=3,
    )
    quick_questions: List[str] = Field(
        default_factory=list,
        description="给学生继续追问的关键问题，最多3条",
        max_length=3,
    )


COMPETITION_ADVISOR_CONFIG = {
    "role_id": "competition_advisor",
    "goal": "帮助学生快速对标并适配特定竞赛，基于动态 Rubric 给出逐项评分、缺口证据与24h/72h修复路径。",
    "focus": "赛事识别、Rubric 动态切换、逐项评分、缺口证据与高性价比提分",
    "output_schema": CompetitionAdvisorOutput,
}
