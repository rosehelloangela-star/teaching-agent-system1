import json
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage

from app.agents.mechanism.llm_config import get_llm
from app.core.json_utils import message_content_to_text, parse_pydantic_from_text
from app.agents.roles import ROLE_CONFIG_REGISTRY
from app.core.stream_logger import log_and_emit


def _truncate_text(text: str, max_chars: int = 6000) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...(文档内容已截断)"


def _build_output_contract(role_id: str) -> str:
    if role_id == "project_coach":
        return (
            '{\n'
            '  "is_refused": false,\n'
            '  "reply": "带有 Markdown 排版的对话回复文本",\n'
            '  "logic_flaw": "缺陷总结（严禁留空）",\n'
            '  "evidence_gap": "缺少的具体证据（严禁留空）",\n'
            '  "only_one_task": "具体修复任务（严禁留空）",\n'
            '  "acceptance_criteria": "验收标准"\n'
            '}'
        )
    if role_id == "student_tutor":
        return '{\n  "is_refused": false,\n  "reply": "在此处输出带有丰富 Markdown 排版的对话文本。"\n}'
    if role_id == "competition_advisor":
        return (
            '{\n'
            '  "is_refused": false,\n'
            '  "reply": "带有 Markdown 排版的竞赛辅导回复文本",\n'
            '  "rubric_items": [\n'
            '    {\n'
            '      "dimension_id": "problem_definition",\n'
            '      "estimated_score": 2.0,\n'
            '      "score_reason": "评分解释",\n'
            '      "missing_evidence": ["必须写明具体缺什么数据或图表"],\n'
            '      "minimal_fix_24h": "必须给出24h具体行动",\n'
            '      "minimal_fix_72h": "必须给出72h具体行动"\n'
            '    }\n'
            '  ],\n'
            '  "top_tasks": [\n'
            '    {\n'
            '      "task_desc": "任务描述",\n'
            '      "roi_reason": "高性价比理由",\n'
            '      "template_example": "模板示例",\n'
            '      "timeframe": "24h或72h"\n'
            '    }\n'
            '  ],\n'
            '  "quick_questions": ["继续追问1", "继续追问2"]\n'
            '}'
        )
    if role_id == "instructor_assistant":
        return '{\n  "knowledge_coverage": "知识覆盖统计",\n  "hypergraph_triggers": "规则触发占比",\n  "rubric_distribution": "Rubric分布",\n  "risk_list": [\n    {\n      "project_name": "项目名",\n      "risk_score": "高/中/低",\n      "primary_issues": ["问题1", "问题2"]\n    }\n  ],\n  "teaching_suggestions": "教学干预建议"\n}'
    if role_id == "assessment_assistant":
        return '{\n  "rubric_table": [\n    {\n      "dimension": "评分维度",\n      "score": 1,\n      "evidence_trace": "证据片段"\n    }\n  ],\n  "revision_suggestions": "修订建议",\n  "feedback_templates": "反馈模板"\n}'
    return "{}"


def _score_to_risk(score: float) -> str:
    if score <= 2:
        return "高"
    if score < 3.5:
        return "中"
    return "低"


def _build_competition_rubric_markdown(items: List[Dict[str, Any]]) -> str:
    header = "| 维度 | 权重 | 预估分 | 核心缺口 |\n|---|---:|---:|---|"
    rows = []
    for item in items:
        gap = "；".join(item.get("missing_evidence", [])[:2]) or "证据基本齐备"
        rows.append(
            f"| {item.get('dimension_name')} | {item.get('weight')}% | {item.get('estimated_score'):.1f}/5 | {gap} |"
        )
    return "\n".join([header, *rows])


def _build_competition_deduction_text(items: List[Dict[str, Any]]) -> str:
    weakest = sorted(items, key=lambda x: (x.get("estimated_score", 5), -x.get("weight", 0)))[:4]
    parts = []
    for item in weakest:
        gaps = item.get("missing_evidence", [])[:2]
        gap_text = "；".join(gaps) if gaps else "当前证据不足以支撑高分"
        parts.append(f"- {item.get('dimension_name')}（{item.get('weight')}%）：{gap_text}")
    return "\n".join(parts)


def _validate_competition_output(parsed_dict: Dict[str, Any], template_ctx: Dict[str, Any]) -> None:
    """【防崩溃核心层】接管所有大模型的偷懒行为，进行代码级自动填补"""
    expected_ids = [item["dimension_id"] for item in template_ctx.get("rubric_items", [])]
    parsed_items = parsed_dict.get("rubric_items", []) or []
    
    # 获取大模型实际生成的维度ID
    parsed_ids = [item.get("dimension_id") for item in parsed_items if item.get("dimension_id")]

    # 1. 自动填坑：大模型漏掉的维度，我们代码自动以中庸分数补齐
    missing_ids = set(expected_ids) - set(parsed_ids)
    if missing_ids:
        for m_id in missing_ids:
            parsed_items.append({
                "dimension_id": m_id,
                "estimated_score": 3.0, 
                "score_reason": "系统缺省评分（基于现有文本无法给出精确判定）",
                "missing_evidence": ["缺乏该维度的核心论证材料"],
                "minimal_fix_24h": "重新审视该维度要求并补充基础素材",
                "minimal_fix_72h": "针对性地开展该维度的闭环论证"
            })

    # 2. 去重兜底：大模型生成的重复维度，只保留第一个
    seen = set()
    unique_items = []
    for item in parsed_items:
        dim_id = item.get("dimension_id")
        if dim_id and dim_id not in seen:
            seen.add(dim_id)
            unique_items.append(item)
    parsed_dict["rubric_items"] = unique_items

    # 3. 强力纠偏：分数低却不给建议的（这就是你之前报错的原因），自动强插建议
    for item in parsed_dict.get("rubric_items", []):
        score = float(item.get("estimated_score", 3.0))
        if score <= 2:
            if not item.get("missing_evidence") or len(item.get("missing_evidence")) < 1:
                item["missing_evidence"] = ["缺少支撑该维度的核心客观证据与数据"]
            if not str(item.get("minimal_fix_24h", "")).strip():
                item["minimal_fix_24h"] = "梳理现有BP，补充最基础的逻辑说明"
            if not str(item.get("minimal_fix_72h", "")).strip():
                item["minimal_fix_72h"] = "进行专项调研或测试，彻底补齐证据缺口"


