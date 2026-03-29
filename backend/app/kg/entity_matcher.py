from typing import List, Dict, Set, Tuple
from rapidfuzz import fuzz


ENTITY_ALIASES: Dict[str, List[str]] = {
    "用户画像(User Persona)": [
        "用户画像", "目标用户", "用户群体", "目标人群", "受众画像", "用户特征", "用户是谁", "服务对象"
    ],
    "核心痛点(Core Pain Point)": [
        "核心痛点", "用户痛点", "痛点", "关键问题", "主要问题", "用户问题", "需求痛点", "核心需求",
        "核心问题", "最核心的问题", "用户最核心的问题", "用户最核心的难题", "真正的问题"
    ],
    "价值主张(Value Proposition)": [
        "价值主张", "产品价值", "核心卖点", "卖点", "差异化价值", "独特价值", "为什么买", "产品优势"
    ],
    "商业模式(Business Model)": [
        "商业模式", "盈利模式", "变现方式", "赚钱方式", "怎么赚钱", "收入模式"
    ],
    "总潜在市场(TAM)": [
        "总潜在市场", "tam", "总体市场", "总市场", "市场规模", "整体市场规模"
    ],
    "可服务潜在市场(SAM)": [
        "可服务潜在市场", "sam", "可服务市场", "目标细分市场", "可触达市场"
    ],
    "可获得服务市场(SOM)": [
        "可获得服务市场", "som", "实际可获得市场", "实际市场份额", "可拿下的市场"
    ],
    "精益画布(Lean Canvas)": [
        "精益画布", "lean canvas", "画布", "商业画布"
    ],
    "用户访谈(User Interview)": [
        "用户访谈", "访谈", "用户调研", "用户采访", "访谈记录"
    ],
    "商业计划书(BP)": [
        "商业计划书", "bp", "计划书", "创业计划书"
    ],
    "伪需求": [
        "伪需求", "假需求", "虚假需求"
    ],
    "逻辑自洽幻觉": [
        "逻辑自洽幻觉", "逻辑幻觉", "自洽幻觉"
    ],
    "无竞争对手错觉": [
        "无竞争对手错觉", "没有竞争对手", "无竞品错觉"
    ],
    "TAM替代SOM": [
        "tam替代som", "用tam代替som", "市场规模夸大"
    ],
}


def _normalize_text(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "")


def detect_concepts(
    user_input: str,
    all_db_nodes: List[str],
    fuzzy_threshold: int = 72,
    debug: bool = True
) -> List[str]:
    """
    三层识别：
    1. 精确实体名命中
    2. 别名/同义词命中
    3. 模糊匹配兜底
    """
    if not user_input:
        if debug:
            print("[entity_matcher] 用户输入为空，返回空结果。", flush=True)
        return []

    normalized_input = _normalize_text(user_input)
    detected: Set[str] = set()

    exact_hits: List[str] = []
    alias_hits: List[Tuple[str, str]] = []
    fuzzy_hits: List[Tuple[str, str, int]] = []
    fuzzy_candidates: List[Tuple[str, str, int]] = []

    if debug:
        print(f"[entity_matcher] 原始输入：{user_input}", flush=True)
        print(f"[entity_matcher] 归一化输入：{normalized_input}", flush=True)

    # -------------------------
    # 第一层：精确实体名命中
    # -------------------------
    for node in all_db_nodes:
        normalized_node = _normalize_text(node)
        if normalized_node and normalized_node in normalized_input:
            detected.add(node)
            exact_hits.append(node)

    if debug:
        print(f"[entity_matcher] 精确命中={exact_hits}", flush=True)

    # -------------------------
    # 第二层：别名命中
    # -------------------------
    for canonical_name, aliases in ENTITY_ALIASES.items():
        if canonical_name not in all_db_nodes:
            continue

        for alias in aliases:
            normalized_alias = _normalize_text(alias)
            if normalized_alias and normalized_alias in normalized_input:
                detected.add(canonical_name)
                alias_hits.append((canonical_name, alias))
                break

    if debug:
        print(f"[entity_matcher] 别名命中={alias_hits}", flush=True)

    # -------------------------
    # 第三层：模糊匹配
    # -------------------------
    for canonical_name, aliases in ENTITY_ALIASES.items():
        if canonical_name not in all_db_nodes:
            continue

        best_alias = ""
        best_score = 0

        for alias in aliases:
            normalized_alias = _normalize_text(alias)
            score = fuzz.partial_ratio(normalized_alias, normalized_input)
            if score > best_score:
                best_score = score
                best_alias = alias

        fuzzy_candidates.append((canonical_name, best_alias, best_score))

        if best_score >= fuzzy_threshold:
            detected.add(canonical_name)
            fuzzy_hits.append((canonical_name, best_alias, best_score))

    if debug:
        sorted_candidates = sorted(fuzzy_candidates, key=lambda x: x[2], reverse=True)
        print(f"[entity_matcher] 模糊命中阈值={fuzzy_threshold}", flush=True)
        print(f"[entity_matcher] 模糊命中={fuzzy_hits}", flush=True)
        print(f"[entity_matcher] Top 5 模糊候选={sorted_candidates[:5]}", flush=True)

    ordered_detected = [node for node in all_db_nodes if node in detected]

    if debug:
        print(f"[entity_matcher] 最终识别结果={ordered_detected}", flush=True)

    return ordered_detected