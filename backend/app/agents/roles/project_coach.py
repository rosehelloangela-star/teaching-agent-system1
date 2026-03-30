from pydantic import BaseModel, Field

class ProjectCoachOutput(BaseModel):
    # --- 聊天专用字段 ---
    is_refused: bool = Field(description="是否检测到直接代写请求，如果是则设为 true")
    reply: str = Field(description="智能体在聊天框的回复内容。使用带有丰富格式的 Markdown 排版。")
    
    # --- 后台面板专用字段（供 Snapshot Overlay 使用） ---
    logic_flaw: str = Field(description="一致性缺陷诊断报告（20-50字凝练）")
    evidence_gap: str = Field(description="逻辑缺口证据（指出缺失了什么数据或推导）")
    only_one_task: str = Field(description="唯一最高优先级的修复任务名称")
    acceptance_criteria: str = Field(description="该修复任务的验收标准")

PROJECT_COACH_CONFIG = {
    "role_id": "project_coach",
    "goal": "对学生项目进行深层商业逻辑压力测试，确保项目证据链与逻辑链的一致性与闭环闭合。",
    "focus": "商业逻辑压力测试、苏格拉底式发问与单任务推进",
    "output_schema": ProjectCoachOutput,
}