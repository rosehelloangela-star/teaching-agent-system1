import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from app.agents.mechanism.llm_config import get_llm
from app.core.json_utils import message_content_to_text, parse_pydantic_from_text
from app.agents.roles import ROLE_CONFIG_REGISTRY
from app.core.stream_logger import log_and_emit


def _build_output_contract(role_id: str) -> str:
    if role_id == "project_coach":
        return (
            '{\n'
            '  "logic_flaw": "一致性缺陷诊断报告",\n'
            '  "evidence_gap": "逻辑缺口证据",\n'
            '  "only_one_task": "唯一最高优先级修复任务",\n'
            '  "acceptance_criteria": "验收标准"\n'
            '}'
        )
    if role_id == "student_tutor":
        return (
            '{\n'
            '  "concept_definition": "核心概念定义",\n'
            '  "examples": "正例与反例讲解",\n'
            '  "common_mistakes": ["错误1", "错误2"],\n'
            '  "next_task": "唯一下一步任务"\n'
            '}'
        )
    if role_id == "competition_advisor":
        return (
            '{\n'
            '  "rubric_scores": "Rubric分数表",\n'
            '  "deduction_evidence": "扣分证据",\n'
            '  "top_tasks": [\n'
            '    {\n'
            '      "task_desc": "任务描述",\n'
            '      "roi_reason": "高性价比理由",\n'
            '      "template_example": "模板示例",\n'
            '      "timeframe": "24h或72h"\n'
            '    }\n'
            '  ]\n'
            '}'
        )
    if role_id == "instructor_assistant":
        return (
            '{\n'
            '  "knowledge_coverage": "知识覆盖统计",\n'
            '  "hypergraph_triggers": "规则触发占比",\n'
            '  "rubric_distribution": "Rubric分布",\n'
            '  "risk_list": [\n'
            '    {\n'
            '      "project_name": "项目名",\n'
            '      "risk_score": "高/中/低",\n'
            '      "primary_issues": ["问题1", "问题2"]\n'
            '    }\n'
            '  ],\n'
            '  "teaching_suggestions": "教学干预建议"\n'
            '}'
        )
    if role_id == "assessment_assistant":
        return (
            '{\n'
            '  "rubric_table": [\n'
            '    {\n'
            '      "dimension": "评分维度",\n'
            '      "score": 1,\n'
            '      "evidence_trace": "证据片段"\n'
            '    }\n'
            '  ],\n'
            '  "revision_suggestions": "修订建议",\n'
            '  "feedback_templates": "反馈模板"\n'
            '}'
        )
    return "{}"


def generator_node(state: dict) -> dict:
    role_id = state.get("selected_role", "student_tutor")
    role_config = ROLE_CONFIG_REGISTRY.get(role_id, {})
    schema = role_config.get("output_schema")

    diagnosis_text = state.get("critic_diagnosis", {}).get("raw_analysis", "")
    tasks_text = json.dumps(state.get("planned_tasks", []), ensure_ascii=False, indent=2)
    errors = state.get("validation_errors") or "无"
    user_input = state.get("user_input", "")

    llm = get_llm(temperature=0.3, max_tokens=420)
    output_contract = _build_output_contract(role_id)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "你是创新创业教学智能体的内容生成器。\n"
                    "请只返回一个合法 JSON 对象。\n"
                    "不要解释，不要 markdown，不要 ```json，不要 。\n"
                    "字段名必须完全一致，不能遗漏，不能增加。\n"
                    "输出合同如下：\n"
                    "{output_contract}"
                ),
            ),
            (
                "user",
                (
                    "原始输入：\n{user_input}\n\n"
                    "诊断信息：\n{diagnosis}\n\n"
                    "任务规划：\n{tasks}\n\n"
                    "上一次校验错误（如有请修正）：\n{errors}"
                ),
            ),
        ]
    )

    chain = prompt | llm
    log_and_emit(state, "generator", "正在调用模型合成最终反馈...")
    
    response = chain.invoke(
        {
            "output_contract": output_contract,
            "user_input": user_input,
            "diagnosis": diagnosis_text,
            "tasks": tasks_text,
            "errors": errors,
        }
    )
    raw_text = message_content_to_text(response)
    parsed_model = parse_pydantic_from_text(raw_text, schema)
    log_and_emit(state, "generator", "模型返回且解析成功。")

    final_content = parsed_model.model_dump()
    return {
        "generated_content": final_content,
        "attempt_count": state.get("attempt_count", 0) + 1,
        "messages": [AIMessage(content=json.dumps(final_content, ensure_ascii=False, indent=2))],
    }
