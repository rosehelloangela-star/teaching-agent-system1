import time
from typing import Dict, List

from langchain_core.prompts import ChatPromptTemplate

from app.agents.competition_templates import build_competition_context_text, resolve_competition_template
from app.agents.mechanism.llm_config import get_llm
from app.agents.roles import ROLE_CONFIG_REGISTRY
from app.core.json_utils import message_content_to_text
from app.core.stream_logger import log_and_emit
from app.hypergraph.entity_matcher import detect_hyper_nodes
from app.hypergraph.extractor import extract_hyperedges_from_text
from app.hypergraph.hyper_engine import HypergraphEngine
from app.hypergraph.semantic_guard import evaluate_hyperedge_semantics, build_stage_semantic_report, build_blocking_semantic_alerts, build_structural_field_notes
from app.hypergraph.stage_config import PROJECT_STAGE_DEFINITIONS
from app.hypergraph.stage_manager import build_project_stage_flow
from app.kg.entity_matcher import detect_concepts
from app.kg.graph_store import kg_store


def _truncate_text(text: str, max_chars: int = 8000) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...(文档内容已截断)"


def _extract_message_text(message) -> str:
    try:
        content = getattr(message, "content", "")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            chunks = []
            for item in content:
                if isinstance(item, str):
                    chunks.append(item)
                elif isinstance(item, dict) and item.get("text"):
                    chunks.append(str(item.get("text")))
            return "\n".join(chunks).strip()
    except Exception:
        pass
    return ""


def _build_student_history(messages, max_turns: int = 6, max_chars_per_turn: int = 1500, total_max_chars: int = 9000) -> str:
    if not messages or len(messages) <= 1:
        return "无历史对话（首次提交）。"

    student_turns: List[str] = []
    total_chars = 0
    for message in messages[:-1]:
        if getattr(message, "type", "") != "human":
            continue
        content = _extract_message_text(message)
        if not content:
            continue
        if len(content) > max_chars_per_turn:
            content = content[:max_chars_per_turn] + "..."
        student_turns.append(content)

    if not student_turns:
        return "无历史对话（首次提交）。"

    selected_turns: List[str] = []
    for content in reversed(student_turns):
        if total_chars + len(content) > total_max_chars and selected_turns:
            break
        selected_turns.append(content)
        total_chars += len(content)
        if len(selected_turns) >= max_turns:
            break

    selected_turns.reverse()
    history_lines = [f"【学生历史补充{idx + 1}】\n{content}" for idx, content in enumerate(selected_turns)]
    return "\n\n".join(history_lines)


