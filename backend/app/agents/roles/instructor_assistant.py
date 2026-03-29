from typing import List

from pydantic import BaseModel, Field


class RiskProject(BaseModel):
    project_name: str = Field(description="项目/小组名称")
    risk_score: str = Field(description="综合风险评分（高严重度规则触发次数 + 证据缺口数量）")
    primary_issues: List[str] = Field(description="主要风险问题描述")


class InstructorAssistantOutput(BaseModel):
    knowledge_coverage: str = Field(description="知识覆盖情况与常见错误统计")
    hypergraph_triggers: str = Field(description="超图一致性规则触发占比（反映逻辑问题高发点）")
    rubric_distribution: str = Field(description="Rubric得分率与分布（反映能力维度薄弱项）")
    risk_list: List[RiskProject] = Field(description="高风险项目名单（Risk List）")
    teaching_suggestions: str = Field(description="教学干预建议与一键布置作业的推荐内容")


INSTRUCTOR_ASSISTANT_CONFIG = {
    "role_id": "instructor_assistant",
    "goal": "将分散在多份作业中的问题聚合为班级画像，识别共性短板、安排课堂重点与设定干预策略。",
    "focus": "班级统计、高风险识别与教学干预建议",
    "output_schema": InstructorAssistantOutput,
}