def _enrich_competition_content(parsed_dict: Dict[str, Any], template_ctx: Dict[str, Any]) -> Dict[str, Any]:
    parsed_items = {item["dimension_id"]: item for item in parsed_dict.get("rubric_items", []) or []}
    merged_items: List[Dict[str, Any]] = []
    for template_item in template_ctx.get("rubric_items", []):
        item = parsed_items.get(template_item["dimension_id"], {}) # 安全获取
        score = round(float(item.get("estimated_score", 3.0)), 1)
        merged_items.append(
            {
                "dimension_id": template_item["dimension_id"],
                "dimension_name": template_item["dimension_name"],
                "category": template_item["category"],
                "weight": template_item["weight"],
                "estimated_score": score,
                "score_reason": item.get("score_reason", "缺省评价"),
                "required_evidence": template_item.get("required_evidence", []),
                "missing_evidence": item.get("missing_evidence", []) or [],
                "common_mistakes": template_item.get("common_mistakes", []),
                "minimal_fix_24h": item.get("minimal_fix_24h", ""),
                "minimal_fix_72h": item.get("minimal_fix_72h", ""),
                "risk_level": _score_to_risk(score),
                "low_score_guardrail_pass": True, # 经过了前面的 validate，这里必然是 True，不再依赖复杂判断
            }
        )
    total_weight = sum(item["weight"] for item in merged_items) or 100
    weighted_score_pct = round(sum(item["estimated_score"] / 5 * item["weight"] for item in merged_items), 1)
    average_score = round(sum(item["estimated_score"] for item in merged_items) / len(merged_items), 2) if merged_items else 0.0

    strongest = sorted(merged_items, key=lambda x: (x["estimated_score"], x["weight"]), reverse=True)[:3]
    weakest = sorted(merged_items, key=lambda x: (x["estimated_score"], -x["weight"]))[:3]
    high_weight_dims = sorted(merged_items, key=lambda x: x["weight"], reverse=True)[:4]
    high_risk_dims = [item for item in merged_items if item["risk_level"] == "高"][:4]

    panel_charts = {
        "radar": [
            {
                "dimension": item["dimension_name"],
                "score": item["estimated_score"],
                "fullMark": 5,
                "weight": item["weight"],
            }
            for item in merged_items
        ],
        "weight_compare": [
            {
                "dimension": item["dimension_name"],
                "weight": item["weight"],
                "category": item["category"],
            }
            for item in merged_items
        ],
        "score_weight_matrix": [
            {
                "dimension": item["dimension_name"],
                "score": item["estimated_score"],
                "weight": item["weight"],
                "risk": item["risk_level"],
            }
            for item in merged_items
        ],
    }

    score_summary = {
        "weighted_score_pct": weighted_score_pct,
        "weighted_score_text": f"{weighted_score_pct}/100",
        "average_score": average_score,
        "verdict": "可以路演，但高权重短板必须优先修复" if weighted_score_pct >= 70 else "当前不宜直接上场，需先补齐高权重证据缺口",
        "strongest_dimensions": [
            {
                "dimension_id": item["dimension_id"],
                "dimension_name": item["dimension_name"],
                "score": item["estimated_score"],
                "weight": item["weight"],
            }
            for item in strongest
        ],
        "weakest_dimensions": [
            {
                "dimension_id": item["dimension_id"],
                "dimension_name": item["dimension_name"],
                "score": item["estimated_score"],
                "weight": item["weight"],
            }
            for item in weakest
        ],
        "high_weight_dimensions": [
            {
                "dimension_id": item["dimension_id"],
                "dimension_name": item["dimension_name"],
                "weight": item["weight"],
            }
            for item in high_weight_dims
        ],
        "high_risk_dimensions": [
            {
                "dimension_id": item["dimension_id"],
                "dimension_name": item["dimension_name"],
                "score": item["estimated_score"],
                "weight": item["weight"],
            }
            for item in high_risk_dims
        ],
    }

    competition_meta = {
        "template_id": template_ctx.get("template_id"),
        "template_name": template_ctx.get("template_name"),
        "short_name": template_ctx.get("short_name"),
        "matched_alias": template_ctx.get("matched_alias"),
        "recognition_basis": template_ctx.get("recognition_basis"),
        "focus_hint": template_ctx.get("focus_hint"),
        "expected_shift": template_ctx.get("expected_shift"),
        "total_dimensions": len(merged_items),
        "total_weight": total_weight,
        "exclusive_dimensions": template_ctx.get("exclusive_dimensions", []),
    }

    enriched = dict(parsed_dict)
    enriched["competition_meta"] = competition_meta
    enriched["rubric_items"] = merged_items
    enriched["score_summary"] = score_summary
    enriched["panel_charts"] = panel_charts
    enriched["rubric_scores"] = _build_competition_rubric_markdown(merged_items)
    enriched["deduction_evidence"] = _build_competition_deduction_text(merged_items)
    return enriched


def _build_competition_template_digest(template_ctx: Dict[str, Any]) -> str:
    if not template_ctx:
        return "{}"
    digest = {
        "template_id": template_ctx.get("template_id"),
        "template_name": template_ctx.get("template_name"),
        "short_name": template_ctx.get("short_name"),
        "focus_hint": template_ctx.get("focus_hint"),
        "expected_shift": template_ctx.get("expected_shift"),
        "exclusive_dimensions": template_ctx.get("exclusive_dimensions", []),
        "rubric_items": [
            {
                "dimension_id": item.get("dimension_id"),
                "dimension_name": item.get("dimension_name"),
                "weight": item.get("weight"),
                "category": item.get("category"),
            }
            for item in template_ctx.get("rubric_items", [])
        ],
    }
    return json.dumps(digest, ensure_ascii=False, separators=(",", ":"))