def _collect_hypergraph_nodes(extracted_h_edges: Dict[str, List[str]]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for nodes in (extracted_h_edges or {}).values():
        for raw in nodes or []:
            raw = str(raw).strip()
            if not raw or raw in seen:
                continue
            seen.add(raw)
            ordered.append(raw)
    return ordered


def _build_stage_context_text(stage_flow: Dict[str, object]) -> str:
    if not stage_flow:
        return ""

    current_stage_id = stage_flow.get("current_stage_id")
    stages = stage_flow.get("stages") or {}
    current_stage = stages.get(current_stage_id, {}) if current_stage_id else {}
    progress = current_stage.get("progress_pct", 0)
    threshold = current_stage.get("pass_threshold", 80)
    critical_remaining = current_stage.get("critical_unresolved", [])
    missing_anchor_labels = (current_stage.get("anchor_status") or {}).get("missing_labels", [])
    blockers = (stage_flow.get("current_stage_gate") or {}).get("blocked_reasons", [])
    followups = stage_flow.get("current_followup_questions", [])[:3]
    current_alerts = stage_flow.get("current_stage_alerts", [])[:5]

    lines = [
        "【项目模式三阶段推进状态】（请务必优先围绕当前阶段引导，不要一次性把全部问题说散）",
        f"- 当前阶段：第{stage_flow.get('current_stage_index', 1)}阶段【{stage_flow.get('current_stage_label', '未命名阶段')}】",
        f"- 当前阶段目标：{current_stage.get('goal', '请优先围绕本阶段核心问题做追问。')}",
        f"- 当前阶段进度：{progress}%（进阶条件之一：达到 {threshold}%）",
        f"- 当前阶段教练提示：{current_stage.get('coach_hint', '请严格围绕当前阶段推进。')}",
    ]
    if critical_remaining:
        lines.append(f"- ⚠️ 当前阶段仍有关键高危规则未解：{', '.join(critical_remaining)}")
    if missing_anchor_labels:
        lines.append(f"- ⚠️ 当前阶段结构锚点仍缺失：{', '.join(missing_anchor_labels)}")
    if blockers:
        lines.append("- 当前未进阶的直接原因：")
        for blocker in blockers:
            lines.append(f"  • {blocker.get('label')}：{blocker.get('detail')}")
    if current_alerts:
        for alert in current_alerts:
            lines.append(
                f"- 本轮重点问题 [{alert.get('rule')}] {alert.get('name')}：{alert.get('issue')}"
            )
    if followups:
        lines.append("- 建议优先追问（尽量选 1-2 个最关键的追问，而不是全部平铺）：")
        for item in followups:
            lines.append(
                f"  • [{item.get('rule_id')}/{item.get('strategy_name')}] {item.get('question')}"
            )
    return "\n".join(lines) + "\n"


def _append_stage_summary_to_diagnosis(raw_analysis: str, stage_flow: Dict[str, object]) -> str:
    if not stage_flow:
        return raw_analysis.strip()
    current_stage_id = stage_flow.get("current_stage_id")
    current_stage = (stage_flow.get("stages") or {}).get(current_stage_id, {}) if current_stage_id else {}
    if not current_stage:
        return raw_analysis.strip()
    followups = stage_flow.get("current_followup_questions", [])[:2]
    blockers = (stage_flow.get("current_stage_gate") or {}).get("blocked_reasons", [])[:2]
    followup_text = "；".join(item.get("question", "") for item in followups if item.get("question"))
    blocker_text = "；".join(item.get("label", "") for item in blockers if item.get("label"))
    addon_lines = [
        f"当前阶段：第{stage_flow.get('current_stage_index', 1)}阶段【{stage_flow.get('current_stage_label', '未命名阶段')}】",
        f"阶段门槛：进度 {current_stage.get('progress_pct', 0)}% / 目标 {current_stage.get('pass_threshold', 80)}%，且需关键高危规则控制在允许范围内，并满足结构锚点要求。",
    ]
    if blocker_text:
        addon_lines.append(f"未进阶原因：{blocker_text}")
    if followup_text:
        addon_lines.append(f"推荐追问：{followup_text}")
    return (raw_analysis or "").strip() + "\n" + "\n".join(addon_lines)


def _build_semantic_context_text(semantic_report: Dict[str, object]) -> str:
    if not semantic_report:
        return ""

    summary = semantic_report.get("summary") or {}
    checks = list(semantic_report.get("checks") or [])
    flagged = [
        item for item in checks
        if str(item.get("status") or "") in {"contradictory", "suspicious", "needs_evidence"}
    ][:6]

    if not flagged and not summary:
        return ""

    lines = [
        "【超边语义复核】（仅对当前阶段里“已通过结构判定”的规则继续复核语义是否成立）",
        f"- 共完成 {int(summary.get('total_checks', 0) or 0)} 组关键配对校验；语义存疑 {int(summary.get('risky_count', 0) or 0)} 组，待补证据 {int(summary.get('needs_evidence_count', 0) or 0)} 组。",
    ]
    for item in flagged:
        status = item.get("status") or "unknown"
        severity = item.get("severity") or "medium"
        lines.append(
            f"- 🔎 [{item.get('rule_id', 'System')}/{status}] (严重度:{severity}) {item.get('left_key', '')}={item.get('left_value', '')} × {item.get('right_key', '')}={item.get('right_value', '')}：{item.get('reason', '')}"
        )
        hint = (item.get("evidence_hint") or "").strip()
        if hint:
            lines.append(f"  ↳ 建议补证：{hint}")
    return "\n".join(lines) + "\n"




def _resolve_project_evaluation_stage_def(previous_stage_flow: Dict[str, object]) -> Dict[str, object]:
    pending_next_stage_index = int(previous_stage_flow.get("next_stage_index") or 0)
    if previous_stage_flow.get("overall_status") == "completed":
        evaluation_stage_index = len(PROJECT_STAGE_DEFINITIONS)
    elif pending_next_stage_index:
        evaluation_stage_index = pending_next_stage_index
    else:
        evaluation_stage_index = int(previous_stage_flow.get("current_stage_index") or 1)
    evaluation_stage_index = max(1, min(evaluation_stage_index, len(PROJECT_STAGE_DEFINITIONS)))
    return next((item for item in PROJECT_STAGE_DEFINITIONS if int(item.get("index", 0)) == evaluation_stage_index), PROJECT_STAGE_DEFINITIONS[0])

def _empty_learning_kg_context() -> Dict[str, object]:
    return {
        "hit_nodes": [],
        "expanded_nodes": [],
        "triples": [],
        "case_examples": {},
        "positive_cases": {},
        "negative_cases": {},
        "mistakes": {},
        "missing_prereqs": [],
        "fallback_case_needed": True,
    }


def _normalize_learning_kg_context(kg_context: Dict[str, object] | None) -> Dict[str, object]:
    normalized = _empty_learning_kg_context()
    if not kg_context:
        return normalized

    normalized.update(kg_context)
    for key in ("hit_nodes", "expanded_nodes", "triples", "missing_prereqs"):
        value = normalized.get(key) or []
        normalized[key] = value if isinstance(value, list) else list(value)

    for key in ("case_examples", "positive_cases", "negative_cases", "mistakes"):
        value = normalized.get(key) or {}
        normalized[key] = value if isinstance(value, dict) else {}

    # 🚨 核心修复：如果有图谱案例，强制关闭 fallback 信号
    has_cases = any(normalized["case_examples"].values()) or \
                any(normalized["positive_cases"].values()) or \
                any(normalized["negative_cases"].values())
    
    if has_cases:
        normalized["fallback_case_needed"] = False
    else:
        normalized["fallback_case_needed"] = bool(kg_context.get("fallback_case_needed", True))
        
    return normalized


def critic_node(state: dict) -> dict:
    user_input = (state.get("user_input") or "").strip()
    role_id = state.get("selected_role", "student_tutor")
    role_config = ROLE_CONFIG_REGISTRY.get(role_id, {})
    role_goal = role_config.get("goal", "提供教学分析")
    focus = role_config.get("focus", "结构化诊断")
    current_mode = state.get("current_mode", "learning")

    bound_document_text = (state.get("bound_document_text") or "").strip()
    bound_file_name = (state.get("bound_file_name") or "").strip()
    document_status = (state.get("document_status") or "none").strip().lower()
    has_bound_doc = document_status == "bound" and bool(bound_document_text)

    messages = state.get("messages", [])
    chat_history = _build_student_history(messages)

    if not user_input:
        log_and_emit(state, "critic", "用户输入为空，返回兜底诊断。", level="warning")
        return {
            "critic_diagnosis": {
                "raw_analysis": "主要问题：用户输入为空\n证据缺口：无可分析文本\n最大风险：无法判断\n推进阻碍：请先提交内容",
            },
            "hypergraph_data": {},
            "competition_context": {},
            "stage_flow": {},
            "kg_context": {},
            "llm_unavailable": False,
        }

    document_context = ""
    analysis_source_text = user_input
    if has_bound_doc:
        doc_excerpt = _truncate_text(bound_document_text, max_chars=8000)
        document_context = (
            "【当前会话已绑定商业计划书】（请优先把它视为事实依据）：\n"
            f"- 文件名：{bound_file_name or '未命名文件'}\n"
            f"- 文档内容节选：\n{doc_excerpt}\n"
        )
        log_and_emit(state, "critic", f"检测到会话已绑定文档：{bound_file_name or '未命名文件'}")
        if current_mode in {"project", "competition"}:
            analysis_source_text = (
                f"【学生本轮最新补充说明（最高优先级，代表本轮针对性修复）】\n{user_input}\n\n"
                f"【学生历史补充，代表项目已确认和已尝试修复的内容】\n{chat_history}\n\n"
                f"【当前会话已绑定商业计划书全文依据】\n{_truncate_text(bound_document_text, max_chars=12000)}"
            ).strip()

    engine_context = ""
    hypergraph_state_data = {}
    competition_context = {}
    stage_flow: Dict[str, object] = {}
    kg_context = _empty_learning_kg_context()


    if current_mode == "learning":
        log_and_emit(
            state,
            "critic",
            f"进入知识图谱诊断分支。current_mode={current_mode}",
            meta={"phase": "kg_retrieval_start", "mode": current_mode},
        )
        try:
            all_db_nodes = kg_store.get_all_entity_names()

            log_and_emit(
                state,
                "critic",
                f"Neo4j 图谱节点总数：{len(all_db_nodes)}",
                meta={
                    "phase": "kg_all_nodes_loaded",
                    "node_count": len(all_db_nodes),
                    "sample_nodes": all_db_nodes[:20],
                },
            )

            # learning 模式只基于本轮问题文本
            detected_concepts = detect_concepts(
                user_input,
                all_db_nodes,
                fuzzy_threshold=72,
                debug=True,
            )

            hit_str = ", ".join(detected_concepts) if detected_concepts else "无"

            log_and_emit(
                state,
                "critic",
                f"Learning 实体命中：[{hit_str}]",
                meta={
                    "phase": "kg_detect_concepts",
                    "user_input": user_input,
                    "detected_concepts": detected_concepts,
                    "hit_count": len(detected_concepts),
                },
            )

            if detected_concepts:
                kg_context = _normalize_learning_kg_context(
                    kg_store.get_learning_subgraph(detected_concepts)
                )

                log_and_emit(
                    state,
                    "critic",
                    (
                        f"Learning 图谱返回："
                        f"hit_nodes={kg_context.get('hit_nodes', [])}，"
                        f"triples_count={len(kg_context.get('triples', []))}，"
                        f"missing_prereqs={kg_context.get('missing_prereqs', [])}"
                    ),
                    meta={
                        "phase": "kg_subgraph_result",
                        "hit_nodes": kg_context.get("hit_nodes", []),
                        "triples": kg_context.get("triples", [])[:20],
                        "triples_count": len(kg_context.get("triples", [])),
                        "missing_prereqs": kg_context.get("missing_prereqs", []),
                        "case_examples": kg_context.get("case_examples", {}),
                        "positive_cases": kg_context.get("positive_cases", {}),
                        "negative_cases": kg_context.get("negative_cases", {}),
                        "mistakes": kg_context.get("mistakes", {}),
                    },
                )

                engine_context = kg_store.build_learning_context(kg_context)

                log_and_emit(
                    state,
                    "critic",
                    "知识图谱上下文组装完成。",
                    meta={
                        "phase": "kg_retrieval_done",
                        "subgraph_node_count": len(kg_context.get("hit_nodes", [])),
                        "subgraph_edge_count": len(kg_context.get("triples", [])),
                    },
                )
            else:
                kg_context = _empty_learning_kg_context()
                log_and_emit(
                    state,
                    "critic",
                    "未命中任何图谱实体，本轮不注入图谱上下文。",
                    level="warning",
                    meta={
                        "phase": "kg_no_hit",
                        "user_input": user_input,
                    },
                )
        except Exception as e:
            kg_context = _empty_learning_kg_context()
            log_and_emit(
                state,
                "critic",
                f"访问 Neo4j 图谱失败，已降级处理：{e}",
                level="warning",
                meta={"phase": "kg_exception", "error": str(e)},
            )

    # if current_mode == "learning":
    #     log_and_emit(state, "critic", f"进入知识图谱诊断分支。current_mode={current_mode}")
    #     try:
    #         all_db_nodes = kg_store.get_all_entity_names()
    #         detected_concepts = detect_concepts(user_input, all_db_nodes, fuzzy_threshold=72, debug=True)
    #         missing_prereqs = kg_store.diagnose_missing_prereqs(detected_concepts)
    #         if missing_prereqs or detected_concepts:
    #             engine_context = "【Neo4j 图谱前置诊断客观信息】（请在评估时严格参考）：\n"
    #             if detected_concepts:
    #                 engine_context += f"- 识别到项目已包含实体概念：{', '.join(detected_concepts)}\n"
    #                 log_and_emit(state, "critic", f"知识图谱命中实体：{', '.join(detected_concepts)}")
    #             if missing_prereqs:
    #                 engine_context += f"- ⚠️ 逻辑断层预警，缺失前置核心概念(PREREQ)：{', '.join(missing_prereqs)}\n"
    #                 log_and_emit(state, "critic", f"检测到缺失前置概念：{', '.join(missing_prereqs)}", level="warning")
    #             for concept in detected_concepts:
    #                 mistakes = kg_store.get_common_mistakes(concept)
    #                 if mistakes:
    #                     engine_context += f"- ⚠️ 针对'{concept}'，历史高发错误模式：{', '.join(mistakes)}\n"
    #             log_and_emit(state, "critic", "知识图谱上下文组装完成。")
    #         else:
    #             log_and_emit(state, "critic", "未命中任何图谱实体，本轮不注入图谱上下文。")
    #     except Exception as e:
    #         log_and_emit(state, "critic", f"访问 Neo4j 图谱失败，已降级处理：{e}", level="warning")

    elif current_mode == "project":
        log_and_emit(state, "critic", f"进入超图诊断分支。current_mode={current_mode}")
        try:
            extracted_h_edges = extract_hyperedges_from_text(analysis_source_text)
            fuzzy_hg_nodes = detect_hyper_nodes(analysis_source_text, fuzzy_threshold=72, debug=True)
            extracted_nodes = _collect_hypergraph_nodes(extracted_h_edges)

            hg_engine = HypergraphEngine()
            hg_engine.build_hypergraph(extracted_h_edges or {})
            topology_alerts = hg_engine.run_topology_diagnostics()

            previous_stage_flow = (((state.get("analysis_snapshot") or {}).get("project") or {}).get("stage_flow") or {})
            evaluation_stage_def = _resolve_project_evaluation_stage_def(previous_stage_flow)
            current_stage_rule_ids = list(evaluation_stage_def.get("rule_ids") or [])

            topology_stage_flow = build_project_stage_flow(
                previous_stage_flow=previous_stage_flow,
                extracted_edges=extracted_h_edges,
                alerts=topology_alerts,
                source_text=analysis_source_text,
            )
            topology_current_stage_id = topology_stage_flow.get("current_stage_id")
            topology_current_stage = ((topology_stage_flow.get("stages") or {}).get(topology_current_stage_id) or {}) if topology_current_stage_id else {}
            structurally_passed_rule_ids = list(topology_current_stage.get("resolved_rule_ids") or [])
            structural_active_alerts = list(topology_current_stage.get("active_alerts") or [])
            structural_field_notes = build_structural_field_notes(
                extracted_h_edges or {},
                stage_rule_ids=structurally_passed_rule_ids,
                source_text=analysis_source_text,
            )

            semantic_report_all = evaluate_hyperedge_semantics(
                extracted_h_edges or {},
                source_text=analysis_source_text,
            )
            semantic_report = build_stage_semantic_report(
                semantic_report_all,
                stage_rule_ids=current_stage_rule_ids,
                structurally_passed_rule_ids=structurally_passed_rule_ids,
                fill_missing_for_passed_rules=True,
                source_text=analysis_source_text,
            )
            semantic_blocking_alerts = build_blocking_semantic_alerts(semantic_report)
            alerts = list(topology_alerts) + list(semantic_blocking_alerts)

            stage_flow = build_project_stage_flow(
                previous_stage_flow=previous_stage_flow,
                extracted_edges=extracted_h_edges,
                alerts=alerts,
                source_text=analysis_source_text,
            )

            hypergraph_state_data = {
                "nodes": extracted_nodes,
                "edges": extracted_h_edges or {},
                "alerts": alerts,
                "topology_alerts": topology_alerts,
                "structural_field_notes": structural_field_notes,
                "semantic_blocking_alerts": semantic_blocking_alerts,
                "semantic_report": semantic_report,
                "semantic_report_all": semantic_report_all,
                "semantic_checks": semantic_report.get("checks", []),
                "semantic_summary": semantic_report.get("summary", {}),
                "semantic_stage_rule_ids": current_stage_rule_ids,
                "semantic_stage_label": evaluation_stage_def.get("label"),
                "structural_rule_status": {
                    "resolved_rule_ids": structurally_passed_rule_ids,
                    "active_alerts": structural_active_alerts,
                    "current_stage_id": topology_current_stage_id,
                },
                "stage_focus_alerts": stage_flow.get("current_stage_alerts", []),
                "guardrail_alerts": stage_flow.get("global_guardrail_alerts", []),
                "current_stage_id": stage_flow.get("current_stage_id"),
            }

            stage_context = _build_stage_context_text(stage_flow)
            semantic_context = _build_semantic_context_text(semantic_report)
            if alerts or fuzzy_hg_nodes or semantic_context:
                engine_context = stage_context + "【基于 HyperNetX 的超图逻辑拓扑审查报告】（最高优先级，请严厉指出逻辑断层）：\n"
                if fuzzy_hg_nodes:
                    engine_context += f"- 🔍 模糊识别到的底层标准要素：{', '.join(fuzzy_hg_nodes)}\n"
                for alert in alerts:
                    rule_id = alert.get("rule", "System")
                    rule_name = alert.get("name", "未知系统警告")
                    severity = alert.get("severity", "high")
                    issue = alert.get("issue", "无具体说明")
                    engine_context += f"- ⚠️ [{rule_id} {rule_name}] (严重度:{severity})：{issue}\n"
                if semantic_context:
                    engine_context += semantic_context
                summary = semantic_report.get("summary") or {}
                log_and_emit(
                    state,
                    "critic",
                    (
                        f"成功触发 {len(alerts)} 条超图预警，其中拓扑预警 {len(topology_alerts)} 条、语义阻断预警 {len(semantic_blocking_alerts)} 条；"
                        f"当前阶段结构已达成规则 {len(structurally_passed_rule_ids)} 条；语义存疑 {int(summary.get('risky_count', 0) or 0)} 组、待补证据 {int(summary.get('needs_evidence_count', 0) or 0)} 组。"
                        f"当前阶段：{stage_flow.get('current_stage_label')}。当前阻塞项：{len((stage_flow.get('current_stage_gate') or {}).get('blocked_reasons', []))}"
                    ),
                    level="warning" if alerts else "info",
                )
            else:
                engine_context = stage_context
                log_and_emit(state, "critic", "超图引擎完成分析，但未触发预警。")
        except Exception as e:
            log_and_emit(state, "critic", f"超图引擎分析失败，已降级处理：{e}", level="warning")

    elif current_mode == "competition":
        log_and_emit(state, "critic", f"进入竞赛诊断分支。current_mode={current_mode}")
        competition_context = resolve_competition_template(f"{chat_history}\n{user_input}")
        engine_context = "【竞赛评审上下文】请严格按以下赛事模板进行诊断：\n"
        engine_context += build_competition_context_text(competition_context)
        log_and_emit(
            state,
            "critic",
            f"已识别赛事模板：{competition_context.get('template_name')}，命中依据：{competition_context.get('matched_alias')}",
        )

    else:
        log_and_emit(state, "critic", f"当前模式未命中特定图谱分支。current_mode={current_mode}")

    llm = get_llm(temperature=0.1, max_tokens=420)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "你是极为严苛的创新创业教学诊断专家。\n"
                    f"当前角色目标：{role_goal}\n"
                    f"当前诊断重点：{focus}\n"
                    "请结合【历史对话】、【绑定文档信息】、【系统客观诊断报告】和学生的【本次输入】进行严苛的结构化诊断。\n"
                    "如果底层的图谱/超图/竞赛模板引擎提示了逻辑断层、缺失要素或高权重维度，你必须优先将其作为最大风险或主要问题指出，绝不能顺从学生的错误思路！\n"
                    "如果学生是在修复之前的问题，请检查是否修复到位；如果是新项目，请全面诊断。\n"
                    "请只输出 4 行，且严格使用以下格式：\n"
                    "主要问题：...\n"
                    "证据缺口：...\n"
                    "最大风险：...\n"
                    "推进阻碍：...\n"
                    "要求：\n"
                    "1. 只输出这 4 行，不要标题，不要解释，不要 markdown\n"
                    "2. 每行尽量简洁，直击要害\n"
                    "3. 必须使用中文"
                ),
            ),
            (
                "user",
                "【历史对话记录】：\n{chat_history}\n\n{document_context}\n{engine_context}\n\n【本次输入】：\n{user_input}",
            ),
        ]
    )
    chain = prompt | llm
    log_and_emit(state, "critic", f"正在结合 {current_mode} 模式上下文调用诊断模型...")
    start = time.perf_counter()
    try:
        response = chain.invoke(
            {
                "chat_history": chat_history,
                "document_context": document_context,
                "engine_context": engine_context,
                "user_input": analysis_source_text,
            }
        )
        text = message_content_to_text(response)
        elapsed = time.perf_counter() - start
        if not text.strip():
            raise ValueError("模型返回为空")
        if current_mode == "project" and stage_flow:
            text = _append_stage_summary_to_diagnosis(text.strip(), stage_flow)
        log_and_emit(state, "critic", f"诊断模型返回成功，用时 {elapsed:.2f}s。")
        return {
            "critic_diagnosis": {"raw_analysis": text.strip()},
            "hypergraph_data": hypergraph_state_data,
            "competition_context": competition_context,
            "kg_context": kg_context,
            "stage_flow": stage_flow,
            "llm_unavailable": False,
        }
    except Exception as e:
        elapsed = time.perf_counter() - start
        log_and_emit(state, "critic", f"诊断模型调用失败，用时 {elapsed:.2f}s。错误：{e}", level="error")
        fallback_text = "主要问题：远程模型调用失败\n证据缺口：系统暂无响应\n最大风险：诊断服务暂时不可用\n推进阻碍：请检查网络或稍后重试"
        if current_mode == "project" and stage_flow:
            fallback_text = _append_stage_summary_to_diagnosis(fallback_text, stage_flow)
        return {
            "critic_diagnosis": {"raw_analysis": fallback_text},
            "hypergraph_data": hypergraph_state_data,
            "competition_context": competition_context,
            "stage_flow": stage_flow,
            "llm_unavailable": True,
            "kg_context": kg_context,
        }


