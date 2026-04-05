# from __future__ import annotations

# from typing import Any, Dict, List, Set, Tuple

# from app.hypergraph.stage_config import PROJECT_STAGE_DEFINITIONS, RULE_METADATA
# from app.hypergraph.strategy_library import select_project_followup_questions


# SEVERITY_WEIGHT = {
#     "critical": 30,
#     "high": 18,
#     "medium": 10,
#     "low": 6,
# }


# def _extract_standard_keys(extracted_edges: Dict[str, List[str]]) -> Tuple[Set[str], List[str]]:
#     standard_keys: Set[str] = set()
#     flat_nodes: List[str] = []
#     for _, nodes in (extracted_edges or {}).items():
#         for raw in nodes or []:
#             raw = str(raw).strip()
#             if not raw:
#                 continue
#             flat_nodes.append(raw)
#             token = raw
#             if ':' in raw:
#                 token = raw.split(':', 1)[0]
#             elif '：' in raw:
#                 token = raw.split('：', 1)[0]
#             token = token.strip()
#             if token:
#                 standard_keys.add(token)
#     return standard_keys, flat_nodes


# def _build_alert_map(alerts: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
#     return {
#         alert.get("rule"): alert
#         for alert in alerts or []
#         if alert.get("rule")
#     }


# def _rule_weight(rule_id: str, alert_map: Dict[str, Dict[str, Any]]) -> int:
#     if rule_id in alert_map:
#         severity = (alert_map[rule_id].get("severity") or "medium").lower()
#         return SEVERITY_WEIGHT.get(severity, 10)
#     meta = RULE_METADATA.get(rule_id, {})
#     return int(meta.get("weight", 10))


# def _normalize_rule_ids(rule_ids: List[str], reference_order: List[str]) -> List[str]:
#     ref_index = {rule_id: idx for idx, rule_id in enumerate(reference_order)}
#     return sorted(set(rule_ids), key=lambda item: ref_index.get(item, 999))


# def _contains_any(text: str, keywords: List[str]) -> bool:
#     return any(keyword in text for keyword in keywords)


# def _detect_evidence_signals(source_text: str) -> Dict[str, bool]:
#     text = (source_text or "").lower()
#     return {
#         "field_research": _contains_any(text, ["调研", "访谈", "走访", "受访", "问卷", "样本", "案例", "报告", "记录", "引述", "quotes", "interview"]),
#         "pain_evidence": _contains_any(text, ["痛点", "损耗", "损失", "误工", "延误", "来不及", "时效", "故障", "风险", "焦虑", "麻烦"]),
#         "payment_evidence": _contains_any(text, ["支付意愿", "愿意付", "愿付", "价格", "报价", "单价", "元/单", "元/公斤", "多少钱", "付费"]),
#         "cost_evidence": _contains_any(text, ["成本", "油费", "电池", "人力", "设备损耗", "获客成本", "cac", "ltv", "补贴"]),
#         "supply_evidence": _contains_any(text, ["飞手", "合作社", "经销商", "供应链", "配送员", "接单", "报价"]),
#         "pilot_evidence": _contains_any(text, ["试点", "试运行", "模拟订单", "样机", "mvp", "小范围", "首批用户"]),
#     }


# def _infer_text_anchor_hits(stage_id: str, label: str, source_text: str, evidence_signals: Dict[str, bool]) -> List[str]:
#     text = source_text or ""
#     hits: List[str] = []
#     if not text:
#         return hits

#     if stage_id == "stage_1_core":
#         if label == "目标用户" and _contains_any(text, ["用户", "农民", "农户", "种植大户", "合作社", "飞手", "老人", "学生", "商家", "客户"]):
#             hits.append("文本命中:目标用户")
#         elif label == "核心痛点":
#             if _contains_any(text, ["痛点", "损耗", "损失", "时效", "延误", "来不及", "急需", "误工", "成本高", "价格敏感", "当天", "24小时"]) or (
#                 evidence_signals.get("field_research") and (evidence_signals.get("pain_evidence") or evidence_signals.get("payment_evidence"))
#             ):
#                 hits.append("文本命中:核心痛点")
#         elif label == "价值/方案表达" and _contains_any(text, ["价值主张", "方案", "服务", "无人机", "配送", "平台", "24小时送达", "调度", "帮助", "解决"]):
#             hits.append("文本命中:价值方案")

#     elif stage_id == "stage_2_logic":
#         if label == "收入/定价表达" and _contains_any(text, ["定价", "价格", "收费", "抽成", "收入", "盈利", "元/单", "revenue", "price"]):
#             hits.append("文本命中:收入定价")
#         elif label == "单位经济" and _contains_any(text, ["成本", "cac", "ltv", "固定成本", "变动成本", "单客", "单位经济"]):
#             hits.append("文本命中:单位经济")
#         elif label == "生存压力" and _contains_any(text, ["现金流", "burn", "融资", "补贴", "账期", "启动资金", "能活多久", "盈亏平衡"]):
#             hits.append("文本命中:生存压力")

#     elif stage_id == "stage_3_reality":
#         if label == "团队/技术" and _contains_any(text, ["团队", "技术路线", "研发", "飞手", "算法", "工程师", "trl"]):
#             hits.append("文本命中:团队技术")
#         elif label == "资源/里程碑" and _contains_any(text, ["资源", "里程碑", "试点", "合作", "计划", "90天", "mvp"]):
#             hits.append("文本命中:资源里程碑")
#         elif label == "落地/合规" and _contains_any(text, ["合规", "政策", "供应链", "供应商", "履约", "落地", "村委", "合作社", "冷启动"]):
#             hits.append("文本命中:落地合规")

#     return hits


