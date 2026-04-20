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
    "Policy_Constraints": ["政策约束", "合规", "政策风险", "法律法规"],
    "Beneficiary_Group": ["受益对象", "服务对象", "受助群体", "受益群体", "帮扶对象"],
    "Service_Scenario": ["服务场景", "应用场景", "发生场景", "介入场景"],
    "Research_Sample": ["调研样本", "样本量", "访谈样本", "调查样本"],
    "Problem_Severity": ["问题严重度", "问题程度", "紧迫性", "严重性"],
    "Intervention_Solution": ["干预方案", "介入方案", "服务方案", "解决方案"],
    "Expected_Outcome": ["预期成效", "预期结果", "预期影响", "目标结果"],
    "Funding_Source": ["资金来源", "筹资来源", "资助方", "捐赠来源"],
    "Grant_Channel": ["资助渠道", "申报渠道", "筹资渠道", "政府购买服务"],
    "Revenue_Supplement": ["补充收入", "配套收入", "造血收入", "服务收费"],
    "Impact_Goal": ["影响目标", "公益目标", "社会目标", "成效目标"],
    "Indicator_System": ["指标体系", "衡量指标", "评估指标", "KPI"],
    "Baseline_Data": ["基线数据", "前测数据", "初始数据"],
    "Evaluation_Method": ["评估方法", "评估方式", "验证方法"],
    "Financial_Disclosure": ["财务公开", "资金公示", "财务披露", "公开透明"],
    "Third_Party_Endorsement": ["第三方背书", "第三方认证", "外部背书"],
    "Pilot_Site": ["试点点位", "试点地区", "试点学校", "试点社区"],
    "Pilot_Result": ["试点结果", "试点成效", "试点反馈"],
    "Expansion_Path": ["扩散路径", "复制路径", "推广路径", "规模化路径"],
    "Volunteer_Role": ["志愿者角色", "志愿者分工", "志愿者岗位"],
    "Training_Process": ["培训流程", "培训机制", "培训体系"],
    "Key_Resource": ["关键资源", "核心资源", "关键要素"],
    "Risk_Buffer": ["风险缓冲", "风险预案", "备用方案"],
    "Policy_Basis": ["政策依据", "政策基础", "法规依据"],
    "Qualification_Requirement": ["资质要求", "准入要求", "执业要求"],
    "Enterprise_Partner": ["企业伙伴", "企业合作方", "企业资源方"],
    "CoCreation_Mode": ["共创模式", "协同模式", "合作机制"],
    "Longterm_Mechanism": ["长期机制", "长效机制", "持续机制"],
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

# from typing import List, Dict, Set, Tuple
# from rapidfuzz import fuzz

