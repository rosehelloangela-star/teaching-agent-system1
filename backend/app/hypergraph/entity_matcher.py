from typing import List, Dict, Set, Tuple
from rapidfuzz import fuzz

# 超图底层的标准英文节点到中文别名的映射池
HYPER_NODE_ALIASES: Dict[str, List[str]] = {
    "Target_Customer": ["目标客群", "目标用户", "用户画像", "下沉市场", "受众", "群体", "客户"],
    "Value_Proposition": ["价值主张", "核心卖点", "产品价值", "解决问题", "差异化价值"],
    "Marketing_Channel": ["营销渠道", "推广渠道", "获客渠道", "怎么卖", "触达", "地推", "投流"],
    "Revenue_Model": ["收入模型", "盈利模式", "商业模式", "怎么赚钱", "订阅", "买断", "抽成"],
    "Cost_Structure": ["成本结构", "固定成本", "可变成本", "支出", "开销"],
    "Core_Pain_Point": ["核心痛点", "用户痛点", "痛点", "伪需求", "痛处", "真实需求"],
    "Price": ["产品定价", "客单价", "单价", "收费标准", "价格"],
    "LTV": ["客户终身价值", "LTV", "复购价值"],
    "CAC": ["获客成本", "CAC", "拉新成本"],
    "Startup_Capital": ["启动资金", "初始资金", "融资金额", "天使轮", "早期投入"],
    "Account_Period": ["账期", "回款周期", "垫资", "结款", "结算周期"],
    "Seed_Users": ["种子用户", "早期用户", "冷启动用户", "天使用户"],
    "Tech_Route": ["技术路线", "核心技术", "底层技术", "算法", "研发方案"],
    "Team_Background": ["团队背景", "创始人", "团队成员", "博士", "教授", "研发团队"],
    "Competitor_Pool": ["竞品", "竞争对手", "替代方案", "市场上", "同类产品"],
    "IP": ["知识产权", "专利", "软著", "壁垒", "技术护城河"],
    "Fulfill_Cost": ["履约成本", "交付成本", "物流成本", "安装成本", "实施成本"],
    "Supplier_Network": ["供应链", "供应商", "代工厂", "上游厂商"],
    "Control_Experiment": ["对照实验", "验证数据", "对比数据", "测试组", "实验结果"],
    "TAM": ["总潜在市场", "tam", "总体市场规模"],
    "SAM": ["可服务潜在市场", "sam", "目标细分市场"],
    "SOM": ["可获得服务市场", "som", "实际可获得市场"],
    "Usage_Frequency": ["使用频次", "打开率", "复购率", "低频", "高频"],
    "Milestone_Plan": ["里程碑", "发展规划", "时间表", "落地计划"],
    "Policy_Constraints": ["政策约束", "合规", "政策风险", "法律法规"]
}

def _normalize_text(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "")

def detect_hyper_nodes(
    user_input: str,
    fuzzy_threshold: int = 72,
    debug: bool = False
) -> List[str]:
    """
    三层识别超图标准英文节点：
    1. 别名/同义词精确命中
    2. 别名/同义词包含命中
    3. 模糊匹配兜底
    """
    if not user_input:
        if debug:
            print("[hyper_matcher] 用户输入为空，返回空结果。", flush=True)
        return []

    normalized_input = _normalize_text(user_input)
    detected: Set[str] = set()

    alias_hits: List[Tuple[str, str]] = []
    fuzzy_hits: List[Tuple[str, str, int]] = []
    fuzzy_candidates: List[Tuple[str, str, int]] = []

    if debug:
        print(f"[hyper_matcher] 归一化输入：{normalized_input}", flush=True)

    # 我们定义的超图标准节点池 (英文Key)
    all_hyper_nodes = list(HYPER_NODE_ALIASES.keys())

    # -------------------------
    # 第一层 & 第二层：别名精确与包含命中
    # -------------------------
    for canonical_name, aliases in HYPER_NODE_ALIASES.items():
        for alias in aliases:
            normalized_alias = _normalize_text(alias)
            if normalized_alias and normalized_alias in normalized_input:
                detected.add(canonical_name)
                alias_hits.append((canonical_name, alias))
                break # 命中一个别名即可跳出当前 canonical_name 的循环

    if debug:
        print(f"[hyper_matcher] 别名包含命中={alias_hits}", flush=True)

    # -------------------------
    # 第三层：模糊匹配兜底
    # -------------------------
    for canonical_name, aliases in HYPER_NODE_ALIASES.items():
        # 如果前面已经命中了，就不再做模糊计算
        if canonical_name in detected:
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
        print(f"[hyper_matcher] 模糊命中={fuzzy_hits}", flush=True)
        print(f"[hyper_matcher] Top 3 模糊候选={sorted_candidates[:3]}", flush=True)

    # 保持固定顺序输出
    ordered_detected = [node for node in all_hyper_nodes if node in detected]

    if debug:
        print(f"[hyper_matcher] 最终识别超图节点={ordered_detected}", flush=True)

    return ordered_detected