# def _resolve_anchor_status(
#     stage_def: Dict[str, Any],
#     standard_keys: Set[str],
#     *,
#     source_text: str = '',
#     previous_groups: List[Dict[str, Any]] | None = None,
#     evidence_signals: Dict[str, bool] | None = None,
# ) -> Dict[str, Any]:
#     evidence_signals = evidence_signals or {}
#     previous_group_map = {item.get("label"): item for item in (previous_groups or [])}
#     groups = []
#     stage_id = str(stage_def.get("id", ''))

#     for group in stage_def.get("anchor_groups", []):
#         hits = [key for key in group.get("keys", []) if key in standard_keys]
#         hits.extend(_infer_text_anchor_hits(stage_id, str(group.get("label", '')), source_text, evidence_signals))
#         hits = sorted(set(hits))
#         passed = len(hits) >= int(group.get("min_hits", 1))

#         previous_group = previous_group_map.get(group.get("label")) or {}
#         if previous_group.get("passed"):
#             passed = True
#             hits = sorted(set(hits).union(previous_group.get("matched_keys", []) or []))

#         groups.append(
#             {
#                 "label": group.get("label", "未命名锚点"),
#                 "required_keys": group.get("keys", []),
#                 "matched_keys": hits,
#                 "passed": passed,
#             }
#         )

#     passed_group_count = sum(1 for item in groups if item["passed"])
#     min_required_groups = int(stage_def.get("anchor_min_groups", len(groups) if groups else 0))
#     passed = passed_group_count >= min_required_groups if groups else True
#     missing_labels = [item["label"] for item in groups if not item["passed"]]
#     return {
#         "passed": passed,
#         "groups": groups,
#         "missing_labels": missing_labels,
#         "passed_group_count": passed_group_count,
#         "required_group_count": min_required_groups,
#     }


# def _build_stage_blockers(
#     *,
#     progress_pct: int,
#     pass_threshold: int,
#     critical_unresolved: List[str],
#     anchor_status: Dict[str, Any],
#     max_critical_carryover: int = 0,
# ) -> List[Dict[str, Any]]:
#     blockers: List[Dict[str, Any]] = []

#     if progress_pct < pass_threshold:
#         blockers.append(
#             {
#                 "code": "progress_not_enough",
#                 "label": "阶段进度未达标",
#                 "detail": f"当前进度 {progress_pct}% ，仍未达到 {pass_threshold}% 的进阶门槛。",
#             }
#         )

#     if len(critical_unresolved) > max_critical_carryover:
#         blockers.append(
#             {
#                 "code": "critical_rules_remaining",
#                 "label": "关键高危规则仍过多",
#                 "detail": f"当前仍有 {len(critical_unresolved)} 条关键高危规则：{', '.join(critical_unresolved)}；本阶段最多允许保留 {max_critical_carryover} 条进入下一轮。",
#                 "rule_ids": list(critical_unresolved),
#                 "allowed_carryover": max_critical_carryover,
#             }
#         )

#     missing_labels = list((anchor_status or {}).get("missing_labels", []))
#     if not (anchor_status or {}).get("passed", True):
#         blockers.append(
#             {
#                 "code": "anchor_not_ready",
#                 "label": "结构锚点覆盖不足",
#                 "detail": f"当前已满足 {(anchor_status or {}).get('passed_group_count', 0)}/{(anchor_status or {}).get('required_group_count', 0)} 组锚点要求；仍可继续补强：{', '.join(missing_labels) if missing_labels else '暂无'}。",
#                 "missing_labels": missing_labels,
#                 "passed_group_count": (anchor_status or {}).get('passed_group_count', 0),
#                 "required_group_count": (anchor_status or {}).get('required_group_count', 0),
#             }
#         )

#     return blockers


# def _stage_progress_bonus(stage_id: str, evidence_signals: Dict[str, bool]) -> int:
#     if stage_id == "stage_1_core":
#         bonus = 0
#         if evidence_signals.get("field_research"):
#             bonus += 4
#         if evidence_signals.get("pain_evidence"):
#             bonus += 3
#         if evidence_signals.get("payment_evidence") or evidence_signals.get("cost_evidence"):
#             bonus += 3
#         return min(bonus, 10)
#     if stage_id == "stage_2_logic":
#         bonus = 0
#         if evidence_signals.get("payment_evidence"):
#             bonus += 4
#         if evidence_signals.get("cost_evidence"):
#             bonus += 4
#         if evidence_signals.get("pilot_evidence"):
#             bonus += 2
#         return min(bonus, 8)
#     if stage_id == "stage_3_reality":
#         bonus = 0
#         if evidence_signals.get("supply_evidence"):
#             bonus += 4
#         if evidence_signals.get("pilot_evidence"):
#             bonus += 3
#         if evidence_signals.get("field_research"):
#             bonus += 1
#         return min(bonus, 8)
#     return 0


# def build_project_stage_flow(
#     *,
#     previous_stage_flow: Dict[str, Any] | None,
#     extracted_edges: Dict[str, List[str]] | None,
#     alerts: List[Dict[str, Any]] | None,
#     source_text: str = '',
# ) -> Dict[str, Any]:
#     previous_stage_flow = previous_stage_flow or {}
#     extracted_edges = extracted_edges or {}
#     alerts = alerts or []

#     alert_map = _build_alert_map(alerts)
#     current_standard_keys, flat_nodes = _extract_standard_keys(extracted_edges)
#     evidence_signals = _detect_evidence_signals(source_text)

#     previous_confirmed_standard_keys = set(previous_stage_flow.get("confirmed_standard_keys", []) or previous_stage_flow.get("all_standard_keys", []) or [])
#     confirmed_standard_keys = set(previous_confirmed_standard_keys).union(current_standard_keys)

#     previous_stage_id = previous_stage_flow.get("current_stage_id") or PROJECT_STAGE_DEFINITIONS[0]["id"]
#     previous_stage_index = 1
#     for stage in PROJECT_STAGE_DEFINITIONS:
#         if stage["id"] == previous_stage_id:
#             previous_stage_index = int(stage["index"])
#             break

