import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from app.agents.mechanism.llm_config import get_llm
from app.core.json_utils import message_content_to_text, parse_pydantic_from_text
from app.agents.roles import ROLE_CONFIG_REGISTRY
from app.core.stream_logger import log_and_emit

def _build_output_contract(role_id: str) -> str:
    # 【核心修改】项目模式的输出合同现在是“双轨”的
    if role_id == "project_coach":
        return (
            '{\n'
            '  "is_refused": false,\n'
            '  "reply": "带有 Markdown 排版的对话回复文本",\n'
            '  "logic_flaw": "面板数据-逻辑缺陷",\n'
            '  "evidence_gap": "面板数据-证据缺口",\n'
            '  "only_one_task": "面板数据-唯一任务",\n'
            '  "acceptance_criteria": "面板数据-验收标准"\n'
            '}'
        )
    if role_id == "student_tutor":
        return '{\n  "is_refused": false,\n  "reply": "在此处输出带有丰富 Markdown 排版的对话文本。"\n}'
    if role_id == "competition_advisor":
        return '{\n  "rubric_scores": "Rubric分数表",\n  "deduction_evidence": "扣分证据",\n  "top_tasks": [\n    {\n      "task_desc": "任务描述",\n      "roi_reason": "高性价比理由",\n      "template_example": "模板示例",\n      "timeframe": "24h或72h"\n    }\n  ]\n}'
    if role_id == "instructor_assistant":
        return '{\n  "knowledge_coverage": "知识覆盖统计",\n  "hypergraph_triggers": "规则触发占比",\n  "rubric_distribution": "Rubric分布",\n  "risk_list": [\n    {\n      "project_name": "项目名",\n      "risk_score": "高/中/低",\n      "primary_issues": ["问题1", "问题2"]\n    }\n  ],\n  "teaching_suggestions": "教学干预建议"\n}'
    if role_id == "assessment_assistant":
        return '{\n  "rubric_table": [\n    {\n      "dimension": "评分维度",\n      "score": 1,\n      "evidence_trace": "证据片段"\n    }\n  ],\n  "revision_suggestions": "修订建议",\n  "feedback_templates": "反馈模板"\n}'
    return "{}"