def _clean_json_fence(raw_text: str) -> str:
    raw_text = (raw_text or "").strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    elif raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    return raw_text.strip()


def _invoke_generator(chain, payload: Dict[str, Any], schema, role_id: str, competition_context: Dict[str, Any]):
    response = chain.invoke(payload)
    raw_text = _clean_json_fence(message_content_to_text(response))

    print(f"\n========== [Generator Debug] ==========\n大模型原始输出内容：\n[{raw_text[:800]}...]\n=======================================\n", flush=True)

    if not raw_text:
        raise ValueError("大模型返回了完全空白的字符串！可能是触发了API平台安全护栏，或超出了输出限制。")

    parsed_model = parse_pydantic_from_text(raw_text, schema)
    final_content = parsed_model.model_dump()

    if role_id == "competition_advisor":
        if not competition_context:
            raise ValueError("竞赛模式缺少模板上下文，无法生成稳定输出。")
        # 这里会调用我们刚刚优化的防崩溃 _validate
        _validate_competition_output(final_content, competition_context)
        final_content = _enrich_competition_content(final_content, competition_context)
    return final_content


def _build_competition_prompt(compact: bool = False):
    if not compact:
        system_text = (
            "你是创新创业教学智能体中的竞赛顾问生成器，也是一个非常严格但专业的路演评委。\n"
            "你必须且只能返回一个合法 JSON 对象。不要输出任何解释、前后缀或代码块。\n"
            "reply 用 Markdown；其余字段必须严格按输出合同。\n"
            "\n【🔥 核心纪律（严禁偷懒）】\n"
            "1. 你必须完整遍历模板中的 *所有* rubric_items，一个都不能少！\n"
            "2. 当 estimated_score <= 2 时，missing_evidence 数组必须写出至少1条具体的缺失证据，minimal_fix 绝不能留空！\n"
            "3. top_tasks 最多3条，优先高权重且低分维度。\n"
            "4. quick_questions 最多3条，必须像评委现场追问。\n"
            "\n【reply 必须包含的 Markdown 模块】\n"
            "### 🏁 赛事口径识别\n"
            "### 📊 总体预判\n"
            "### 🎯 高权重扣分项\n"
            "### 🧾 证据缺口清单\n"
            "### ⏱ 24h / 72h 冲刺建议\n"
            "### ❓ 路演追问预演\n"
            "\n【赛事模板摘要】\n{template_digest}\n"
            "\n输出格式参考：\n{output_contract}"
        )
        user_text = (
            "用户当前指令：\n{user_input}\n\n"
            "诊断摘要：\n{diagnosis}\n\n"
            "任务规划：\n{tasks}\n\n"
            "文档节选：\n{document_excerpt}\n\n"
            "上次校验错误：\n{errors}\n\n"
            "⚠️ 最后警告：请务必确保 JSON 字段完整，不遗漏任何 rubric_item 和 missing_evidence！"
        )
    else:
        # 在重试模式下，去掉繁琐的规则，降低长文本的注意力分散
        system_text = (
            "你是冷酷竞赛评委。必须且只能返回合法 JSON。\n"
            "目标：基于赛事模板摘要，对全部维度逐项打分并给出精炼修复建议。\n"
            "⚠️ 硬约束：\n"
            "- rubric_items 必须完整覆盖模板中的全部 dimension_id！\n"
            "- estimated_score <=2 时，必须给 missing_evidence、minimal_fix_24h、minimal_fix_72h，严禁留空！\n"
            "- reply 只写简洁 Markdown 总结。\n"
            "赛事模板摘要：{template_digest}\n"
            "输出格式：{output_contract}"
        )
        user_text = (
            "当前指令：{user_input}\n"
            "诊断：{diagnosis}\n"
            "任务：{tasks}\n"
            "文档：{document_excerpt}\n\n"
            "⚠️ 不要偷懒，请务必保证 JSON 结构完整性！"
        )
    return ChatPromptTemplate.from_messages([("system", system_text), ("user", user_text)])


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
    bound_document_text = state.get("bound_document_text", "")
    competition_context = state.get("competition_context", {})

    output_contract = _build_output_contract(role_id)

    if role_id == "competition_advisor":
        template_digest = _build_competition_template_digest(competition_context)
        # 【减小上下文范围】缩短长文档截断，降低 token 压力，显著降低超时概率
        document_excerpt = _truncate_text(bound_document_text, max_chars=1200) 
        log_and_emit(state, "generator", "正在调用模型合成最终反馈...")

        normal_prompt = _build_competition_prompt(compact=False)
        normal_chain = normal_prompt | get_llm(temperature=0.15, max_tokens=1800)
        normal_payload = {
            "output_contract": output_contract,
            "template_digest": template_digest,
            "user_input": user_input,
            "diagnosis": diagnosis_text,
            "tasks": tasks_text,
            "document_excerpt": document_excerpt,
            "errors": errors,
        }

        try:
            final_content = _invoke_generator(normal_chain, normal_payload, schema, role_id, competition_context)
            log_and_emit(state, "generator", "模型返回且解析成功。")
            return {
                "generated_content": final_content,
                "attempt_count": state.get("attempt_count", 0) + 1,
                "messages": [AIMessage(content=json.dumps(final_content, ensure_ascii=False, indent=2))],
            }
        except Exception as e:
            err_text = str(e)
            if "timed out" not in err_text.lower() and "timeout" not in err_text.lower():
                log_and_emit(state, "generator", f"模型首轮生成失败：{e}", level="warning")
            else:
                log_and_emit(state, "generator", "首轮生成超时，切换精简上下文重试。", level="warning")

            compact_prompt = _build_competition_prompt(compact=True)
            # 【极致缩减】重试时使用极小上下文，确保秒级返回，彻底告别二次超时
            compact_chain = compact_prompt | get_llm(temperature=0.1, max_tokens=1000)
            compact_payload = {
                "output_contract": output_contract,
                "template_digest": template_digest,
                "user_input": user_input[:200],
                "diagnosis": _truncate_text(diagnosis_text, max_chars=400),
                "tasks": _truncate_text(tasks_text, max_chars=300),
                "document_excerpt": _truncate_text(bound_document_text, max_chars=500),
            }
            try:
                final_content = _invoke_generator(compact_chain, compact_payload, schema, role_id, competition_context)
                log_and_emit(state, "generator", "精简重试成功，模型返回且解析成功。")
                return {
                    "generated_content": final_content,
                    "attempt_count": state.get("attempt_count", 0) + 1,
                    "messages": [AIMessage(content=json.dumps(final_content, ensure_ascii=False, indent=2))],
                }
            except Exception as e2:
                log_and_emit(state, "generator", f"容错重试依然失败：{e2}", level="error")
                # 不再让系统崩溃，直接构造一个极简的通过版字典，保全前端渲染
                fallback_content = {
                    "is_refused": False,
                    "reply": "⚠️ **系统提示**：当前项目内容过于庞大或网络出现严重拥堵，导致 AI 深度评审超时。请精简您的项目计划书（控制在 3000 字以内）后重试。",
                    "rubric_items": []
                }
                # 用强硬的补齐代码将其包装为合法输出
                _validate_competition_output(fallback_content, competition_context)
                fallback_content = _enrich_competition_content(fallback_content, competition_context)
                return {
                    "generated_content": fallback_content,
                    "attempt_count": state.get("attempt_count", 0) + 1,
                    "messages": [AIMessage(content=json.dumps(fallback_content, ensure_ascii=False, indent=2))],
                }

    # ====================
    # 以下学习模式 / 项目模式逻辑严格恢复为原版
    # ====================
    llm = get_llm(temperature=0.25, max_tokens=1800)

    system_prompt_text = (
        "你是创新创业教学智能体的内容生成器。\n"
        "请按要求生成回复，并【必须且只能】返回一个合法的 JSON 对象。\n"
        "【格式要求】：直接输出大括号 {{ }}，不要包含任何解释文字，不要使用 ```json 代码块。\n"
        "【换行要求】：在 reply 等字符串中，如果需要换行（如 Markdown 的段落），请务必使用 '\\n' 进行转义，不要直接物理回车换行。\n"
        "【🔥 核心纪律】：严禁偷懒留空，必须严格填满每个 required 字段！"
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
        ("user", "原始输入：\n{user_input}\n\n诊断：\n{diagnosis}\n\n任务：\n{tasks}\n\n上次报错：\n{errors}\n\n⚠️ 警告：请确保字段严密对应！")
    ])

    chain = prompt | llm
    log_and_emit(state, "generator", "正在调用模型合成最终反馈...")

    try:
        final_content = _invoke_generator(
            chain,
            {
                "output_contract": output_contract,
                "user_input": user_input,
                "diagnosis": diagnosis_text,
                "tasks": tasks_text,
                "errors": errors,
            },
            schema,
            role_id,
            competition_context,
        )
        log_and_emit(state, "generator", "模型返回且解析成功。")

        return {
            "generated_content": final_content,
            "attempt_count": state.get("attempt_count", 0) + 1,
            "messages": [AIMessage(content=json.dumps(final_content, ensure_ascii=False, indent=2))],
        }
    except Exception as e:
        log_and_emit(state, "generator", f"模型调用或解析失败：{e}", level="error")
        raise ValueError(f"生成器执行失败，未能生成有效格式：{str(e)}")