#     previous_stages = previous_stage_flow.get("stages") or {}

#     stage_results: List[Dict[str, Any]] = []
#     computed_unpassed_stage_index = None

#     for stage in PROJECT_STAGE_DEFINITIONS:
#         stage_id = stage["id"]
#         previous_stage = previous_stages.get(stage_id) or {}
#         previously_passed = previous_stage.get("status") == "passed"

#         rule_ids = list(stage.get("rule_ids", []))
#         active_alerts_raw = [alert_map[rule_id] for rule_id in rule_ids if rule_id in alert_map]
#         previous_resolved_rule_ids = set(previous_stage.get("resolved_rule_ids", []) or [])
#         previous_reopened_rule_counts = previous_stage.get("reopened_rule_counts") or {}

#         unresolved_rule_ids: List[str] = []
#         active_alerts: List[Dict[str, Any]] = []
#         sticky_reopened_alerts: List[Dict[str, Any]] = []
#         reopened_rule_counts: Dict[str, int] = {}

#         for alert in active_alerts_raw:
#             rule_id = alert.get("rule")
#             if not rule_id:
#                 continue

#             if rule_id in previous_resolved_rule_ids:
#                 reopen_count = int(previous_reopened_rule_counts.get(rule_id, 0)) + 1
#                 reopened_rule_counts[rule_id] = reopen_count
#                 # 放宽：高质量项目在后续补充中经常会带出新问题，不应因为一次回摆就重新卡死。
#                 if reopen_count >= 3:
#                     unresolved_rule_ids.append(rule_id)
#                     active_alerts.append(alert)
#                 else:
#                     sticky_reopened_alerts.append(alert)
#             else:
#                 unresolved_rule_ids.append(rule_id)
#                 active_alerts.append(alert)

#         unresolved_rule_ids = _normalize_rule_ids(unresolved_rule_ids, rule_ids)
#         resolved_rule_ids = _normalize_rule_ids(
#             [rule_id for rule_id in rule_ids if rule_id not in unresolved_rule_ids] + list(previous_resolved_rule_ids),
#             rule_ids,
#         )

#         critical_unresolved = [
#             alert.get("rule") for alert in active_alerts if (alert.get("severity") or '').lower() == 'critical'
#         ]
#         critical_unresolved = _normalize_rule_ids([item for item in critical_unresolved if item], rule_ids)

#         total_weight = sum(_rule_weight(rule_id, alert_map) for rule_id in rule_ids) or 1
#         unresolved_weight = sum(_rule_weight(rule_id, alert_map) for rule_id in unresolved_rule_ids)
#         resolved_weight = max(total_weight - unresolved_weight, 0)
#         progress_pct = int(round((resolved_weight / total_weight) * 100))
#         progress_pct += _stage_progress_bonus(stage_id, evidence_signals)
#         progress_pct = min(progress_pct, 100)
#         progress_pct = max(progress_pct, int(previous_stage.get("progress_pct", 0) or 0))

#         anchor_status = _resolve_anchor_status(
#             stage,
#             confirmed_standard_keys,
#             source_text=source_text,
#             previous_groups=(previous_stage.get("anchor_status", {}) or {}).get("groups", []),
#             evidence_signals=evidence_signals,
#         )

#         blockers = _build_stage_blockers(
#             progress_pct=progress_pct,
#             pass_threshold=int(stage.get("pass_threshold", 80)),
#             critical_unresolved=critical_unresolved,
#             anchor_status=anchor_status,
#             max_critical_carryover=int(stage.get("max_critical_carryover", 0)),
#         )

#         passed = previously_passed or not blockers
#         if computed_unpassed_stage_index is None and not passed:
#             computed_unpassed_stage_index = int(stage["index"])

#         followup_questions = select_project_followup_questions(active_alerts, source_text=source_text, max_questions=3)
#         stage_results.append(
#             {
#                 "id": stage_id,
#                 "index": stage["index"],
#                 "label": stage["label"],
#                 "short_label": stage.get("short_label", stage["label"]),
#                 "subtitle": stage.get("subtitle", ''),
#                 "goal": stage.get("goal", ''),
#                 "coach_hint": stage.get("coach_hint", ''),
#                 "status": "passed" if passed else "locked",
#                 "progress_pct": progress_pct,
#                 "pass_threshold": stage.get("pass_threshold", 80),
#                 "rule_ids": rule_ids,
#                 "active_rule_ids": unresolved_rule_ids,
#                 "resolved_rule_ids": resolved_rule_ids,
#                 "critical_unresolved": critical_unresolved,
#                 "active_alerts": active_alerts,
#                 "sticky_reopened_alerts": sticky_reopened_alerts,
#                 "sticky_reopened_rule_ids": _normalize_rule_ids(
#                     [alert.get("rule") for alert in sticky_reopened_alerts if alert.get("rule")],
#                     rule_ids,
#                 ),
#                 "reopened_rule_counts": reopened_rule_counts,
#                 "followup_questions": followup_questions,
#                 "score_breakdown": {
#                     "total_weight": total_weight,
#                     "resolved_weight": resolved_weight,
#                     "unresolved_weight": unresolved_weight,
#                     "evidence_bonus": _stage_progress_bonus(stage_id, evidence_signals),
#                 },
#                 "anchor_status": anchor_status,
#                 "can_advance": not blockers,
#                 "blocked_reasons": blockers,
#                 "advance_rule_text": f"进度≥{int(stage.get('pass_threshold', 80))}% + 关键高危规则控制在允许范围内 + 结构锚点达到要求",
#                 "memory_applied": bool(previous_stage),
#             }
#         )

#     if computed_unpassed_stage_index is None:
#         computed_unpassed_stage_index = len(PROJECT_STAGE_DEFINITIONS)