# import time
# from typing import Dict, List

# from langchain_core.prompts import ChatPromptTemplate

# from app.agents.competition_templates import build_competition_context_text, resolve_competition_template
# from app.agents.mechanism.llm_config import get_llm
# from app.agents.roles import ROLE_CONFIG_REGISTRY
# from app.core.json_utils import message_content_to_text
# from app.core.stream_logger import log_and_emit
# from app.hypergraph.entity_matcher import detect_hyper_nodes
# from app.hypergraph.extractor import extract_hyperedges_from_text
# from app.hypergraph.hyper_engine import HypergraphEngine
# from app.hypergraph.semantic_guard import evaluate_hyperedge_semantics, build_stage_semantic_report, build_blocking_semantic_alerts, build_structural_field_notes
# from app.hypergraph.stage_config import PROJECT_STAGE_DEFINITIONS
# from app.hypergraph.stage_manager import build_project_stage_flow
# from app.kg.entity_matcher import detect_concepts
# from app.kg.graph_store import kg_store


# def _truncate_text(text: str, max_chars: int = 8000) -> str:
#     text = (text or "").strip()
#     if len(text) <= max_chars:
#         return text
#     return text[:max_chars] + "\n...(文档内容已截断)"


# def _extract_message_text(message) -> str:
#     try:
#         content = getattr(message, "content", "")
#         if isinstance(content, str):
#             return content.strip()
#         if isinstance(content, list):
#             chunks = []
#             for item in content:
#                 if isinstance(item, str):
#                     chunks.append(item)
#                 elif isinstance(item, dict) and item.get("text"):
#                     chunks.append(str(item.get("text")))
#             return "\n".join(chunks).strip()
#     except Exception:
#         pass
#     return ""


