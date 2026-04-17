from typing import List, Dict, Set, Tuple
from rapidfuzz import fuzz

ENTITY_ALIASES: Dict[str, List[str]] = {
    # 市场分析
    "总潜在市场(TAM)": ["总潜在市场", "tam", "总体市场", "总体市场规模"],
    "可服务市场(SAM)": ["可服务市场", "sam", "目标细分市场", "可触达市场"],
    "可获得市场(SOM)": ["可获得市场", "som", "实际市场份额", "可拿下的市场"],
    "用户画像(Persona)": ["用户画像", "目标用户", "用户群体", "受众", "目标人群"],
    "核心痛点": ["核心痛点", "用户痛点", "真正的问题", "痛点", "需求痛点"],
    "伪需求": ["伪需求", "假需求", "虚假需求", "不是刚需"],
    "TAM替代SOM": ["用tam代替som", "盲目夸大市场", "市场规模夸大"],
    
    # 产品与验证
    "最小可行性产品(MVP)": ["最小可行性产品", "mvp", "原型", "初期产品", "极简产品"],
    "产品市场契合度(PMF)": ["产品市场契合度", "pmf", "市场契合度"],
    "核心壁垒(Moat)": ["核心壁垒", "护城河", "壁垒", "核心优势", "竞争壁垒"],
    "冷启动(Cold Start)": ["冷启动", "早期获客", "从零开始"],
    
    # 商业模式与指标
    "商业模式(Business Model)": ["商业模式", "盈利模式", "怎么赚钱", "变现方式"],
    "价值主张(Value Proposition)": ["价值主张", "产品价值", "核心卖点", "独特价值"],
    "获客成本(CAC)": ["获客成本", "cac", "拉新成本"],
    "用户终身价值(LTV)": ["用户终身价值", "ltv", "单客价值"],
    "单均经济模型(Unit Economics)": ["单均经济模型", "ue模型", "单体经济模型", "ue"],
    "投资回报率(ROI)": ["投资回报率", "roi", "回报率"],
}

def _normalize_text(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "")

def detect_concepts(
    user_input: str,
    all_db_nodes: List[str],
    fuzzy_threshold: int = 72,
    debug: bool = True
) -> List[str]:
    """返回签名与原版完全一致，内部强化 Logger 埋点"""
    if not user_input: return []

    normalized_input = _normalize_text(user_input)
    detected: Set[str] = set()
    exact_hits, alias_hits, fuzzy_hits = [], [], []

    for node in all_db_nodes:
        if _normalize_text(node) and _normalize_text(node) in normalized_input:
            detected.add(node); exact_hits.append(node)

    for canonical_name, aliases in ENTITY_ALIASES.items():
        if canonical_name not in all_db_nodes: continue
        for alias in aliases:
            if _normalize_text(alias) and _normalize_text(alias) in normalized_input:
                detected.add(canonical_name); alias_hits.append(f"{alias}=>{canonical_name}")
                break

    for canonical_name, aliases in ENTITY_ALIASES.items():
        if canonical_name not in all_db_nodes: continue
        for alias in aliases:
            score = fuzz.partial_ratio(_normalize_text(alias), normalized_input)
            if score >= fuzzy_threshold:
                detected.add(canonical_name); fuzzy_hits.append(f"{alias}({score}%)=>{canonical_name}")
                break

    ordered_detected = [node for node in all_db_nodes if node in detected]

    if debug:
        print("\n" + "-"*40, flush=True)
        print("[KG_Logger] 🔎 实体漏斗匹配轨迹:", flush=True)
        if exact_hits: print(f" ├─ [Layer1 精确命中]: {exact_hits}", flush=True)
        if alias_hits: print(f" ├─ [Layer2 别名命中]: {alias_hits}", flush=True)
        if fuzzy_hits: print(f" └─ [Layer3 模糊命中]: {fuzzy_hits}", flush=True)
        if not ordered_detected: print(" └─ 未命中任何实体", flush=True)
        print("-"*40 + "\n", flush=True)

    return ordered_detected

# from typing import List, Dict, Set, Tuple
# from rapidfuzz import fuzz