#     current_stage_index = max(previous_stage_index, computed_unpassed_stage_index)
#     current_stage_index = min(current_stage_index, len(PROJECT_STAGE_DEFINITIONS))

#     just_upgraded = current_stage_index > previous_stage_index
#     all_passed = all(stage["status"] == "passed" for stage in stage_results)
#     if all_passed:
#         overall_status = "completed"
#         current_stage_index = len(PROJECT_STAGE_DEFINITIONS)
#     else:
#         overall_status = "in_progress"

#     normalized_stage_results: Dict[str, Dict[str, Any]] = {}
#     current_stage = None
#     for stage in stage_results:
#         stage_index = int(stage["index"])
#         if stage_index < current_stage_index:
#             stage["status"] = "passed"
#         elif stage_index == current_stage_index:
#             stage["status"] = "current" if overall_status != 'completed' else 'passed'
#             current_stage = stage
#         else:
#             stage["status"] = "locked"
#         normalized_stage_results[stage["id"]] = stage

#     if current_stage is None:
#         current_stage = stage_results[-1]

#     stage_def = next(stage for stage in PROJECT_STAGE_DEFINITIONS if int(stage["index"]) == current_stage_index)
#     milestone_message = stage_def.get("milestone_message", '') if just_upgraded else ''
#     current_stage_alerts = list(current_stage.get("active_alerts", []))
#     current_followup_questions = list(current_stage.get("followup_questions", []))
#     guardrail_rule_ids = list(stage_def.get("guardrail_rule_ids", []))
#     guardrail_alerts = [alert_map[rule_id] for rule_id in guardrail_rule_ids if rule_id in alert_map]

#     blockers = list(current_stage.get("blocked_reasons", []))
#     stage_progress_summary = {
#         "resolved_rules": len(current_stage.get("resolved_rule_ids", [])),
#         "total_rules": len(current_stage.get("rule_ids", [])),
#         "critical_remaining": len(current_stage.get("critical_unresolved", [])),
#         "sticky_watchlist": len(current_stage.get("sticky_reopened_rule_ids", [])),
#         "blocked_reason_count": len(blockers),
#         "can_advance": not blockers,
#     }

#     return {
#         "current_stage_id": current_stage["id"],
#         "current_stage_label": current_stage["label"],
#         "current_stage_index": current_stage["index"],
#         "overall_status": overall_status,
#         "just_upgraded": just_upgraded,
#         "milestone_message": milestone_message,
#         "current_stage_entry_message": stage_def.get("entry_message", ''),
#         "global_guardrail_rule_ids": guardrail_rule_ids,
#         "current_stage_alerts": current_stage_alerts,
#         "current_followup_questions": current_followup_questions,
#         "global_guardrail_alerts": guardrail_alerts,
#         "stage_progress_summary": stage_progress_summary,
#         "current_stage_gate": {
#             "ready": not blockers,
#             "advance_rule_text": current_stage.get("advance_rule_text", ''),
#             "blocked_reasons": blockers,
#             "max_critical_carryover": int(stage_def.get("max_critical_carryover", 0)),
#         },
#         "all_triggered_rule_ids": [alert.get("rule") for alert in alerts if alert.get("rule")],
#         "all_standard_keys": sorted(current_standard_keys),
#         "confirmed_standard_keys": sorted(confirmed_standard_keys),
#         "evidence_signals": evidence_signals,
#         "all_extracted_nodes": flat_nodes,
#         "stages": normalized_stage_results,
#     }



from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

from app.hypergraph.stage_config import PROJECT_STAGE_DEFINITIONS, RULE_METADATA
from app.hypergraph.strategy_library import select_project_followup_questions


SEVERITY_WEIGHT = {
    "critical": 30,
    "high": 18,
    "medium": 10,
    "low": 6,
}


def _extract_standard_keys(extracted_edges: Dict[str, List[str]]) -> Tuple[Set[str], List[str]]:
    standard_keys: Set[str] = set()
    flat_nodes: List[str] = []
    for _, nodes in (extracted_edges or {}).items():
        for raw in nodes or []:
            raw = str(raw).strip()
            if not raw:
                continue
            flat_nodes.append(raw)
            token = raw
            if ':' in raw:
                token = raw.split(':', 1)[0]
            elif '：' in raw:
                token = raw.split('：', 1)[0]
            token = token.strip()
            if token:
                standard_keys.add(token)
    return standard_keys, flat_nodes