# def _build_student_history(messages, max_turns: int = 6, max_chars_per_turn: int = 1500, total_max_chars: int = 9000) -> str:
#     if not messages or len(messages) <= 1:
#         return "无历史对话（首次提交）。"

#     student_turns: List[str] = []
#     total_chars = 0
#     for message in messages[:-1]:
#         if getattr(message, "type", "") != "human":
#             continue
#         content = _extract_message_text(message)
#         if not content:
#             continue
#         if len(content) > max_chars_per_turn:
#             content = content[:max_chars_per_turn] + "..."
#         student_turns.append(content)

#     if not student_turns:
#         return "无历史对话（首次提交）。"

#     selected_turns: List[str] = []
#     for content in reversed(student_turns):
#         if total_chars + len(content) > total_max_chars and selected_turns:
#             break
#         selected_turns.append(content)
#         total_chars += len(content)
#         if len(selected_turns) >= max_turns:
#             break

#     selected_turns.reverse()
#     history_lines = [f"【学生历史补充{idx + 1}】\n{content}" for idx, content in enumerate(selected_turns)]
#     return "\n\n".join(history_lines)


# def _collect_hypergraph_nodes(extracted_h_edges: Dict[str, List[str]]) -> List[str]:
#     seen = set()
#     ordered: List[str] = []
#     for nodes in (extracted_h_edges or {}).values():
#         for raw in nodes or []:
#             raw = str(raw).strip()
#             if not raw or raw in seen:
#                 continue
#             seen.add(raw)
#             ordered.append(raw)
#     return ordered