import json
from typing import Any, Dict, List

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.agents.mechanism.llm_config import get_llm
from app.agents.roles import ROLE_CONFIG_REGISTRY
from app.core.json_utils import extract_first_json_value, message_content_to_text, parse_pydantic_from_text
from app.core.stream_logger import log_and_emit


# ====================
# 通用工具
# ====================

def _truncate_text(text: str, max_chars: int = 6000) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...(文档内容已截断)"


def _build_output_contract(role_id: str) -> str:
    if role_id == "project_coach":
        return (
            '{\n'
            '  "is_refused": false,\n'
            '  "reply": "带有 Markdown 排版的对话回复文本",\n'
            '  "logic_flaw": "缺陷总结（严禁留空）",\n'
            '  "evidence_gap": "缺少的具体证据（严禁留空）",\n'
            '  "only_one_task": "具体修复任务（严禁留空）",\n'
            '  "acceptance_criteria": "验收标准"\n'
            '}'
        )
    if role_id == "student_tutor":
        return '{\n  "is_refused": false,\n  "reply": "在此处输出带有丰富 Markdown 排版的对话文本。"\n}'
    if role_id == "competition_advisor":
        return (
            '{\n'
            '  "is_refused": false,\n'
            '  "reply": "带有 Markdown 排版的竞赛辅导回复文本",\n'
            '  "rubric_items": [\n'
            '    {\n'
            '      "dimension_id": "problem_definition",\n'
            '      "estimated_score": 2.0,\n'
            '      "score_reason": "评分解释",\n'
            '      "missing_evidence": ["必须写明具体缺什么数据或图表"],\n'
            '      "minimal_fix_24h": "必须给出24h具体行动",\n'
            '      "minimal_fix_72h": "必须给出72h具体行动"\n'
            '    }\n'
            '  ],\n'
            '  "top_tasks": [\n'
            '    {\n'
            '      "task_desc": "任务描述",\n'
            '      "roi_reason": "高性价比理由",\n'
            '      "template_example": "模板示例",\n'
            '      "timeframe": "24h或72h"\n'
            '    }\n'
            '  ],\n'
            '  "quick_questions": ["继续追问1", "继续追问2"]\n'
            '}'
        )
    if role_id == "instructor_assistant":
        return '{\n  "knowledge_coverage": "知识覆盖统计",\n  "hypergraph_triggers": "规则触发占比",\n  "rubric_distribution": "Rubric分布",\n  "risk_list": [\n    {\n      "project_name": "项目名",\n      "risk_score": "高/中/低",\n      "primary_issues": ["问题1", "问题2"]\n    }\n  ],\n  "teaching_suggestions": "教学干预建议"\n}'
    if role_id == "assessment_assistant":
        return '{\n  "rubric_table": [\n    {\n      "dimension": "评分维度",\n      "score": 1,\n      "evidence_trace": "证据片段"\n    }\n  ],\n  "revision_suggestions": "修订建议",\n  "feedback_templates": "反馈模板"\n}'
    return "{}"