def generator_node(state: dict) -> dict:
    role_id = state.get("selected_role", "student_tutor")
    role_config = ROLE_CONFIG_REGISTRY.get(role_id, {})
    schema = role_config.get("output_schema")
    if state.get("llm_unavailable"):
        log_and_emit(state, "generator", "检测到模型诊断阶段不可用，中断生成。", level="error")
        raise RuntimeError("大语言模型当前不可用，请检查网络或配置。")
        
    diagnosis_text = state.get("critic_diagnosis", {}).get("raw_analysis", "")
    tasks_text = json.dumps(state.get("planned_tasks", []), ensure_ascii=False, indent=2)
    errors = state.get("validation_errors") or "无"
    user_input = state.get("user_input", "")
    
    llm = get_llm(temperature=0.3, max_tokens=2000)
    
    output_contract = _build_output_contract(role_id)
    
    system_prompt_text = (
        "你是创新创业教学智能体的内容生成器。\n"
        "请按要求生成回复，并【必须且只能】返回一个合法的 JSON 对象。\n"
        "【格式要求】：直接输出大括号 {{ }}，不要包含任何解释文字，不要使用 ```json 代码块。\n"
        "【换行要求】：在 reply 等字符串中，如果需要换行（如 Markdown 的段落），请务必使用 '\\n' 进行转义，不要直接物理回车换行。\n"
    )

    if role_id == "student_tutor":
        system_prompt_text += (
            "\n【排版与启发式教学规则（最高优先级）】\n"
            "1. 视觉渲染：你必须充分利用 Markdown 语法来增强阅读体验！\n"
            "   - 使用 **加粗** 来强调关键术语和重点句。\n"
            "   - 使用 > 引用块 来展示具体案例或原话说明。\n"
            "   - 使用 ### 作为小标题来区分段落。\n"
            "\n"
            "2. 反代写红线：如果学生要求“直接写”、“生成商业计划书”、“帮我完善这段话”等代写请求，必须设 is_refused = true。\n"
            "   - 若触发反代写，`reply` 第一句必须温和但坚定地拒绝（例如：“同学你好，根据我们的教学原则，我不能直接替你写这段内容哦，不过我可以陪你一起梳理思路。”）。\n"
            "   - 拒绝后，直接在 `reply` 中抛出 2 到 3 个苏格拉底式启发问题，让学生先回答。\n"
            "\n"
            "3. 显性结构化：在 reply 中，你必须使用 Markdown 标题（如 `### 📖 概念解析`）依次包含以下 6 个必选结构：\n"
            "   ### 📖 概念解析（结合图谱客观依据，精准定义）\n"
            "   ### 💡 项目案例（使用 > 引用块 给出通俗易懂的例子）\n"
            "   ### ⚠️ 避坑指南（提醒学生历史高发的一个坑（防幻觉，依诊断信息））\n"
            "   ### 🎯 实操任务（每次【只布置一个】最小阻力的小任务。）\n"
            "   ### 📦 交付要求（告诉学生具体要交给你什么（比如：一句话、三个标签）。）\n"
            "   ### ⚖️ 评价标准（告诉学生你会用什么标准来评判对错。）\n"
            "\n"
            "4. 苏格拉底式收尾：`reply` 的结尾必须抛出一个具有启发性的问题，把话筒交给学生！\n"
            "   - 示例范音：“我们先不着急写整段，咱们一步一步来。结合你的项目，你觉得你的目标用户第一痛点是什么？我们先聊聊这个？”\n"
        )
    elif role_id == "project_coach":
        # 【核心修改】明确赋予它双重任务
        system_prompt_text += (
            "\n【双轨任务指令（最高优先级）】\n"
            "你现在肩负双重任务：1. 生成给前端面板的后台结构化数据； 2. 在 reply 字段中生成与学生的真实对话。\n"
            "\n"
            "【任务一：生成后台数据（logic_flaw 等字段）】\n"
            "请严格参考诊断信息，用较精炼但全面的语言（50-100字）填入 logic_flaw, evidence_gap, only_one_task, acceptance_criteria 字段。\n"
            "\n"
            "【任务二：撰写对话文本（reply 字段）】\n"
            "1. 视觉渲染：必须充分利用 Markdown 语法（**加粗**、> 引用块、### 标题、- 列表）。\n"
            "2. 反代写拦截：面对学生要求直接罗列答案时，设 is_refused = true，在 reply 开头强硬拒绝。\n"
            "3. 显性结构化：在 reply 中，必须按顺序使用 Markdown 小标题包含以下 5 个模块：\n"
            "   ### 📍 项目所处阶段（明确指出是 想法期 / 原型期 / 验证期 之一）\n"
            "   ### 🩺 当前核心诊断（指出最大矛盾或缺口）\n"
            "   ### 🔎 诊断证据追踪（> 引用原文本或诊断信息说明依据）\n"
            "   ### ⚠️ 风险预警（说明不修复的致命后果）\n"
            "   ### 🎯 破局任务（结合前面的 only_one_task，给出执行模板/步骤）\n"
            "\n"
            "4. 非对称信息获取与压力测试（核心灵魂）：在 reply 的最后，你必须从以下 3 层逻辑中【选择最致命的 1 到 2 个】作为苏格拉底式追问收尾：\n"
            "   - 逻辑1【寻找隐形替代品】：引导从产品形态转向任务目标。用户的零成本方案/旧习惯都是你的竞争对手。\n"
            "   - 逻辑2【模拟巨头入场】：如果字节/腾讯内置了这个功能免费做，你的护城河在哪？\n"
            "   - 逻辑3【成本转换与生存测试】：这提升的体验能覆盖用户迁移成本吗？不融资你能活多久？\n"
        )

    system_prompt_text += "\n输出格式参考如下：\n{output_contract}"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_text),
        ("user", "原始输入：\n{user_input}\n\n诊断信息：\n{diagnosis}\n\n任务规划：\n{tasks}\n\n上一次校验错误：\n{errors}")
    ])
    
    chain = prompt | llm
    log_and_emit(state, "generator", "正在调用模型合成最终反馈...")
    
    try:
        response = chain.invoke({
            "output_contract": output_contract,
            "user_input": user_input,
            "diagnosis": diagnosis_text,
            "tasks": tasks_text,
            "errors": errors,
        })
        raw_text = message_content_to_text(response).strip()
        
        print(f"\n========== [Generator Debug] ==========\n大模型原始输出内容：\n[{raw_text}]\n=======================================\n", flush=True)
        
        if not raw_text:
            raise ValueError("大模型返回了完全空白的字符串！可能是触发了API平台安全护栏，或超出了输出限制。")

        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        parsed_model = parse_pydantic_from_text(raw_text.strip(), schema)
        log_and_emit(state, "generator", "模型返回且解析成功。")
        
        final_content = parsed_model.model_dump()
        return {
            "generated_content": final_content,
            "attempt_count": state.get("attempt_count", 0) + 1,
            "messages": [AIMessage(content=json.dumps(final_content, ensure_ascii=False, indent=2))],
        }
    except Exception as e:
        log_and_emit(state, "generator", f"模型调用或解析失败：{e}", level="error")
        raise ValueError(f"生成器执行失败，未能生成有效格式：{str(e)}")