# # 超图底层的标准英文节点到中文别名的映射池
# HYPER_NODE_ALIASES: Dict[str, List[str]] = {
#     "Target_Customer": ["目标客群", "目标用户", "用户画像", "下沉市场", "目标客户群", "客户画像"],
#     "Value_Proposition": ["价值主张", "核心卖点", "产品价值", "解决问题", "差异化价值"],
#     "Marketing_Channel": ["营销渠道", "推广渠道", "获客渠道", "怎么卖", "触达", "地推", "投流"],
#     "Revenue_Model": ["收入模型", "盈利模式", "商业模式", "怎么赚钱", "订阅", "买断", "抽成"],
#     "Cost_Structure": ["成本结构", "固定成本", "可变成本", "运营开销", "成本支出"],
#     "Core_Pain_Point": ["核心痛点", "用户痛点", "关键痛点", "伪需求", "真实需求"],
#     "Price": ["产品定价", "客单价", "单价", "收费标准", "价格"],
#     "LTV": ["客户终身价值", "LTV", "复购价值"],
#     "CAC": ["获客成本", "CAC", "拉新成本"],
#     "Startup_Capital": ["启动资金", "初始资金", "融资金额", "天使轮", "早期投入"],
#     "Account_Period": ["账期", "回款周期", "垫资", "结款", "结算周期"],
#     "Seed_Users": ["种子用户", "早期用户", "冷启动用户", "天使用户"],
#     "Tech_Route": ["技术路线", "核心技术", "底层技术", "算法", "研发方案"],
#     "Team_Background": ["团队背景", "创始人", "团队成员", "博士", "教授", "研发团队"],
#     "Competitor_Pool": ["竞品", "竞争对手", "替代方案", "市场上", "同类产品"],
#     "IP": ["知识产权", "专利", "软著", "技术护城河", "专利壁垒"],
#     "Fulfill_Cost": ["履约成本", "交付成本", "物流成本", "安装成本", "实施成本"],
#     "Supplier_Network": ["供应链", "供应商", "代工厂", "上游厂商"],
#     "Control_Experiment": ["对照实验", "验证数据", "对比数据", "测试组", "实验结果"],
#     "TAM": ["总潜在市场", "tam", "总体市场规模"],
#     "SAM": ["可服务潜在市场", "sam", "目标细分市场"],
#     "SOM": ["可获得服务市场", "som", "实际可获得市场"],
#     "Usage_Frequency": ["使用频次", "打开率", "复购率", "低频", "高频"],
#     "Milestone_Plan": ["里程碑", "发展规划", "阶段计划", "落地计划"],
#     "Policy_Constraints": ["政策约束", "合规", "政策风险", "法律法规"],
#     "Beneficiary": ["受益对象", "受益人", "服务对象", "帮扶对象"],
#     "Service_Object": ["服务对象", "服务人群", "重点人群"],
#     "Social_Issue": ["社会问题", "公共问题", "公益痛点", "社会痛点"],
#     "Survey_Data": ["调研数据", "问卷数据", "统计数据"],
#     "Interview_Record": ["访谈记录", "深访", "用户访谈", "实地访谈"],
#     "Case_Study": ["案例研究", "典型案例", "试点案例"],
#     "Service_Process": ["服务流程", "干预流程", "执行流程"],
#     "Donation_Source": ["捐赠来源", "捐赠方", "基金支持"],
#     "Partnership_Model": ["合作模式", "合作伙伴", "协同机制", "联动合作机制"],
#     "Volunteer_System": ["志愿者体系", "志愿者机制", "志愿者招募"],
#     "Impact_Metric": ["成效指标", "影响指标", "社会影响指标"],
#     "KPI": ["KPI", "关键指标", "考核指标"],
#     "Outcome_Index": ["结果指标", "产出指标", "效果指标"],
#     "Replication_Path": ["复制路径", "扩散路径", "推广路径", "规模化路径"]
# }

# def _normalize_text(text: str) -> str:
#     return (text or "").strip().lower().replace(" ", "")

# def detect_hyper_nodes(
#     user_input: str,
#     fuzzy_threshold: int = 72,
#     debug: bool = False
# ) -> List[str]:
#     """
#     三层识别超图标准英文节点：
#     1. 别名/同义词精确命中
#     2. 别名/同义词包含命中
#     3. 模糊匹配兜底
#     """
#     if not user_input:
#         if debug:
#             print("[hyper_matcher] 用户输入为空，返回空结果。", flush=True)
#         return []

#     normalized_input = _normalize_text(user_input)
#     detected: Set[str] = set()

#     alias_hits: List[Tuple[str, str]] = []
#     fuzzy_hits: List[Tuple[str, str, int]] = []
#     fuzzy_candidates: List[Tuple[str, str, int]] = []

#     if debug:
#         print(f"[hyper_matcher] 归一化输入：{normalized_input}", flush=True)

#     # 我们定义的超图标准节点池 (英文Key)
#     all_hyper_nodes = list(HYPER_NODE_ALIASES.keys())

#     # -------------------------
#     # 第一层 & 第二层：别名精确与包含命中
#     # -------------------------
#     for canonical_name, aliases in HYPER_NODE_ALIASES.items():
#         for alias in aliases:
#             normalized_alias = _normalize_text(alias)
#             if normalized_alias and normalized_alias in normalized_input:
#                 detected.add(canonical_name)
#                 alias_hits.append((canonical_name, alias))
#                 break # 命中一个别名即可跳出当前 canonical_name 的循环

#     if debug:
#         print(f"[hyper_matcher] 别名包含命中={alias_hits}", flush=True)

#     # -------------------------
#     # 第三层：模糊匹配兜底
#     # -------------------------
#     for canonical_name, aliases in HYPER_NODE_ALIASES.items():
#         # 如果前面已经命中了，就不再做模糊计算
#         if canonical_name in detected:
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
#         print(f"[hyper_matcher] 模糊命中={fuzzy_hits}", flush=True)
#         print(f"[hyper_matcher] Top 3 模糊候选={sorted_candidates[:3]}", flush=True)

#     # 保持固定顺序输出
#     ordered_detected = [node for node in all_hyper_nodes if node in detected]

#     if debug:
#         print(f"[hyper_matcher] 最终识别超图节点={ordered_detected}", flush=True)

#     return ordered_detected