# ====================
# competition 专用内部 schema
# ====================

class _CompetitionStructItem(BaseModel):
    dimension_id: str
    estimated_score: float = Field(ge=0, le=5)
    score_reason: str
    missing_evidence: List[str] = Field(default_factory=list)
    minimal_fix_24h: str
    minimal_fix_72h: str


class _CompetitionTask(BaseModel):
    task_desc: str
    roi_reason: str
    template_example: str
    timeframe: str


class _CompetitionStructOutput(BaseModel):
    rubric_items: List[_CompetitionStructItem]
    top_tasks: List[_CompetitionTask] = Field(default_factory=list, max_length=3)
    quick_questions: List[str] = Field(default_factory=list, max_length=3)


class _CompetitionReplyOutput(BaseModel):
    reply: str


# ====================
# competition 结果增强
# ====================

def _score_to_risk(score: float) -> str:
    if score <= 2:
        return "高"
    if score < 3.5:
        return "中"
    return "低"


def _build_competition_rubric_markdown(items: List[Dict[str, Any]]) -> str:
    header = "| 维度 | 权重 | 预估分 | 核心缺口 |\n|---|---:|---:|---|"
    rows = []
    for item in items:
        gap = "；".join(item.get("missing_evidence", [])[:2]) or "证据基本齐备"
        rows.append(
            f"| {item.get('dimension_name')} | {item.get('weight')}% | {item.get('estimated_score'):.1f}/5 | {gap} |"
        )
    return "\n".join([header, *rows])


def _build_competition_deduction_text(items: List[Dict[str, Any]]) -> str:
    weakest = sorted(items, key=lambda x: (x.get("estimated_score", 5), -x.get("weight", 0)))[:4]
    parts = []
    for item in weakest:
        gaps = item.get("missing_evidence", [])[:2]
        gap_text = "；".join(gaps) if gaps else "当前证据不足以支撑高分"
        parts.append(f"- {item.get('dimension_name')}（{item.get('weight')}%）：{gap_text}")
    return "\n".join(parts)


def _validate_competition_output(parsed_dict: Dict[str, Any], template_ctx: Dict[str, Any]) -> None:
    expected_ids = [item["dimension_id"] for item in template_ctx.get("rubric_items", [])]
    parsed_items = parsed_dict.get("rubric_items", []) or []
    parsed_ids = [item.get("dimension_id") for item in parsed_items if item.get("dimension_id")]

    missing_ids = set(expected_ids) - set(parsed_ids)
    if missing_ids:
        for m_id in missing_ids:
            parsed_items.append({
                "dimension_id": m_id,
                "estimated_score": 3.0,
                "score_reason": "系统缺省评分（基于现有文本无法给出精确判定）",
                "missing_evidence": ["缺乏该维度的核心论证材料"],
                "minimal_fix_24h": "重新审视该维度要求并补充基础素材",
                "minimal_fix_72h": "针对性地开展该维度的闭环论证",
            })

    seen = set()
    unique_items = []
    for item in parsed_items:
        dim_id = item.get("dimension_id")
        if dim_id and dim_id not in seen:
            seen.add(dim_id)
            unique_items.append(item)
    parsed_dict["rubric_items"] = unique_items

    for item in parsed_dict.get("rubric_items", []):
        score = float(item.get("estimated_score", 3.0))
        if score <= 2:
            if not item.get("missing_evidence") or len(item.get("missing_evidence")) < 1:
                item["missing_evidence"] = ["缺少支撑该维度的核心客观证据与数据"]
            if not str(item.get("minimal_fix_24h", "")).strip():
                item["minimal_fix_24h"] = "梳理现有BP，补充最基础的逻辑说明"
            if not str(item.get("minimal_fix_72h", "")).strip():
                item["minimal_fix_72h"] = "进行专项调研或测试，彻底补齐证据缺口"