# def _build_stage_context_text(stage_flow: Dict[str, object]) -> str:
#     if not stage_flow:
#         return ""

#     current_stage_id = stage_flow.get("current_stage_id")
#     stages = stage_flow.get("stages") or {}
#     current_stage = stages.get(current_stage_id, {}) if current_stage_id else {}
#     progress = current_stage.get("progress_pct", 0)
#     threshold = current_stage.get("pass_threshold", 80)
#     critical_remaining = current_stage.get("critical_unresolved", [])
#     missing_anchor_labels = (current_stage.get("anchor_status") or {}).get("missing_labels", [])
#     blockers = (stage_flow.get("current_stage_gate") or {}).get("blocked_reasons", [])
#     followups = stage_flow.get("current_followup_questions", [])[:3]
#     current_alerts = stage_flow.get("current_stage_alerts", [])[:5]

#     lines = [
#         "【项目模式三阶段推进状态】（请务必优先围绕当前阶段引导，不要一次性把全部问题说散）",
#         f"- 当前阶段：第{stage_flow.get('current_stage_index', 1)}阶段【{stage_flow.get('current_stage_label', '未命名阶段')}】",
#         f"- 当前阶段目标：{current_stage.get('goal', '请优先围绕本阶段核心问题做追问。')}",
#         f"- 当前阶段进度：{progress}%（进阶条件之一：达到 {threshold}%）",
#         f"- 当前阶段教练提示：{current_stage.get('coach_hint', '请严格围绕当前阶段推进。')}",
#     ]
#     if critical_remaining:
#         lines.append(f"- ⚠️ 当前阶段仍有关键高危规则未解：{', '.join(critical_remaining)}")
#     if missing_anchor_labels:
#         lines.append(f"- ⚠️ 当前阶段结构锚点仍缺失：{', '.join(missing_anchor_labels)}")
#     if blockers:
#         lines.append("- 当前未进阶的直接原因：")
#         for blocker in blockers:
#             lines.append(f"  • {blocker.get('label')}：{blocker.get('detail')}")
#     if current_alerts:
#         for alert in current_alerts:
#             lines.append(
#                 f"- 本轮重点问题 [{alert.get('rule')}] {alert.get('name')}：{alert.get('issue')}"
#             )
#     if followups:
#         lines.append("- 建议优先追问（尽量选 1-2 个最关键的追问，而不是全部平铺）：")
#         for item in followups:
#             lines.append(
#                 f"  • [{item.get('rule_id')}/{item.get('strategy_name')}] {item.get('question')}"
#             )
#     return "\n".join(lines) + "\n"