def _build_alert_map(alerts: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {
        alert.get("rule"): alert
        for alert in alerts or []
        if alert.get("rule")
    }


def _rule_weight(rule_id: str, alert_map: Dict[str, Dict[str, Any]]) -> int:
    if rule_id in alert_map:
        severity = (alert_map[rule_id].get("severity") or "medium").lower()
        return SEVERITY_WEIGHT.get(severity, 10)
    meta = RULE_METADATA.get(rule_id, {})
    return int(meta.get("weight", 10))


def _normalize_rule_ids(rule_ids: List[str], reference_order: List[str]) -> List[str]:
    ref_index = {rule_id: idx for idx, rule_id in enumerate(reference_order)}
    return sorted(set(rule_ids), key=lambda item: ref_index.get(item, 999))


def _contains_any(text: str, keywords: List[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _detect_evidence_signals(source_text: str) -> Dict[str, bool]:
    text = (source_text or "").lower()
    return {
        "field_research": _contains_any(text, ["调研", "访谈", "走访", "受访", "问卷", "样本", "案例", "报告", "记录", "引述", "quotes", "interview"]),
        "pain_evidence": _contains_any(text, ["痛点", "损耗", "损失", "误工", "延误", "来不及", "时效", "故障", "风险", "焦虑", "麻烦"]),
        "payment_evidence": _contains_any(text, ["支付意愿", "愿意付", "愿付", "价格", "报价", "单价", "元/单", "元/公斤", "多少钱", "付费"]),
        "cost_evidence": _contains_any(text, ["成本", "油费", "电池", "人力", "设备损耗", "获客成本", "cac", "ltv", "补贴"]),
        "supply_evidence": _contains_any(text, ["飞手", "合作社", "经销商", "供应链", "配送员", "接单", "报价"]),
        "pilot_evidence": _contains_any(text, ["试点", "试运行", "模拟订单", "样机", "mvp", "小范围", "首批用户"]),
    }


def _infer_text_anchor_hits(stage_id: str, label: str, source_text: str, evidence_signals: Dict[str, bool]) -> List[str]:
    text = source_text or ""
    hits: List[str] = []
    if not text:
        return hits

    if stage_id == "stage_1_core":
        if label == "目标用户" and _contains_any(text, ["用户", "农民", "农户", "种植大户", "合作社", "飞手", "老人", "学生", "商家", "客户"]):
            hits.append("文本命中:目标用户")
        elif label == "核心痛点":
            if _contains_any(text, ["痛点", "损耗", "损失", "时效", "延误", "来不及", "急需", "误工", "成本高", "价格敏感", "当天", "24小时"]) or (
                evidence_signals.get("field_research") and (evidence_signals.get("pain_evidence") or evidence_signals.get("payment_evidence"))
            ):
                hits.append("文本命中:核心痛点")
        elif label == "价值/方案表达" and _contains_any(text, ["价值主张", "方案", "服务", "无人机", "配送", "平台", "24小时送达", "调度", "帮助", "解决"]):
            hits.append("文本命中:价值方案")

    elif stage_id == "stage_2_logic":
        if label == "收入/定价表达" and _contains_any(text, ["定价", "价格", "收费", "抽成", "收入", "盈利", "元/单", "revenue", "price"]):
            hits.append("文本命中:收入定价")
        elif label == "单位经济" and _contains_any(text, ["成本", "cac", "ltv", "固定成本", "变动成本", "单客", "单位经济"]):
            hits.append("文本命中:单位经济")
        elif label == "生存压力" and _contains_any(text, ["现金流", "burn", "融资", "补贴", "账期", "启动资金", "能活多久", "盈亏平衡"]):
            hits.append("文本命中:生存压力")

    elif stage_id == "stage_3_reality":
        if label == "团队/技术" and _contains_any(text, ["团队", "技术路线", "研发", "飞手", "算法", "工程师", "trl"]):
            hits.append("文本命中:团队技术")
        elif label == "资源/里程碑" and _contains_any(text, ["资源", "里程碑", "试点", "合作", "计划", "90天", "mvp"]):
            hits.append("文本命中:资源里程碑")
        elif label == "落地/合规" and _contains_any(text, ["合规", "政策", "供应链", "供应商", "履约", "落地", "村委", "合作社", "冷启动"]):
            hits.append("文本命中:落地合规")

    return hits


def _resolve_anchor_status(
    stage_def: Dict[str, Any],
    standard_keys: Set[str],
    *,
    source_text: str = '',
    previous_groups: List[Dict[str, Any]] | None = None,
    evidence_signals: Dict[str, bool] | None = None,
) -> Dict[str, Any]:
    evidence_signals = evidence_signals or {}
    previous_group_map = {item.get("label"): item for item in (previous_groups or [])}
    groups = []
    stage_id = str(stage_def.get("id", ''))

    for group in stage_def.get("anchor_groups", []):
        hits = [key for key in group.get("keys", []) if key in standard_keys]
        hits.extend(_infer_text_anchor_hits(stage_id, str(group.get("label", '')), source_text, evidence_signals))
        hits = sorted(set(hits))
        passed = len(hits) >= int(group.get("min_hits", 1))

        previous_group = previous_group_map.get(group.get("label")) or {}
        if previous_group.get("passed"):
            passed = True
            hits = sorted(set(hits).union(previous_group.get("matched_keys", []) or []))

        groups.append(
            {
                "label": group.get("label", "未命名锚点"),
                "required_keys": group.get("keys", []),
                "matched_keys": hits,
                "passed": passed,
            }
        )

    passed_group_count = sum(1 for item in groups if item["passed"])
    min_required_groups = int(stage_def.get("anchor_min_groups", len(groups) if groups else 0))
    passed = passed_group_count >= min_required_groups if groups else True
    missing_labels = [item["label"] for item in groups if not item["passed"]]
    return {
        "passed": passed,
        "groups": groups,
        "missing_labels": missing_labels,
        "passed_group_count": passed_group_count,
        "required_group_count": min_required_groups,
    }


def _build_stage_blockers(
    *,
    progress_pct: int,
    pass_threshold: int,
    critical_unresolved: List[str],
    anchor_status: Dict[str, Any],
    max_critical_carryover: int = 0,
) -> List[Dict[str, Any]]:
    blockers: List[Dict[str, Any]] = []

    if progress_pct < pass_threshold:
        blockers.append(
            {
                "code": "progress_not_enough",
                "label": "阶段进度未达标",
                "detail": f"当前进度 {progress_pct}% ，仍未达到 {pass_threshold}% 的进阶门槛。",
            }
        )

    if len(critical_unresolved) > max_critical_carryover:
        blockers.append(
            {
                "code": "critical_rules_remaining",
                "label": "关键高危规则仍过多",
                "detail": f"当前仍有 {len(critical_unresolved)} 条关键高危规则：{', '.join(critical_unresolved)}；本阶段最多允许保留 {max_critical_carryover} 条进入下一轮。",
                "rule_ids": list(critical_unresolved),
                "allowed_carryover": max_critical_carryover,
            }
        )

    missing_labels = list((anchor_status or {}).get("missing_labels", []))
    if not (anchor_status or {}).get("passed", True):
        blockers.append(
            {
                "code": "anchor_not_ready",
                "label": "结构锚点覆盖不足",
                "detail": f"当前已满足 {(anchor_status or {}).get('passed_group_count', 0)}/{(anchor_status or {}).get('required_group_count', 0)} 组锚点要求；仍可继续补强：{', '.join(missing_labels) if missing_labels else '暂无'}。",
                "missing_labels": missing_labels,
                "passed_group_count": (anchor_status or {}).get('passed_group_count', 0),
                "required_group_count": (anchor_status or {}).get('required_group_count', 0),
            }
        )

    return blockers


def _stage_progress_bonus(stage_id: str, evidence_signals: Dict[str, bool]) -> int:
    if stage_id == "stage_1_core":
        bonus = 0
        if evidence_signals.get("field_research"):
            bonus += 4
        if evidence_signals.get("pain_evidence"):
            bonus += 3
        if evidence_signals.get("payment_evidence") or evidence_signals.get("cost_evidence"):
            bonus += 3
        return min(bonus, 10)
    if stage_id == "stage_2_logic":
        bonus = 0
        if evidence_signals.get("payment_evidence"):
            bonus += 4
        if evidence_signals.get("cost_evidence"):
            bonus += 4
        if evidence_signals.get("pilot_evidence"):
            bonus += 2
        return min(bonus, 8)
    if stage_id == "stage_3_reality":
        bonus = 0
        if evidence_signals.get("supply_evidence"):
            bonus += 4
        if evidence_signals.get("pilot_evidence"):
            bonus += 3
        if evidence_signals.get("field_research"):
            bonus += 1
        return min(bonus, 8)
    return 0


def build_project_stage_flow(
    *,
    previous_stage_flow: Dict[str, Any] | None,
    extracted_edges: Dict[str, List[str]] | None,
    alerts: List[Dict[str, Any]] | None,
    source_text: str = '',
) -> Dict[str, Any]:
    previous_stage_flow = previous_stage_flow or {}
    extracted_edges = extracted_edges or {}
    alerts = alerts or []

    alert_map = _build_alert_map(alerts)
    current_standard_keys, flat_nodes = _extract_standard_keys(extracted_edges)
    evidence_signals = _detect_evidence_signals(source_text)

    previous_confirmed_standard_keys = set(previous_stage_flow.get("confirmed_standard_keys", []) or previous_stage_flow.get("all_standard_keys", []) or [])
    confirmed_standard_keys = set(previous_confirmed_standard_keys).union(current_standard_keys)

    previous_stage_id = previous_stage_flow.get("current_stage_id") or PROJECT_STAGE_DEFINITIONS[0]["id"]
    previous_stage_index = 1
    for stage in PROJECT_STAGE_DEFINITIONS:
        if stage["id"] == previous_stage_id:
            previous_stage_index = int(stage["index"])
            break

    previous_stages = previous_stage_flow.get("stages") or {}

    # 顺序闯关：每一轮只允许评估一个“当前阶段”。
    # 如果上一轮刚好完成，则通过 next_stage_index 在下一轮再进入下一阶段。
    pending_next_stage_index = int(previous_stage_flow.get("next_stage_index") or 0)

    is_force_completed = previous_stage_flow.get("overall_status") == "completed" or pending_next_stage_index > len(PROJECT_STAGE_DEFINITIONS)
    
    if previous_stage_flow.get("overall_status") == "completed":
        evaluation_stage_index = len(PROJECT_STAGE_DEFINITIONS)
    elif pending_next_stage_index:
        evaluation_stage_index = pending_next_stage_index
    else:
        evaluation_stage_index = int(previous_stage_flow.get("current_stage_index") or previous_stage_index or 1)
    evaluation_stage_index = max(1, min(evaluation_stage_index, len(PROJECT_STAGE_DEFINITIONS)))

    def _make_base_stage(stage_def: Dict[str, Any], previous_stage: Dict[str, Any] | None) -> Dict[str, Any]:
        previous_stage = previous_stage or {}
        rule_ids = list(stage_def.get("rule_ids", []))
        return {
            "id": stage_def["id"],
            "index": stage_def["index"],
            "label": stage_def["label"],
            "short_label": stage_def.get("short_label", stage_def["label"]),
            "subtitle": stage_def.get("subtitle", ''),
            "goal": stage_def.get("goal", ''),
            "coach_hint": stage_def.get("coach_hint", ''),
            "status": previous_stage.get("status", "locked"),
            "progress_pct": int(previous_stage.get("progress_pct", 0) or 0),
            "pass_threshold": stage_def.get("pass_threshold", 80),
            "rule_ids": rule_ids,
            "active_rule_ids": list(previous_stage.get("active_rule_ids", []) or []),
            "resolved_rule_ids": list(previous_stage.get("resolved_rule_ids", []) or []),
            "critical_unresolved": list(previous_stage.get("critical_unresolved", []) or []),
            "active_alerts": list(previous_stage.get("active_alerts", []) or []),
            "sticky_reopened_alerts": list(previous_stage.get("sticky_reopened_alerts", []) or []),
            "sticky_reopened_rule_ids": list(previous_stage.get("sticky_reopened_rule_ids", []) or []),
            "reopened_rule_counts": dict(previous_stage.get("reopened_rule_counts", {}) or {}),
            "followup_questions": list(previous_stage.get("followup_questions", []) or []),
            "score_breakdown": dict(previous_stage.get("score_breakdown", {}) or {}),
            "anchor_status": dict(previous_stage.get("anchor_status", {}) or {}),
            "can_advance": bool(previous_stage.get("can_advance", False)),
            "blocked_reasons": list(previous_stage.get("blocked_reasons", []) or []),
            "advance_rule_text": previous_stage.get("advance_rule_text") or f"进度≥{int(stage_def.get('pass_threshold', 80))}% + 关键高危规则控制在允许范围内 + 结构锚点达到要求",
            "memory_applied": bool(previous_stage),
        }

    stage_results: List[Dict[str, Any]] = []
    evaluated_stage_result: Dict[str, Any] | None = None

    for stage in PROJECT_STAGE_DEFINITIONS:
        stage_id = stage["id"]
        stage_index = int(stage["index"])
        previous_stage = previous_stages.get(stage_id) or {}
        rule_ids = list(stage.get("rule_ids", []))

        if stage_index < evaluation_stage_index:
            stage_block = _make_base_stage(stage, previous_stage)
            stage_block.update(
                {
                    "status": "passed",
                    "progress_pct": max(int(stage_block.get("progress_pct", 0) or 0), int(stage.get("pass_threshold", 80))),
                    "active_rule_ids": [],
                    "active_alerts": [],
                    "critical_unresolved": [],
                    "sticky_reopened_alerts": [],
                    "sticky_reopened_rule_ids": [],
                    "followup_questions": [],
                    "can_advance": True,
                    "blocked_reasons": [],
                }
            )
            if not stage_block.get("resolved_rule_ids"):
                stage_block["resolved_rule_ids"] = list(rule_ids)
            if not stage_block.get("anchor_status"):
                stage_block["anchor_status"] = {
                    "passed": True,
                    "groups": [],
                    "missing_labels": [],
                    "passed_group_count": len(stage.get("anchor_groups", [])),
                    "required_group_count": int(stage.get("anchor_min_groups", len(stage.get("anchor_groups", [])) if stage.get("anchor_groups") else 0)),
                }
            stage_results.append(stage_block)
            continue

        if stage_index > evaluation_stage_index:
            stage_block = _make_base_stage(stage, previous_stage)
            stage_block.update(
                {
                    "status": "locked",
                    # 未解锁阶段不使用本轮文本重新打分，避免在第一阶段直接把第二、三阶段也“提前通关”。
                    "progress_pct": int(previous_stage.get("progress_pct", 0) or 0),
                    "active_rule_ids": list(previous_stage.get("active_rule_ids", []) or []),
                    "active_alerts": list(previous_stage.get("active_alerts", []) or []),
                    "critical_unresolved": list(previous_stage.get("critical_unresolved", []) or []),
                    "followup_questions": list(previous_stage.get("followup_questions", []) or []),
                    "can_advance": False,
                    "blocked_reasons": list(previous_stage.get("blocked_reasons", []) or []),
                }
            )
            stage_results.append(stage_block)
            continue

        # 仅评估当前阶段
        active_alerts_raw = [alert_map[rule_id] for rule_id in rule_ids if rule_id in alert_map]
        previous_resolved_rule_ids = set(previous_stage.get("resolved_rule_ids", []) or [])
        previous_reopened_rule_counts = previous_stage.get("reopened_rule_counts") or {}

        unresolved_rule_ids: List[str] = []
        active_alerts: List[Dict[str, Any]] = []
        sticky_reopened_alerts: List[Dict[str, Any]] = []
        reopened_rule_counts: Dict[str, int] = {}

        for alert in active_alerts_raw:
            rule_id = alert.get("rule")
            if not rule_id:
                continue

            if rule_id in previous_resolved_rule_ids:
                reopen_count = int(previous_reopened_rule_counts.get(rule_id, 0)) + 1
                reopened_rule_counts[rule_id] = reopen_count
                # 放宽：高质量项目在后续补充中经常会带出新问题，不应因为一次回摆就重新卡死。
                if reopen_count >= 3:
                    unresolved_rule_ids.append(rule_id)
                    active_alerts.append(alert)
                else:
                    sticky_reopened_alerts.append(alert)
            else:
                unresolved_rule_ids.append(rule_id)
                active_alerts.append(alert)

        unresolved_rule_ids = _normalize_rule_ids(unresolved_rule_ids, rule_ids)
        resolved_rule_ids = _normalize_rule_ids(
            [rule_id for rule_id in rule_ids if rule_id not in unresolved_rule_ids] + list(previous_resolved_rule_ids),
            rule_ids,
        )

        critical_unresolved = [
            alert.get("rule") for alert in active_alerts if (alert.get("severity") or '').lower() == 'critical'
        ]
        critical_unresolved = _normalize_rule_ids([item for item in critical_unresolved if item], rule_ids)

        total_weight = sum(_rule_weight(rule_id, alert_map) for rule_id in rule_ids) or 1
        unresolved_weight = sum(_rule_weight(rule_id, alert_map) for rule_id in unresolved_rule_ids)
        resolved_weight = max(total_weight - unresolved_weight, 0)
        progress_pct = int(round((resolved_weight / total_weight) * 100))
        progress_pct += _stage_progress_bonus(stage_id, evidence_signals)
        progress_pct = min(progress_pct, 100)
        progress_pct = max(progress_pct, int(previous_stage.get("progress_pct", 0) or 0))

        anchor_status = _resolve_anchor_status(
            stage,
            confirmed_standard_keys,
            source_text=source_text,
            previous_groups=(previous_stage.get("anchor_status", {}) or {}).get("groups", []),
            evidence_signals=evidence_signals,
        )

        blockers = _build_stage_blockers(
            progress_pct=progress_pct,
            pass_threshold=int(stage.get("pass_threshold", 80)),
            critical_unresolved=critical_unresolved,
            anchor_status=anchor_status,
            max_critical_carryover=int(stage.get("max_critical_carryover", 0)),
        )

        passed = not blockers
        followup_questions = select_project_followup_questions(active_alerts, source_text=source_text, max_questions=3) if not passed else []
        stage_block = {
            "id": stage_id,
            "index": stage["index"],
            "label": stage["label"],
            "short_label": stage.get("short_label", stage["label"]),
            "subtitle": stage.get("subtitle", ''),
            "goal": stage.get("goal", ''),
            "coach_hint": stage.get("coach_hint", ''),
            "status": "passed" if passed else "current",
            "progress_pct": progress_pct,
            "pass_threshold": stage.get("pass_threshold", 80),
            "rule_ids": rule_ids,
            "active_rule_ids": unresolved_rule_ids,
            "resolved_rule_ids": resolved_rule_ids,
            "critical_unresolved": critical_unresolved,
            "active_alerts": [] if passed else active_alerts,
            "sticky_reopened_alerts": sticky_reopened_alerts,
            "sticky_reopened_rule_ids": _normalize_rule_ids(
                [alert.get("rule") for alert in sticky_reopened_alerts if alert.get("rule")],
                rule_ids,
            ),
            "reopened_rule_counts": reopened_rule_counts,
            "followup_questions": followup_questions,
            "score_breakdown": {
                "total_weight": total_weight,
                "resolved_weight": resolved_weight,
                "unresolved_weight": unresolved_weight,
                "evidence_bonus": _stage_progress_bonus(stage_id, evidence_signals),
            },
            "anchor_status": anchor_status,
            "can_advance": not blockers,
            "blocked_reasons": blockers,
            "advance_rule_text": f"进度≥{int(stage.get('pass_threshold', 80))}% + 关键高危规则控制在允许范围内 + 结构锚点达到要求",
            "memory_applied": bool(previous_stage),
        }
        stage_results.append(stage_block)
        evaluated_stage_result = stage_block

    if evaluated_stage_result is None:
        evaluated_stage_result = stage_results[-1]

    current_stage_index = evaluation_stage_index
    current_stage_def = PROJECT_STAGE_DEFINITIONS[current_stage_index - 1]
    current_stage_passed = evaluated_stage_result.get("status") == "passed"

    # 新增：判断上一轮的上一阶段是否已经自然通关
    prev_stage_was_passed_last_turn = previous_stages.get(previous_stage_id, {}).get("status") == "passed"
    
    # 修正精算：强制跳跃的判定标准 -> 当前阶段大于历史阶段，且历史阶段在上一次并没有自然通关
    is_forced_jump = current_stage_index > previous_stage_index and not prev_stage_was_passed_last_turn
    just_upgraded = current_stage_passed

    next_stage_index = None
    next_stage_label = None
    overall_status = "completed" if (current_stage_passed and current_stage_index == len(PROJECT_STAGE_DEFINITIONS)) else "in_progress"

    if current_stage_passed and current_stage_index < len(PROJECT_STAGE_DEFINITIONS):
        next_stage_index = current_stage_index + 1
        next_stage_label = PROJECT_STAGE_DEFINITIONS[next_stage_index - 1]["label"]

    normalized_stage_results: Dict[str, Dict[str, Any]] = {}
    for stage in stage_results:
        stage_index = int(stage["index"])
        if stage_index < current_stage_index:
            stage["status"] = "passed"
        elif stage_index == current_stage_index:
            stage["status"] = "passed" if current_stage_passed else "current"
        else:
            stage["status"] = "locked"
        normalized_stage_results[stage["id"]] = stage

    if just_upgraded:
        milestone_message = current_stage_def.get("milestone_message", '')
    elif is_forced_jump:
        skipped_stage_def = PROJECT_STAGE_DEFINITIONS[previous_stage_index - 1]
        milestone_message = f"【系统提示：教师已强制调控流转至“{current_stage_def.get('label')}”】上一阶段未达标规则已作豁免处理。"
    else:
        milestone_message = ""

    current_stage_alerts = list(evaluated_stage_result.get("active_alerts", []))
    current_followup_questions = list(evaluated_stage_result.get("followup_questions", []))
    guardrail_rule_ids = list(current_stage_def.get("guardrail_rule_ids", []))
    guardrail_alerts = [alert_map[rule_id] for rule_id in guardrail_rule_ids if rule_id in alert_map]

    blockers = list(evaluated_stage_result.get("blocked_reasons", []))
    stage_progress_summary = {
        "resolved_rules": len(evaluated_stage_result.get("resolved_rule_ids", [])),
        "total_rules": len(evaluated_stage_result.get("rule_ids", [])),
        "critical_remaining": len(evaluated_stage_result.get("critical_unresolved", [])),
        "sticky_watchlist": len(evaluated_stage_result.get("sticky_reopened_rule_ids", [])),
        "blocked_reason_count": len(blockers),
        "can_advance": not blockers,
    }

    return {
        "current_stage_id": evaluated_stage_result["id"],
        "current_stage_label": evaluated_stage_result["label"],
        "current_stage_index": evaluated_stage_result["index"],
        "next_stage_index": next_stage_index,
        "next_stage_label": next_stage_label,
        "overall_status": overall_status,
        "just_upgraded": just_upgraded,
        "milestone_message": milestone_message,
        "current_stage_entry_message": current_stage_def.get("entry_message", ''),
        "global_guardrail_rule_ids": guardrail_rule_ids,
        "current_stage_alerts": current_stage_alerts,
        "current_followup_questions": current_followup_questions,
        "global_guardrail_alerts": guardrail_alerts,
        "stage_progress_summary": stage_progress_summary,
        "current_stage_gate": {
            "ready": not blockers,
            "advance_rule_text": evaluated_stage_result.get("advance_rule_text", ''),
            "blocked_reasons": blockers,
            "max_critical_carryover": int(current_stage_def.get("max_critical_carryover", 0)),
        },
        "all_triggered_rule_ids": [alert.get("rule") for alert in alerts if alert.get("rule")],
        "all_standard_keys": sorted(current_standard_keys),
        "confirmed_standard_keys": sorted(confirmed_standard_keys),
        "evidence_signals": evidence_signals,
        "all_extracted_nodes": flat_nodes,
        "stages": normalized_stage_results,
    }