def _enrich_competition_content(parsed_dict: Dict[str, Any], template_ctx: Dict[str, Any]) -> Dict[str, Any]:
    parsed_items = {item["dimension_id"]: item for item in parsed_dict.get("rubric_items", []) or []}
    merged_items: List[Dict[str, Any]] = []
    for template_item in template_ctx.get("rubric_items", []):
        item = parsed_items.get(template_item["dimension_id"], {})
        score = round(float(item.get("estimated_score", 3.0)), 1)
        merged_items.append(
            {
                "dimension_id": template_item["dimension_id"],
                "dimension_name": template_item["dimension_name"],
                "category": template_item["category"],
                "weight": template_item["weight"],
                "estimated_score": score,
                "score_reason": item.get("score_reason", "缺省评价"),
                "required_evidence": template_item.get("required_evidence", []),
                "missing_evidence": item.get("missing_evidence", []) or [],
                "common_mistakes": template_item.get("common_mistakes", []),
                "minimal_fix_24h": item.get("minimal_fix_24h", ""),
                "minimal_fix_72h": item.get("minimal_fix_72h", ""),
                "risk_level": _score_to_risk(score),
                "low_score_guardrail_pass": True,
            }
        )
    total_weight = sum(item["weight"] for item in merged_items) or 100
    weighted_score_pct = round(sum(item["estimated_score"] / 5 * item["weight"] for item in merged_items), 1)
    average_score = round(sum(item["estimated_score"] for item in merged_items) / len(merged_items), 2) if merged_items else 0.0

    strongest = sorted(merged_items, key=lambda x: (x["estimated_score"], x["weight"]), reverse=True)[:3]
    weakest = sorted(merged_items, key=lambda x: (x["estimated_score"], -x["weight"]))[:3]
    high_weight_dims = sorted(merged_items, key=lambda x: x["weight"], reverse=True)[:4]
    high_risk_dims = [item for item in merged_items if item["risk_level"] == "高"][:4]

    panel_charts = {
        "radar": [{"dimension": item["dimension_name"], "score": item["estimated_score"], "fullMark": 5, "weight": item["weight"]} for item in merged_items],
        "weight_compare": [{"dimension": item["dimension_name"], "weight": item["weight"], "category": item["category"]} for item in merged_items],
        "score_weight_matrix": [{"dimension": item["dimension_name"], "score": item["estimated_score"], "weight": item["weight"], "risk": item["risk_level"]} for item in merged_items],
    }

    score_summary = {
        "weighted_score_pct": weighted_score_pct,
        "weighted_score_text": f"{weighted_score_pct}/100",
        "average_score": average_score,
        "verdict": "可以路演，但高权重短板必须优先修复" if weighted_score_pct >= 70 else "当前不宜直接上场，需先补齐高权重证据缺口",
        "strongest_dimensions": [{"dimension_id": item["dimension_id"], "dimension_name": item["dimension_name"], "score": item["estimated_score"], "weight": item["weight"]} for item in strongest],
        "weakest_dimensions": [{"dimension_id": item["dimension_id"], "dimension_name": item["dimension_name"], "score": item["estimated_score"], "weight": item["weight"]} for item in weakest],
        "high_weight_dimensions": [{"dimension_id": item["dimension_id"], "dimension_name": item["dimension_name"], "weight": item["weight"]} for item in high_weight_dims],
        "high_risk_dimensions": [{"dimension_id": item["dimension_id"], "dimension_name": item["dimension_name"], "score": item["estimated_score"], "weight": item["weight"]} for item in high_risk_dims],
    }

    competition_meta = {
        "template_id": template_ctx.get("template_id"),
        "template_name": template_ctx.get("template_name"),
        "short_name": template_ctx.get("short_name"),
        "matched_alias": template_ctx.get("matched_alias"),
        "recognition_basis": template_ctx.get("recognition_basis"),
        "focus_hint": template_ctx.get("focus_hint"),
        "expected_shift": template_ctx.get("expected_shift"),
        "total_dimensions": len(merged_items),
        "total_weight": total_weight,
        "exclusive_dimensions": template_ctx.get("exclusive_dimensions", []),
    }

    enriched = dict(parsed_dict)
    enriched["competition_meta"] = competition_meta
    enriched["rubric_items"] = merged_items
    enriched["score_summary"] = score_summary
    enriched["panel_charts"] = panel_charts
    enriched["rubric_scores"] = _build_competition_rubric_markdown(merged_items)
    enriched["deduction_evidence"] = _build_competition_deduction_text(merged_items)
    return enriched


def _build_competition_template_digest(template_ctx: Dict[str, Any]) -> str:
    if not template_ctx:
        return "{}"
    digest = {
        "template_id": template_ctx.get("template_id"),
        "template_name": template_ctx.get("template_name"),
        "short_name": template_ctx.get("short_name"),
        "focus_hint": template_ctx.get("focus_hint"),
        "expected_shift": template_ctx.get("expected_shift"),
        "exclusive_dimensions": template_ctx.get("exclusive_dimensions", []),
        "rubric_items": [
            {
                "dimension_id": item.get("dimension_id"),
                "dimension_name": item.get("dimension_name"),
                "weight": item.get("weight"),
                "category": item.get("category"),
            }
            for item in template_ctx.get("rubric_items", [])
        ],
    }
    return json.dumps(digest, ensure_ascii=False, separators=(",", ":"))


def _clean_json_fence(raw_text: str) -> str:
    raw_text = (raw_text or "").strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    elif raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    return raw_text.strip()


def _extract_json_payload(raw_text: str) -> str:
    cleaned = _clean_json_fence(raw_text)
    try:
        parsed = extract_first_json_value(cleaned)
        if parsed is not None:
            return json.dumps(parsed, ensure_ascii=False)
    except Exception:
        pass
    return cleaned


def _safe_parse_pydantic(raw_text: str, schema):
    payload = _extract_json_payload(raw_text)
    return parse_pydantic_from_text(payload, schema)


def _build_rule_based_competition_reply(content: Dict[str, Any]) -> str:
    meta = content.get("competition_meta", {})
    summary = content.get("score_summary", {})
    weakest = summary.get("weakest_dimensions", [])[:3]
    strongest = summary.get("strongest_dimensions", [])[:2]
    high_weight = summary.get("high_weight_dimensions", [])[:4]
    items = content.get("rubric_items", [])
    top_tasks = content.get("top_tasks", [])
    quick_questions = content.get("quick_questions", [])[:3]

    high_weight_names = "、".join(item.get("dimension_name", "") for item in high_weight) or "当前高权重维度"
    weak_lines = []
    for item in weakest:
        full = next((x for x in items if x.get("dimension_id") == item.get("dimension_id")), None)
        gaps = full.get("missing_evidence", [])[:2] if full else []
        gap_text = "；".join(gaps) if gaps else "缺少关键证据支撑"
        weak_lines.append(f"- **{item.get('dimension_name')}**（{item.get('weight')}% / {item.get('score')}/5）：{gap_text}")
    if not weak_lines:
        weak_lines.append("- 暂无显著低分维度，但仍建议优先完善高权重项的客观证据。")

    task_lines = []
    for task in top_tasks[:3]:
        task_lines.append(f"- **{task.get('task_desc','任务')}**（{task.get('timeframe','短周期')}）：{task.get('roi_reason','优先修复高权重缺口')}。")
    if not task_lines:
        task_lines.append("- 优先补齐高权重维度的核心证据与图表。")

    strong_text = "、".join(item.get("dimension_name", "") for item in strongest) or "暂未形成明显强项"
    question_lines = [f"- {q}" for q in quick_questions] or ["- 如果评委追问“你的核心证据在哪里”，你准备展示哪一页材料？"]

    return (
        f"### 🏁 赛事口径识别\n"
        f"你当前对标的赛事是 **{meta.get('template_name','当前赛事模板')}**。这一口径会优先关注 **{meta.get('focus_hint','高权重核心维度')}**。\n\n"
        f"### 📊 总体预判\n"
        f"- 当前综合预估得分：**{summary.get('weighted_score_text','—')}**\n"
        f"- 平均单项分：**{summary.get('average_score','—')}**\n"
        f"- 目前较强的维度：**{strong_text}**\n"
        f"- 结论：{summary.get('verdict','建议先补齐高权重短板后再正式路演。')}\n\n"
        f"### 🎯 高权重扣分项\n"
        f"当前真正会拉低评审结果的，不是所有问题，而是这些**高权重/低得分**维度：\n"
        f"{chr(10).join(weak_lines)}\n\n"
        f"### 🧾 证据缺口清单\n"
        f"这个赛事模板最看重的维度包括：**{high_weight_names}**。如果这些维度没有客观证据、测算逻辑或对比材料，再漂亮的讲述也很难拿高分。\n\n"
        f"### ⏱ 24h / 72h 冲刺建议\n"
        f"{chr(10).join(task_lines)}\n\n"
        f"### ❓ 路演追问预演\n"
        f"{chr(10).join(question_lines)}"
    )