# def _append_stage_summary_to_diagnosis(raw_analysis: str, stage_flow: Dict[str, object]) -> str:
#     if not stage_flow:
#         return raw_analysis.strip()
#     current_stage_id = stage_flow.get("current_stage_id")
#     current_stage = (stage_flow.get("stages") or {}).get(current_stage_id, {}) if current_stage_id else {}
#     if not current_stage:
#         return raw_analysis.strip()
#     followups = stage_flow.get("current_followup_questions", [])[:2]
#     blockers = (stage_flow.get("current_stage_gate") or {}).get("blocked_reasons", [])[:2]
#     followup_text = "；".join(item.get("question", "") for item in followups if item.get("question"))
#     blocker_text = "；".join(item.get("label", "") for item in blockers if item.get("label"))
#     addon_lines = [
#         f"当前阶段：第{stage_flow.get('current_stage_index', 1)}阶段【{stage_flow.get('current_stage_label', '未命名阶段')}】",
#         f"阶段门槛：进度 {current_stage.get('progress_pct', 0)}% / 目标 {current_stage.get('pass_threshold', 80)}%，且需关键高危规则控制在允许范围内，并满足结构锚点要求。",
#     ]
#     if blocker_text:
#         addon_lines.append(f"未进阶原因：{blocker_text}")
#     if followup_text:
#         addon_lines.append(f"推荐追问：{followup_text}")
#     return (raw_analysis or "").strip() + "\n" + "\n".join(addon_lines)


# def _build_semantic_context_text(semantic_report: Dict[str, object]) -> str:
#     if not semantic_report:
#         return ""

#     summary = semantic_report.get("summary") or {}
#     checks = list(semantic_report.get("checks") or [])
#     flagged = [
#         item for item in checks
#         if str(item.get("status") or "") in {"contradictory", "suspicious", "needs_evidence"}
#     ][:6]

#     if not flagged and not summary:
#         return ""

#     lines = [
#         "【超边语义复核】（仅对当前阶段里“已通过结构判定”的规则继续复核语义是否成立）",
#         f"- 共完成 {int(summary.get('total_checks', 0) or 0)} 组关键配对校验；语义存疑 {int(summary.get('risky_count', 0) or 0)} 组，待补证据 {int(summary.get('needs_evidence_count', 0) or 0)} 组。",
#     ]
#     for item in flagged:
#         status = item.get("status") or "unknown"
#         severity = item.get("severity") or "medium"
#         lines.append(
#             f"- 🔎 [{item.get('rule_id', 'System')}/{status}] (严重度:{severity}) {item.get('left_key', '')}={item.get('left_value', '')} × {item.get('right_key', '')}={item.get('right_value', '')}：{item.get('reason', '')}"
#         )
#         hint = (item.get("evidence_hint") or "").strip()
#         if hint:
#             lines.append(f"  ↳ 建议补证：{hint}")
#     return "\n".join(lines) + "\n"




# def _resolve_project_evaluation_stage_def(previous_stage_flow: Dict[str, object]) -> Dict[str, object]:
#     pending_next_stage_index = int(previous_stage_flow.get("next_stage_index") or 0)
#     if previous_stage_flow.get("overall_status") == "completed":
#         evaluation_stage_index = len(PROJECT_STAGE_DEFINITIONS)
#     elif pending_next_stage_index:
#         evaluation_stage_index = pending_next_stage_index
#     else:
#         evaluation_stage_index = int(previous_stage_flow.get("current_stage_index") or 1)
#     evaluation_stage_index = max(1, min(evaluation_stage_index, len(PROJECT_STAGE_DEFINITIONS)))
#     return next((item for item in PROJECT_STAGE_DEFINITIONS if int(item.get("index", 0)) == evaluation_stage_index), PROJECT_STAGE_DEFINITIONS[0])

# def critic_node(state: dict) -> dict:
#     user_input = (state.get("user_input") or "").strip()
#     role_id = state.get("selected_role", "student_tutor")
#     role_config = ROLE_CONFIG_REGISTRY.get(role_id, {})
#     role_goal = role_config.get("goal", "提供教学分析")
#     focus = role_config.get("focus", "结构化诊断")
#     current_mode = state.get("current_mode", "learning")

#     bound_document_text = (state.get("bound_document_text") or "").strip()
#     bound_file_name = (state.get("bound_file_name") or "").strip()
#     document_status = (state.get("document_status") or "none").strip().lower()
#     has_bound_doc = document_status == "bound" and bool(bound_document_text)

#     messages = state.get("messages", [])
#     chat_history = _build_student_history(messages)

#     if not user_input:
#         log_and_emit(state, "critic", "用户输入为空，返回兜底诊断。", level="warning")
#         return {
#             "critic_diagnosis": {
#                 "raw_analysis": "主要问题：用户输入为空\n证据缺口：无可分析文本\n最大风险：无法判断\n推进阻碍：请先提交内容",
#             },
#             "hypergraph_data": {},
#             "competition_context": {},
#             "stage_flow": {},
#             "kg_context": {},
#             "llm_unavailable": False,
#         }

#     document_context = ""
#     analysis_source_text = user_input
#     if has_bound_doc:
#         doc_excerpt = _truncate_text(bound_document_text, max_chars=8000)
#         document_context = (
#             "【当前会话已绑定商业计划书】（请优先把它视为事实依据）：\n"
#             f"- 文件名：{bound_file_name or '未命名文件'}\n"
#             f"- 文档内容节选：\n{doc_excerpt}\n"
#         )
#         log_and_emit(state, "critic", f"检测到会话已绑定文档：{bound_file_name or '未命名文件'}")
#         if current_mode in {"project", "competition"}:
#             analysis_source_text = (
#                 f"【学生本轮最新补充说明（最高优先级，代表本轮针对性修复）】\n{user_input}\n\n"
#                 f"【学生历史补充，代表项目已确认和已尝试修复的内容】\n{chat_history}\n\n"
#                 f"【当前会话已绑定商业计划书全文依据】\n{_truncate_text(bound_document_text, max_chars=12000)}"
#             ).strip()

#     engine_context = ""
#     hypergraph_state_data = {}
#     competition_context = {}
#     stage_flow: Dict[str, object] = {}
#     kg_context = {}


#     if current_mode == "learning":
#         log_and_emit(
#             state,
#             "critic",
#             f"进入知识图谱诊断分支。current_mode={current_mode}",
#             meta={"phase": "kg_retrieval_start", "mode": current_mode},
#         )
#         try:
#             all_db_nodes = kg_store.get_all_entity_names()

#             log_and_emit(
#                 state,
#                 "critic",
#                 f"Neo4j 图谱节点总数：{len(all_db_nodes)}",
#                 meta={
#                     "phase": "kg_all_nodes_loaded",
#                     "node_count": len(all_db_nodes),
#                     "sample_nodes": all_db_nodes[:20],
#                 },
#             )

