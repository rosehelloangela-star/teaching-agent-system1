from typing import List
from pydantic import BaseModel, Field

class CapabilityItem(BaseModel):
    dimension: str = Field(description="核心能力维度，必须涵盖：痛点发现(Empathy)、方案策划(Ideation)、商业建模(Business)、资源杠杆(Execution)、逻辑表达(Logic)")
    score: int = Field(description="量化打分 (0-5分)")
    reason: str = Field(description="得分的简要依据")

class StageDiagnosisItem(BaseModel):
    stage_name: str = Field(description="阶段名称，如：第一轮（核心价值探测）、第二轮（逻辑压力测试）、第三轮（落地可行性）")
    performance: str = Field(description="该阶段的学生行为与思维表现诊断总结")

class EvidenceItem(BaseModel):
    student_quote: str = Field(description="直接引用对话日志中的学生原话（必须是原话）")
    implication: str = Field(description="该原话反映出的能力亮点或思维缺陷/逻辑断层")

class ProfileEvaluatorOutput(BaseModel):
    capabilities: List[CapabilityItem] = Field(description="核心能力打分")
    stage_diagnoses: List[StageDiagnosisItem] = Field(description="三轮对话行为诊断")
    evidences: List[EvidenceItem] = Field(description="引用的原始证据链")

PROFILE_EVALUATOR_CONFIG = {
    "role_id": "profile_evaluator",
    "goal": "将学生与AI的多轮对抗式对话历史，转化为结构化的能力评估报告。",
    "focus": "严格按照能力映射图谱输出0-5分，总结三阶段表现，并必须引用学生原话作为证据。",
    "output_schema": ProfileEvaluatorOutput,
}