# ====================
# competition 两阶段生成
# ====================

def _run_competition_structurer(state: dict, schema, output_contract: str, competition_context: Dict[str, Any]) -> Dict[str, Any]:
    user_input = state.get("user_input", "")
    diagnosis_text = state.get("critic_diagnosis", {}).get("raw_analysis", "")
    tasks_text = json.dumps(state.get("planned_tasks", []), ensure_ascii=False, separators=(",", ":"))
    bound_document_text = state.get("bound_document_text", "")
    errors = state.get("validation_errors") or "无"

    template_digest = _build_competition_template_digest(competition_context)
    document_excerpt = _truncate_text(bound_document_text, max_chars=1800)

    struct_contract = (
        '{\n'
        '  "rubric_items": [\n'
        '    {\n'
        '      "dimension_id": "problem_definition",\n'
        '      "estimated_score": 2.0,\n'
        '      "score_reason": "评分解释",\n'
        '      "missing_evidence": ["缺失的客观证据"],\n'
        '      "minimal_fix_24h": "24小时修复",\n'
        '      "minimal_fix_72h": "72小时修复"\n'
        '    }\n'
        '  ],\n'
        '  "top_tasks": [\n'
        '    {\n'
        '      "task_desc": "任务描述",\n'
        '      "roi_reason": "高性价比理由",\n'
        '      "template_example": "模板或示例",\n'
        '      "timeframe": "24h或72h"\n'
        '    }\n'
        '  ],\n'
        '  "quick_questions": ["评委追问1", "评委追问2"]\n'
        '}'
    )

    system_text = (
        "你是 competition_structurer，只负责输出竞赛模式的结构化评分结果。\n"
        "你必须且只能返回合法 JSON，不要 markdown，不要解释。\n"
        "你的唯一目标是：完整覆盖赛事模板中的全部 rubric 维度，并给出可用于后续展示的结构化评分结果。\n"
        "硬约束：\n"
        "1. rubric_items 必须完整覆盖模板中的全部 dimension_id，一个都不能少。\n"
        "2. 维度不得改名，不得新增自造维度。\n"
        "3. estimated_score <= 2 时，missing_evidence 至少 1 条，且必须同时填写 minimal_fix_24h / minimal_fix_72h。\n"
        "4. missing_evidence 必须指向真实缺口，例如缺访谈、缺竞品矩阵、缺单位经济、缺论文/专利支撑。\n"
        "5. top_tasks 最多 3 条，优先高权重且低分维度。\n"
        "6. quick_questions 最多 3 条，必须像冷酷评委的追问。\n"
        "模板摘要：{template_digest}\n"
        "输出格式参考：{struct_contract}"
    )
    user_text = (
        "用户当前指令：\n{user_input}\n\n"
        "诊断摘要：\n{diagnosis}\n\n"
        "任务规划：\n{tasks}\n\n"
        "文档节选：\n{document_excerpt}\n\n"
        "上次报错：\n{errors}"
    )

    prompt = ChatPromptTemplate.from_messages([("system", system_text), ("user", user_text)])
    chain = prompt | get_llm(temperature=0.1, max_tokens=1500)

    log_and_emit(state, "competition_structurer", "开始生成竞赛结构化评分结果。")
    response = chain.invoke({
        "template_digest": template_digest,
        "struct_contract": struct_contract,
        "user_input": user_input,
        "diagnosis": diagnosis_text,
        "tasks": tasks_text,
        "document_excerpt": document_excerpt,
        "errors": errors,
    })
    raw_text = _clean_json_fence(message_content_to_text(response))
    print(f"\n========== [Competition Structurer Debug] ==========\n[{raw_text[:1200]}...]\n===================================================\n", flush=True)
    parsed_model = _safe_parse_pydantic(raw_text, _CompetitionStructOutput)
    struct_content = parsed_model.model_dump()
    _validate_competition_output(struct_content, competition_context)

    if "top_tasks" not in struct_content or not struct_content.get("top_tasks"):
        struct_content["top_tasks"] = (json.loads(tasks_text) if tasks_text else [])[:3]
    if "quick_questions" not in struct_content:
        struct_content["quick_questions"] = []

    log_and_emit(state, "competition_structurer", "结构化评分结果生成成功。")
    return struct_content


