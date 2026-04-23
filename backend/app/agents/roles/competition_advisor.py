# from typing import List

# from pydantic import BaseModel, Field


# class ImprovementTask(BaseModel):
#     task_desc: str = Field(description="任务描述")
#     roi_reason: str = Field(description="高性价比提分理由（权重×提分空间/成本）")
#     template_example: str = Field(description="对应的模板或示例")
#     timeframe: str = Field(description="24h或72h快速补救方案")


# class CompetitionRubricAssessment(BaseModel):
#     dimension_id: str = Field(description="Rubric 维度ID，必须与系统提供的模板维度一致")
#     estimated_score: float = Field(description="0到5之间的预估得分", ge=0, le=5)
#     score_reason: str = Field(description="该维度的评分解释")
#     missing_evidence: List[str] = Field(
#         default_factory=list,
#         description="若不是高分，必须明确指出当前材料缺少的客观支撑",
#     )
#     minimal_fix_24h: str = Field(description="24小时内最小可交付修复")
#     minimal_fix_72h: str = Field(description="72小时内增强版修复")


# class CompetitionAdvisorOutput(BaseModel):
#     is_refused: bool = Field(default=False, description="是否触发安全护栏")
#     reply: str = Field(description="对学生展示的 Markdown 富文本回复")
#     rubric_items: List[CompetitionRubricAssessment] = Field(
#         description="逐维度结构化评分结果",
#         min_length=8,
#         max_length=12,
#     )
#     top_tasks: List[ImprovementTask] = Field(
#         description="Top提分任务清单（最多3条），强调短周期可提升",
#         max_length=3,
#     )
#     quick_questions: List[str] = Field(
#         default_factory=list,
#         description="给学生继续追问的关键问题，最多3条",
#         max_length=3,
#     )


# COMPETITION_ADVISOR_CONFIG = {
#     "role_id": "competition_advisor",
#     "goal": "帮助学生快速对标并适配特定竞赛，基于动态 Rubric 给出逐项评分、缺口证据与24h/72h修复路径。",
#     "focus": "赛事识别、Rubric 动态切换、逐项评分、缺口证据与高性价比提分",
#     "output_schema": CompetitionAdvisorOutput,
# }




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


class JudgeQuestionCard(BaseModel):
    # 最终输出理论上会在 generator 中被补齐；这里保留宽松默认值，
    # 防止个别字段漏生导致整个竞赛模式回复失败。
    expert_id: str = Field(default="", description="评委身份ID")
    expert_role: str = Field(default="", description="评委身份，例如商业模式与财务评委")
    expert_domain: str = Field(default="", description="评委所属领域，例如商业/财务")
    target_dimension_id: str = Field(default="", description="本条追问主要针对的 Rubric 维度ID")
    target_dimension_name: str = Field(default="", description="本条追问主要针对的 Rubric 维度名称")
    pressure_level: str = Field(default="", description="追问强度标签，例如高压追问/证据追问")
    attack_point: str = Field(default="", description="该问题盯住的薄弱点")
    question: str = Field(default="", description="评委会直接抛出的毒舌问题")
    evidence_hint: str = Field(default="", description="学生回答时最应该补齐的证据提示")


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
        description="给学生继续追问的关键问题，最多3条；用于兼容旧前端字段",
        max_length=3,
    )
    judge_questions: List[JudgeQuestionCard] = Field(
        default_factory=list,
        description="结构化模拟评委毒舌追问卡片，最多3条",
        max_length=3,
    )


COMPETITION_ADVISOR_CONFIG = {
    "role_id": "competition_advisor",
    "goal": "帮助学生快速对标并适配特定竞赛，基于动态 Rubric 给出逐项评分、缺口证据与24h/72h修复路径。",
    "focus": "赛事识别、Rubric 动态切换、逐项评分、缺口证据与高性价比提分",
    "output_schema": CompetitionAdvisorOutput,
}