# import json
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.messages import AIMessage
# from app.agents.mechanism.llm_config import get_llm
# from app.core.json_utils import message_content_to_text, parse_pydantic_from_text
# from app.agents.roles import ROLE_CONFIG_REGISTRY
# from app.core.stream_logger import log_and_emit


# def _build_output_contract(role_id: str) -> str:
#     if role_id == "project_coach":
#         return (
#             '{\n'
#             '  "logic_flaw": "一致性缺陷诊断报告",\n'
#             '  "evidence_gap": "逻辑缺口证据",\n'
#             '  "only_one_task": "唯一最高优先级修复任务",\n'
#             '  "acceptance_criteria": "验收标准"\n'
#             '}'
#         )
#     if role_id == "student_tutor":
#         return (
#             '{\n'
#             '  "concept_definition": "核心概念定义",\n'
#             '  "examples": "正例与反例讲解",\n'
#             '  "common_mistakes": ["错误1", "错误2"],\n'
#             '  "next_task": "唯一下一步任务"\n'
#             '}'
#         )
#     if role_id == "competition_advisor":
#         return (
#             '{\n'
#             '  "rubric_scores": "Rubric分数表",\n'
#             '  "deduction_evidence": "扣分证据",\n'
#             '  "top_tasks": [\n'
#             '    {\n'
#             '      "task_desc": "任务描述",\n'
#             '      "roi_reason": "高性价比理由",\n'
#             '      "template_example": "模板示例",\n'
#             '      "timeframe": "24h或72h"\n'
#             '    }\n'
#             '  ]\n'
#             '}'
#         )
#     if role_id == "instructor_assistant":
#         return (
#             '{\n'
#             '  "knowledge_coverage": "知识覆盖统计",\n'
#             '  "hypergraph_triggers": "规则触发占比",\n'
#             '  "rubric_distribution": "Rubric分布",\n'
#             '  "risk_list": [\n'
#             '    {\n'
#             '      "project_name": "项目名",\n'
#             '      "risk_score": "高/中/低",\n'
#             '      "primary_issues": ["问题1", "问题2"]\n'
#             '    }\n'
#             '  ],\n'
#             '  "teaching_suggestions": "教学干预建议"\n'
#             '}'
#         )
#     if role_id == "assessment_assistant":
#         return (
#             '{\n'
#             '  "rubric_table": [\n'
#             '    {\n'
#             '      "dimension": "评分维度",\n'
#             '      "score": 1,\n'
#             '      "evidence_trace": "证据片段"\n'
#             '    }\n'
#             '  ],\n'
#             '  "revision_suggestions": "修订建议",\n'
#             '  "feedback_templates": "反馈模板"\n'
#             '}'
#         )
#     return "{}"


# def generator_node(state: dict) -> dict:
#     role_id = state.get("selected_role", "student_tutor")
#     role_config = ROLE_CONFIG_REGISTRY.get(role_id, {})
#     schema = role_config.get("output_schema")

#     diagnosis_text = state.get("critic_diagnosis", {}).get("raw_analysis", "")
#     tasks_text = json.dumps(state.get("planned_tasks", []), ensure_ascii=False, indent=2)
#     errors = state.get("validation_errors") or "无"
#     user_input = state.get("user_input", "")

#     llm = get_llm(temperature=0.3, max_tokens=420)
#     output_contract = _build_output_contract(role_id)

#     prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 (
#                     "你是创新创业教学智能体的内容生成器。\n"
#                     "请只返回一个合法 JSON 对象。\n"
#                     "不要解释，不要 markdown，不要 ```json，不要 。\n"
#                     "字段名必须完全一致，不能遗漏，不能增加。\n"
#                     "输出合同如下：\n"
#                     "{output_contract}"
#                 ),
#             ),
#             (
#                 "user",
#                 (
#                     "原始输入：\n{user_input}\n\n"
#                     "诊断信息：\n{diagnosis}\n\n"
#                     "任务规划：\n{tasks}\n\n"
#                     "上一次校验错误（如有请修正）：\n{errors}"
#                 ),
#             ),
#         ]
#     )

#     chain = prompt | llm
#     log_and_emit(state, "generator", "正在调用模型合成最终反馈...")
    
#     response = chain.invoke(
#         {
#             "output_contract": output_contract,
#             "user_input": user_input,
#             "diagnosis": diagnosis_text,
#             "tasks": tasks_text,
#             "errors": errors,
#         }
#     )
#     raw_text = message_content_to_text(response)
#     parsed_model = parse_pydantic_from_text(raw_text, schema)
#     log_and_emit(state, "generator", "模型返回且解析成功。")

#     final_content = parsed_model.model_dump()
#     return {
#         "generated_content": final_content,
#         "attempt_count": state.get("attempt_count", 0) + 1,
#         "messages": [AIMessage(content=json.dumps(final_content, ensure_ascii=False, indent=2))],
#     }