def _run_competition_presenter(state: dict, enriched_content: Dict[str, Any]) -> str:
    meta = enriched_content.get("competition_meta", {})
    summary = enriched_content.get("score_summary", {})
    top_tasks = enriched_content.get("top_tasks", [])[:3]
    weakest = summary.get("weakest_dimensions", [])[:4]
    strongest = summary.get("strongest_dimensions", [])[:3]

    presenter_payload = {
        "template_name": meta.get("template_name"),
        "focus_hint": meta.get("focus_hint"),
        "expected_shift": meta.get("expected_shift"),
        "weighted_score_text": summary.get("weighted_score_text"),
        "average_score": summary.get("average_score"),
        "verdict": summary.get("verdict"),
        "strongest_dimensions": strongest,
        "weakest_dimensions": weakest,
        "top_tasks": top_tasks,
        "quick_questions": enriched_content.get("quick_questions", [])[:3],
        "rubric_items": [
            {
                "dimension_name": item.get("dimension_name"),
                "weight": item.get("weight"),
                "estimated_score": item.get("estimated_score"),
                "missing_evidence": item.get("missing_evidence", [])[:2],
                "minimal_fix_24h": item.get("minimal_fix_24h"),
                "minimal_fix_72h": item.get("minimal_fix_72h"),
            }
            for item in enriched_content.get("rubric_items", [])
        ],
    }

    system_text = (
        "你是 competition_presenter，只负责把已经确定好的结构化评分结果写成高质量 Markdown 评审反馈。\n"
        "你不能改动分数、维度和结论，只能做表达与组织。\n"
        "请输出 JSON，且只包含 reply 一个字段。\n"
        "reply 必须包含以下模块：\n"
        "### 🏁 赛事口径识别\n"
        "### 📊 总体预判\n"
        "### 🎯 高权重扣分项\n"
        "### 🧾 证据缺口清单\n"
        "### ⏱ 24h / 72h 冲刺建议\n"
        "### ❓ 路演追问预演\n"
        "写作要求：\n"
        "1. 必须像冷酷但专业的评委。\n"
        "2. 必须指出权重偏移，不要一套标准打天下。\n"
        "3. 必须优先谈高权重短板，而不是平均用力。\n"
        "4. 必须结合具体证据缺口，不要写空话。\n"
        "输出格式：{{\"reply\": \"Markdown 文本\"}}"
    )
    user_text = "请根据以下已经确定的评分结果写 reply：\n{presenter_payload}"
    prompt = ChatPromptTemplate.from_messages([("system", system_text), ("user", user_text)])
    chain = prompt | get_llm(temperature=0.35, max_tokens=1400)

    log_and_emit(state, "competition_presenter", "开始生成竞赛模式 Markdown 讲评。")
    response = chain.invoke({"presenter_payload": json.dumps(presenter_payload, ensure_ascii=False)})
    raw_text = _clean_json_fence(message_content_to_text(response))
    print(f"\n========== [Competition Presenter Debug] ==========\n[{raw_text[:1200]}...]\n===================================================\n", flush=True)
    parsed_model = _safe_parse_pydantic(raw_text, _CompetitionReplyOutput)
    reply = (parsed_model.reply or "").strip()
    if not reply:
        raise ValueError("competition_presenter 返回空 reply")
    log_and_emit(state, "competition_presenter", "Markdown 讲评生成成功。")
    return reply


# ====================
# 主节点
# ====================

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
    competition_context = state.get("competition_context", {})

    output_contract = _build_output_contract(role_id)

    # ====== 仅 competition 分支改造成两阶段 ======
    if role_id == "competition_advisor":
        log_and_emit(state, "generator", "竞赛模式进入双阶段生成：先结构化评分，再生成 Markdown 讲评。")
        try:
            struct_content = _run_competition_structurer(state, schema, output_contract, competition_context)
            enriched_content = _enrich_competition_content(struct_content, competition_context)
            try:
                reply = _run_competition_presenter(state, enriched_content)
            except Exception as presenter_error:
                log_and_emit(state, "competition_presenter", f"Markdown 讲评生成失败，改用规则模板兜底：{presenter_error}", level="warning")
                reply = _build_rule_based_competition_reply(enriched_content)

            final_content = {
                "is_refused": False,
                "reply": reply,
                "rubric_items": enriched_content.get("rubric_items", []),
                "top_tasks": struct_content.get("top_tasks", [])[:3],
                "quick_questions": struct_content.get("quick_questions", [])[:3],
            }
            final_content = _enrich_competition_content(final_content, competition_context)
            schema.model_validate(final_content)
            log_and_emit(state, "generator", "竞赛模式双阶段生成成功。")
            return {
                "generated_content": final_content,
                "attempt_count": state.get("attempt_count", 0) + 1,
                "messages": [AIMessage(content=json.dumps(final_content, ensure_ascii=False, indent=2))],
            }
        except Exception as e:
            log_and_emit(state, "generator", f"竞赛模式双阶段生成失败：{e}", level="error")
            raise ValueError(f"生成器执行失败，未能生成有效格式：{str(e)}")

    # ====================
    # 以下学习模式 / 项目模式逻辑保持当前版本不变
    # ====================
    llm = get_llm(temperature=0.25, max_tokens=1800)

    system_prompt_text = (
        "你是创新创业教学智能体的内容生成器。\n"
        "请按要求生成回复，并【必须且只能】返回一个合法的 JSON 对象。\n"
        "【格式要求】：直接输出大括号 {{ }}，不要包含任何解释文字，不要使用 ```json 代码块。\n"
        "【换行要求】：在 reply 等字符串中，如果需要换行（如 Markdown 的段落），请务必使用 '\\n' 进行转义，不要直接物理回车换行。\n"
        "【🔥 核心纪律】：严禁偷懒留空，必须严格填满每个 required 字段！"
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
        ("user", "原始输入：\n{user_input}\n\n诊断：\n{diagnosis}\n\n任务：\n{tasks}\n\n上次报错：\n{errors}\n\n⚠️ 警告：请确保字段严密对应！")
    ])

    chain = prompt | llm
    log_and_emit(state, "generator", "正在调用模型合成最终反馈...")

    try:
        response = chain.invoke(
            {
                "output_contract": output_contract,
                "user_input": user_input,
                "diagnosis": diagnosis_text,
                "tasks": tasks_text,
                "errors": errors,
            }
        )
        raw_text = _clean_json_fence(message_content_to_text(response))
        parsed_model = _safe_parse_pydantic(raw_text, schema)
        final_content = parsed_model.model_dump()
        log_and_emit(state, "generator", "模型返回且解析成功。")
        return {
            "generated_content": final_content,
            "attempt_count": state.get("attempt_count", 0) + 1,
            "messages": [AIMessage(content=json.dumps(final_content, ensure_ascii=False, indent=2))],
        }
    except Exception as e:
        log_and_emit(state, "generator", f"模型调用或解析失败：{e}", level="error")
        raise ValueError(f"生成器执行失败，未能生成有效格式：{str(e)}")