# ENTITY_ALIASES: Dict[str, List[str]] = {
#     "用户画像(User Persona)": [
#         "用户画像", "目标用户", "用户群体", "目标人群", "受众画像", "用户特征", "用户是谁", "服务对象"
#     ],
#     "核心痛点(Core Pain Point)": [
#         "核心痛点", "用户痛点", "痛点", "关键问题", "主要问题", "用户问题", "需求痛点", "核心需求",
#         "核心问题", "最核心的问题", "用户最核心的问题", "用户最核心的难题", "真正的问题"
#     ],
#     "价值主张(Value Proposition)": [
#         "价值主张", "产品价值", "核心卖点", "卖点", "差异化价值", "独特价值", "为什么买", "产品优势"
#     ],
#     "商业模式(Business Model)": [
#         "商业模式", "盈利模式", "变现方式", "赚钱方式", "怎么赚钱", "收入模式"
#     ],
#     "总潜在市场(TAM)": [
#         "总潜在市场", "tam", "总体市场", "总市场", "市场规模", "整体市场规模"
#     ],
#     "可服务潜在市场(SAM)": [
#         "可服务潜在市场", "sam", "可服务市场", "目标细分市场", "可触达市场"
#     ],
#     "可获得服务市场(SOM)": [
#         "可获得服务市场", "som", "实际可获得市场", "实际市场份额", "可拿下的市场"
#     ],
#     "精益画布(Lean Canvas)": [
#         "精益画布", "lean canvas", "画布", "商业画布"
#     ],
#     "用户访谈(User Interview)": [
#         "用户访谈", "访谈", "用户调研", "用户采访", "访谈记录"
#     ],
#     "商业计划书(BP)": [
#         "商业计划书", "bp", "计划书", "创业计划书"
#     ],
#     "伪需求": [
#         "伪需求", "假需求", "虚假需求"
#     ],
#     "逻辑自洽幻觉": [
#         "逻辑自洽幻觉", "逻辑幻觉", "自洽幻觉"
#     ],
#     "无竞争对手错觉": [
#         "无竞争对手错觉", "没有竞争对手", "无竞品错觉"
#     ],
#     "TAM替代SOM": [
#         "tam替代som", "用tam代替som", "市场规模夸大"
#     ],
# }


# def _normalize_text(text: str) -> str:
#     return (text or "").strip().lower().replace(" ", "")


# def detect_concepts(
#     user_input: str,
#     all_db_nodes: List[str],
#     fuzzy_threshold: int = 72,
#     debug: bool = True
# ) -> List[str]:
#     """
#     三层识别：
#     1. 精确实体名命中
#     2. 别名/同义词命中
#     3. 模糊匹配兜底
#     """
#     if not user_input:
#         if debug:
#             print("[entity_matcher] 用户输入为空，返回空结果。", flush=True)
#         return []

#     normalized_input = _normalize_text(user_input)
#     detected: Set[str] = set()

#     exact_hits: List[str] = []
#     alias_hits: List[Tuple[str, str]] = []
#     fuzzy_hits: List[Tuple[str, str, int]] = []
#     fuzzy_candidates: List[Tuple[str, str, int]] = []

#     if debug:
#         print(f"[entity_matcher] 原始输入：{user_input}", flush=True)
#         print(f"[entity_matcher] 归一化输入：{normalized_input}", flush=True)

#     # -------------------------
#     # 第一层：精确实体名命中
#     # -------------------------
#     for node in all_db_nodes:
#         normalized_node = _normalize_text(node)
#         if normalized_node and normalized_node in normalized_input:
#             detected.add(node)
#             exact_hits.append(node)

#     if debug:
#         print(f"[entity_matcher] 精确命中={exact_hits}", flush=True)

#     # -------------------------
#     # 第二层：别名命中
#     # -------------------------
#     for canonical_name, aliases in ENTITY_ALIASES.items():
#         if canonical_name not in all_db_nodes:
#             continue

#         for alias in aliases:
#             normalized_alias = _normalize_text(alias)
#             if normalized_alias and normalized_alias in normalized_input:
#                 detected.add(canonical_name)
#                 alias_hits.append((canonical_name, alias))
#                 break

#     if debug:
#         print(f"[entity_matcher] 别名命中={alias_hits}", flush=True)

#     # -------------------------
#     # 第三层：模糊匹配
#     # -------------------------
#     for canonical_name, aliases in ENTITY_ALIASES.items():
#         if canonical_name not in all_db_nodes:
#             continue

#         best_alias = ""
#         best_score = 0

#         for alias in aliases:
#             normalized_alias = _normalize_text(alias)
#             score = fuzz.partial_ratio(normalized_alias, normalized_input)
#             if score > best_score:
#                 best_score = score
#                 best_alias = alias

#         fuzzy_candidates.append((canonical_name, best_alias, best_score))

#         if best_score >= fuzzy_threshold:
#             detected.add(canonical_name)
#             fuzzy_hits.append((canonical_name, best_alias, best_score))

#     if debug:
#         sorted_candidates = sorted(fuzzy_candidates, key=lambda x: x[2], reverse=True)
#         print(f"[entity_matcher] 模糊命中阈值={fuzzy_threshold}", flush=True)
#         print(f"[entity_matcher] 模糊命中={fuzzy_hits}", flush=True)
#         print(f"[entity_matcher] Top 5 模糊候选={sorted_candidates[:5]}", flush=True)

#     ordered_detected = [node for node in all_db_nodes if node in detected]

#     if debug:
#         print(f"[entity_matcher] 最终识别结果={ordered_detected}", flush=True)

#     return ordered_detected