#             # learning 模式只基于本轮问题文本
#             detected_concepts = detect_concepts(
#                 user_input,
#                 all_db_nodes,
#                 fuzzy_threshold=72,
#                 debug=True,
#             )

#             hit_str = ", ".join(detected_concepts) if detected_concepts else "无"

#             log_and_emit(
#                 state,
#                 "critic",
#                 f"Learning 实体命中：[{hit_str}]",
#                 meta={
#                     "phase": "kg_detect_concepts",
#                     "user_input": user_input,
#                     "detected_concepts": detected_concepts,
#                     "hit_count": len(detected_concepts),
#                 },
#             )

#             if detected_concepts:
#                 kg_context = kg_store.get_learning_subgraph(detected_concepts)

#                 log_and_emit(
#                     state,
#                     "critic",
#                     (
#                         f"Learning 图谱返回："
#                         f"hit_nodes={kg_context.get('hit_nodes', [])}，"
#                         f"triples_count={len(kg_context.get('triples', []))}，"
#                         f"missing_prereqs={kg_context.get('missing_prereqs', [])}"
#                     ),
#                     meta={
#                         "phase": "kg_subgraph_result",
#                         "hit_nodes": kg_context.get("hit_nodes", []),
#                         "triples": kg_context.get("triples", [])[:20],
#                         "triples_count": len(kg_context.get("triples", [])),
#                         "missing_prereqs": kg_context.get("missing_prereqs", []),
#                         "positive_cases": kg_context.get("positive_cases", {}),
#                         "negative_cases": kg_context.get("negative_cases", {}),
#                         "mistakes": kg_context.get("mistakes", {}),
#                     },
#                 )

#                 engine_context = kg_store.build_learning_context(kg_context)

#                 log_and_emit(
#                     state,
#                     "critic",
#                     "知识图谱上下文组装完成。",
#                     meta={
#                         "phase": "kg_retrieval_done",
#                         "subgraph_node_count": len(kg_context.get("hit_nodes", [])),
#                         "subgraph_edge_count": len(kg_context.get("triples", [])),
#                     },
#                 )
#             else:
#                 kg_context = {
#                     "hit_nodes": [],
#                     "triples": [],
#                     "positive_cases": {},
#                     "negative_cases": {},
#                     "mistakes": {},
#                     "missing_prereqs": [],
#                     "fallback_case_needed": True,
#                 }
#                 log_and_emit(
#                     state,
#                     "critic",
#                     "未命中任何图谱实体，本轮不注入图谱上下文。",
#                     level="warning",
#                     meta={
#                         "phase": "kg_no_hit",
#                         "user_input": user_input,
#                     },
#                 )
#         except Exception as e:
#             kg_context = {
#                 "hit_nodes": [],
#                 "triples": [],
#                 "positive_cases": {},
#                 "negative_cases": {},
#                 "mistakes": {},
#                 "missing_prereqs": [],
#                 "fallback_case_needed": True,
#             }
#             log_and_emit(
#                 state,
#                 "critic",
#                 f"访问 Neo4j 图谱失败，已降级处理：{e}",
#                 level="warning",
#                 meta={"phase": "kg_exception", "error": str(e)},
#             )


#     elif current_mode == "project":
#         log_and_emit(state, "critic", f"进入超图诊断分支。current_mode={current_mode}")
#         try:
#             extracted_h_edges = extract_hyperedges_from_text(analysis_source_text)
#             fuzzy_hg_nodes = detect_hyper_nodes(analysis_source_text, fuzzy_threshold=72, debug=True)
#             extracted_nodes = _collect_hypergraph_nodes(extracted_h_edges)

#             hg_engine = HypergraphEngine()
#             hg_engine.build_hypergraph(extracted_h_edges or {})
#             topology_alerts = hg_engine.run_topology_diagnostics()

#             previous_stage_flow = (((state.get("analysis_snapshot") or {}).get("project") or {}).get("stage_flow") or {})
#             evaluation_stage_def = _resolve_project_evaluation_stage_def(previous_stage_flow)
#             current_stage_rule_ids = list(evaluation_stage_def.get("rule_ids") or [])

#             topology_stage_flow = build_project_stage_flow(
#                 previous_stage_flow=previous_stage_flow,
#                 extracted_edges=extracted_h_edges,
#                 alerts=topology_alerts,
#                 source_text=analysis_source_text,
#             )
#             topology_current_stage_id = topology_stage_flow.get("current_stage_id")
#             topology_current_stage = ((topology_stage_flow.get("stages") or {}).get(topology_current_stage_id) or {}) if topology_current_stage_id else {}
#             structurally_passed_rule_ids = list(topology_current_stage.get("resolved_rule_ids") or [])
#             structural_active_alerts = list(topology_current_stage.get("active_alerts") or [])
#             structural_field_notes = build_structural_field_notes(
#                 extracted_h_edges or {},
#                 stage_rule_ids=structurally_passed_rule_ids,
#                 source_text=analysis_source_text,
#             )

#             semantic_report_all = evaluate_hyperedge_semantics(
#                 extracted_h_edges or {},
#                 source_text=analysis_source_text,
#             )
#             semantic_report = build_stage_semantic_report(
#                 semantic_report_all,
#                 stage_rule_ids=current_stage_rule_ids,
#                 structurally_passed_rule_ids=structurally_passed_rule_ids,
#                 fill_missing_for_passed_rules=True,
#                 source_text=analysis_source_text,
#             )
#             semantic_blocking_alerts = build_blocking_semantic_alerts(semantic_report)
#             alerts = list(topology_alerts) + list(semantic_blocking_alerts)

#             stage_flow = build_project_stage_flow(
#                 previous_stage_flow=previous_stage_flow,
#                 extracted_edges=extracted_h_edges,
#                 alerts=alerts,
#                 source_text=analysis_source_text,
#             )

#             hypergraph_state_data = {
#                 "nodes": extracted_nodes,
#                 "edges": extracted_h_edges or {},
#                 "alerts": alerts,
#                 "topology_alerts": topology_alerts,
#                 "structural_field_notes": structural_field_notes,
#                 "semantic_blocking_alerts": semantic_blocking_alerts,
#                 "semantic_report": semantic_report,
#                 "semantic_report_all": semantic_report_all,
#                 "semantic_checks": semantic_report.get("checks", []),
#                 "semantic_summary": semantic_report.get("summary", {}),
#                 "semantic_stage_rule_ids": current_stage_rule_ids,
#                 "semantic_stage_label": evaluation_stage_def.get("label"),
#                 "structural_rule_status": {
#                     "resolved_rule_ids": structurally_passed_rule_ids,
#                     "active_alerts": structural_active_alerts,
#                     "current_stage_id": topology_current_stage_id,
#                 },
#                 "stage_focus_alerts": stage_flow.get("current_stage_alerts", []),
#                 "guardrail_alerts": stage_flow.get("global_guardrail_alerts", []),
#                 "current_stage_id": stage_flow.get("current_stage_id"),
#             }

#             stage_context = _build_stage_context_text(stage_flow)
#             semantic_context = _build_semantic_context_text(semantic_report)
#             if alerts or fuzzy_hg_nodes or semantic_context:
#                 engine_context = stage_context + "【基于 HyperNetX 的超图逻辑拓扑审查报告】（最高优先级，请严厉指出逻辑断层）：\n"
#                 if fuzzy_hg_nodes:
#                     engine_context += f"- 🔍 模糊识别到的底层标准要素：{', '.join(fuzzy_hg_nodes)}\n"
#                 for alert in alerts:
#                     rule_id = alert.get("rule", "System")
#                     rule_name = alert.get("name", "未知系统警告")
#                     severity = alert.get("severity", "high")
#                     issue = alert.get("issue", "无具体说明")
#                     engine_context += f"- ⚠️ [{rule_id} {rule_name}] (严重度:{severity})：{issue}\n"
#                 if semantic_context:
#                     engine_context += semantic_context
#                 summary = semantic_report.get("summary") or {}
#                 log_and_emit(
#                     state,
#                     "critic",
#                     (
#                         f"成功触发 {len(alerts)} 条超图预警，其中拓扑预警 {len(topology_alerts)} 条、语义阻断预警 {len(semantic_blocking_alerts)} 条；"
#                         f"当前阶段结构已达成规则 {len(structurally_passed_rule_ids)} 条；语义存疑 {int(summary.get('risky_count', 0) or 0)} 组、待补证据 {int(summary.get('needs_evidence_count', 0) or 0)} 组。"
#                         f"当前阶段：{stage_flow.get('current_stage_label')}。当前阻塞项：{len((stage_flow.get('current_stage_gate') or {}).get('blocked_reasons', []))}"
#                     ),
#                     level="warning" if alerts else "info",
#                 )
#             else:
#                 engine_context = stage_context
#                 log_and_emit(state, "critic", "超图引擎完成分析，但未触发预警。")
#         except Exception as e:
#             log_and_emit(state, "critic", f"超图引擎分析失败，已降级处理：{e}", level="warning")

#     elif current_mode == "competition":
#         log_and_emit(state, "critic", f"进入竞赛诊断分支。current_mode={current_mode}")
#         competition_context = resolve_competition_template(f"{chat_history}\n{user_input}")
#         engine_context = "【竞赛评审上下文】请严格按以下赛事模板进行诊断：\n"
#         engine_context += build_competition_context_text(competition_context)
#         log_and_emit(
#             state,
#             "critic",
#             f"已识别赛事模板：{competition_context.get('template_name')}，命中依据：{competition_context.get('matched_alias')}",
#         )

#     else:
#         log_and_emit(state, "critic", f"当前模式未命中特定图谱分支。current_mode={current_mode}")

#     llm = get_llm(temperature=0.1, max_tokens=420)
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 (
#                     "你是极为严苛的创新创业教学诊断专家。\n"
#                     f"当前角色目标：{role_goal}\n"
#                     f"当前诊断重点：{focus}\n"
#                     "请结合【历史对话】、【绑定文档信息】、【系统客观诊断报告】和学生的【本次输入】进行严苛的结构化诊断。\n"
#                     "如果底层的图谱/超图/竞赛模板引擎提示了逻辑断层、缺失要素或高权重维度，你必须优先将其作为最大风险或主要问题指出，绝不能顺从学生的错误思路！\n"
#                     "如果学生是在修复之前的问题，请检查是否修复到位；如果是新项目，请全面诊断。\n"
#                     "请只输出 4 行，且严格使用以下格式：\n"
#                     "主要问题：...\n"
#                     "证据缺口：...\n"
#                     "最大风险：...\n"
#                     "推进阻碍：...\n"
#                     "要求：\n"
#                     "1. 只输出这 4 行，不要标题，不要解释，不要 markdown\n"
#                     "2. 每行尽量简洁，直击要害\n"
#                     "3. 必须使用中文"
#                 ),
#             ),
#             (
#                 "user",
#                 "【历史对话记录】：\n{chat_history}\n\n{document_context}\n{engine_context}\n\n【本次输入】：\n{user_input}",
#             ),
#         ]
#     )
#     chain = prompt | llm
#     log_and_emit(state, "critic", f"正在结合 {current_mode} 模式上下文调用诊断模型...")
#     start = time.perf_counter()
#     try:
#         response = chain.invoke(
#             {
#                 "chat_history": chat_history,
#                 "document_context": document_context,
#                 "engine_context": engine_context,
#                 "user_input": analysis_source_text,
#             }
#         )
#         text = message_content_to_text(response)
#         elapsed = time.perf_counter() - start
#         if not text.strip():
#             raise ValueError("模型返回为空")
#         if current_mode == "project" and stage_flow:
#             text = _append_stage_summary_to_diagnosis(text.strip(), stage_flow)
#         log_and_emit(state, "critic", f"诊断模型返回成功，用时 {elapsed:.2f}s。")
#         return {
#             "critic_diagnosis": {"raw_analysis": text.strip()},
#             "hypergraph_data": hypergraph_state_data,
#             "competition_context": competition_context,
#             "kg_context": kg_context,
#             "stage_flow": stage_flow,
#             "llm_unavailable": False,
#         }
#     except Exception as e:
#         elapsed = time.perf_counter() - start
#         log_and_emit(state, "critic", f"诊断模型调用失败，用时 {elapsed:.2f}s。错误：{e}", level="error")
#         fallback_text = "主要问题：远程模型调用失败\n证据缺口：系统暂无响应\n最大风险：诊断服务暂时不可用\n推进阻碍：请检查网络或稍后重试"
#         if current_mode == "project" and stage_flow:
#             fallback_text = _append_stage_summary_to_diagnosis(fallback_text, stage_flow)
#         return {
#             "critic_diagnosis": {"raw_analysis": fallback_text},
#             "hypergraph_data": hypergraph_state_data,
#             "competition_context": competition_context,
#             "stage_flow": stage_flow,
#             "llm_unavailable": True,
#             "kg_context": kg_context,
#         }
