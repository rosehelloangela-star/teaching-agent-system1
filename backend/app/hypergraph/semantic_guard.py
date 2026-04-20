from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Tuple

STATUS_RANK = {
    "contradictory": 4,
    "suspicious": 3,
    "needs_evidence": 2,
    "confirmed": 1,
    "unknown": 0,
}

SEVERITY_RANK = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

RULE_NAMES = {
    "R1": "全局逻辑散架",
    "R2": "技术与商业双轨孤岛",
    "R3": "叙事因果断裂",
    "R4": "合规逻辑游离",
    "R5": "闭环要素严重缺失",
    "R6": "渠道与客群脱节",
    "R7": "支付意愿支撑不足",
    "R8": "无竞争对手幻觉",
    "R9": "市场漏斗断层",
    "R10": "创新缺乏竞争对标",
    "R11": "单位经济模型崩塌",
    "R12": "利润空间黑盒",
    "R13": "现金流断裂高危",
    "R14": "供应链脱离业务",
    "R15": "冷启动策略空转",
    "R16": "技术壁垒无团队支撑",
    "R17": "执行方案空壳",
    "R18": "财务预测漂浮",
    "R19": "频次与收入模型错配",
    "R20": "公益属性过重",

    "PR1": "受益对象界定模糊",
    "PR2": "公益需求证据薄弱",
    "PR3": "服务设计脱离真实问题",
    "PR4": "关键协同方缺位",
    "PR5": "伦理保护失焦",
    "PR6": "筹资路径不成立",
    "PR7": "公益成本效率黑箱",
    "PR8": "影响评估不可验证",
    "PR9": "受益者转化路径断裂",
    "PR10": "公信力与透明度不足",
    "PR11": "试点无法复制扩散",
    "PR12": "志愿者运营失控",
    "PR13": "关键资源不可持续",
    "PR14": "政策合规落地风险",
    "PR15": "社会共创机制悬空",
}

SEMANTIC_CAPABLE_RULE_IDS = set(RULE_NAMES.keys())

SEMANTIC_BLOCKING_STATUSES = {"contradictory", "suspicious"}

RULE_DEFAULT_SEVERITY = {
    "R1": "high",
    "R2": "critical",
    "R3": "high",
    "R4": "medium",
    "R5": "high",
    "R6": "high",
    "R7": "high",
    "R8": "critical",
    "R9": "medium",
    "R10": "high",
    "R11": "critical",
    "R12": "high",
    "R13": "critical",
    "R14": "high",
    "R15": "medium",
    "R16": "medium",
    "R17": "medium",
    "R18": "high",
    "R19": "high",
    "R20": "medium",

    "PR1": "high",
    "PR2": "high",
    "PR3": "high",
    "PR4": "medium",
    "PR5": "high",
    "PR6": "high",
    "PR7": "medium",
    "PR8": "high",
    "PR9": "medium",
    "PR10": "medium",
    "PR11": "high",
    "PR12": "low",
    "PR13": "high",
    "PR14": "high",
    "PR15": "low",
}

KEY_LABELS = {
    # commercial
    "Target_Customer": "目标客户",
    "Customer_Type": "客户类型",
    "Value_Proposition": "价值主张",
    "Marketing_Channel": "营销渠道",
    "Revenue_Model": "收入模式",
    "Cost_Structure": "成本结构",
    "Core_Pain_Point": "核心痛点",
    "Current_Pain": "当前痛点",
    "Disposable_Income": "可支配收入",
    "Price": "价格",
    "Unit_Price": "客单价",
    "TAM": "TAM",
    "SAM": "SAM",
    "SOM": "SOM",
    "Marketing_Budget": "营销预算",
    "Usage_Frequency": "使用频次",
    "LTV": "LTV",
    "CAC": "CAC",
    "Fixed_Cost": "固定成本",
    "Variable_Cost": "变动成本",
    "Account_Period": "账期",
    "Startup_Capital": "启动资金",
    "Burn_Rate": "烧钱速度",
    "Financial_Model": "财务模型",
    "Key_Assumption": "关键假设",
    "Sensitivity_Analysis": "敏感性分析",
    "Product_Form": "产品形态",
    "Delivery_Method": "交付方式",
    "Fulfill_Cost": "履约成本",
    "Supplier_Network": "供应网络",
    "Platform_Model": "平台模式",
    "Seed_Users": "种子用户",
    "Cold_Start_Strategy": "冷启动策略",
    "TRL": "技术成熟度",
    "Team_Background": "团队背景",
    "Tech_Route": "技术路线",
    "Resource_List": "资源清单",
    "Milestone_Plan": "里程碑计划",
    "Core_Advantage": "核心优势",
    "Competitor_Status": "竞品状态",
    "Switching_Cost": "切换成本",
    "IP": "知识产权",
    "Alternative_Solution": "替代方案",
    "Competitor_Pool": "竞争对手池",
    "Solution": "解决方案",
    "Differentiation": "差异化",
    "Verifiable_Metric": "可验证指标",
    "Control_Experiment": "对照实验",
    "Data_Source": "数据来源",
    "Industry": "行业",
    "Policy_Constraints": "政策限制",
    "Scenario_Research": "场景调研",
    "Pilot_Cooperation": "试点合作",
    "Translation_Roadmap": "转化路径",

    # public welfare
    "Beneficiary_Group": "受益对象",
    "Urgency_Pain": "紧迫问题",
    "Service_Scenario": "服务场景",
    "Accessibility_Constraint": "可及性约束",
    "Research_Sample": "调研样本",
    "Field_Observation": "实地观察",
    "Needs_Quote": "需求引述",
    "Problem_Severity": "问题严重度",
    "Intervention_Solution": "干预方案",
    "Expected_Outcome": "预期成效",
    "Core_Service": "核心服务",
    "Trust_Mechanism": "信任机制",
    "Government_Link": "政府链接",
    "NGO_Partner": "公益伙伴",
    "Community_Leader": "社区关键人",
    "Volunteer_Source": "志愿者来源",
    "Vulnerable_Group": "弱势群体",
    "Ethical_Risk": "伦理风险",
    "Privacy_Protection": "隐私保护",
    "Consent_Process": "知情同意流程",
    "Funding_Source": "资金来源",
    "Donation_Product": "捐赠产品",
    "Grant_Channel": "资助渠道",
    "Revenue_Supplement": "补充收入",
    "Single_Service_Cost": "单次服务成本",
    "Management_Cost": "管理成本",
    "Fund_Use_Ratio": "资金使用比例",
    "Budget_Ceiling": "预算上限",
    "Impact_Goal": "影响目标",
    "Indicator_System": "指标体系",
    "Baseline_Data": "基线数据",
    "Evaluation_Method": "评估方法",
    "Reach_Channel": "触达渠道",
    "Participation_Motivation": "参与动机",
    "Retention_Mechanism": "留存机制",
    "Referral_Path": "转介路径",
    "Disclosure_Frequency": "披露频率",
    "Financial_Disclosure": "财务披露",
    "Story_Evidence": "故事证据",
    "Third_Party_Endorsement": "第三方背书",
    "Pilot_Site": "试点地点",
    "Pilot_Result": "试点结果",
    "Replication_Condition": "复制条件",
    "Expansion_Path": "扩散路径",
    "Volunteer_Role": "志愿者角色",
    "Training_Process": "培训流程",
    "Scheduling_Mechanism": "排班机制",
    "Incentive_NonCash": "非现金激励",
    "Key_Resource": "关键资源",
    "Resource_Gap": "资源缺口",
    "Replacement_Plan": "替代方案",
    "Risk_Buffer": "风险缓冲",
    "Policy_Basis": "政策依据",
    "Qualification_Requirement": "资质要求",
    "Safety_Redline": "安全红线",
    "Public_Opinion_Risk": "舆情风险",
    "Enterprise_Partner": "企业伙伴",
    "School_Hospital_Community": "学校/医院/社区",
    "CoCreation_Mode": "共创模式",
    "Longterm_Mechanism": "长期机制",
}

RULE_SPECS = {
    # ========== Commercial ==========
    "R1": {
        "dimension": "商业闭环基本完整性",
        "left_keys": ["Target_Customer", "Value_Proposition"],
        "right_keys": ["Revenue_Model", "Cost_Structure"],
        "hint": "请至少补清：你服务谁、提供什么价值、如何收费、核心成本是什么。",
    },
    "R2": {
        "dimension": "技术路线 × 商业闭环",
        "left_keys": ["Tech_Route", "Core_Advantage", "IP"],
        "right_keys": ["Value_Proposition", "Revenue_Model"],
        "hint": "请说明：技术具体提升了哪一项用户价值，或改善了哪一个收费环节。",
    },
    "R3": {
        "dimension": "痛点 × 解决方案",
        "left_keys": ["Core_Pain_Point", "Current_Pain"],
        "right_keys": ["Solution", "Value_Proposition"],
        "hint": "请补清：用户现在怎么做、哪里痛、你的方案到底改变了什么。",
    },
    "R4": {
        "dimension": "合规要求 × 执行链路",
        "left_keys": ["Industry", "Data_Source", "Policy_Constraints"],
        "right_keys": ["Tech_Route", "Delivery_Method", "Revenue_Model"],
        "hint": "请补充：哪条合规要求，影响哪个执行动作或收费动作。",
    },
    "R5": {
        "dimension": "闭环要素覆盖度",
        "left_keys": ["Target_Customer", "Value_Proposition"],
        "right_keys": ["Marketing_Channel", "Revenue_Model", "Cost_Structure"],
        "hint": "请至少补齐商业闭环中的渠道、收入或成本一侧。",
    },
    "R6": {
        "dimension": "目标客户 × 营销渠道",
        "left_keys": ["Target_Customer", "Customer_Type"],
        "right_keys": ["Marketing_Channel"],
        "hint": "请说明：这个渠道为什么能有效触达你的目标用户。",
    },
    "R7": {
        "dimension": "痛点强度 × 支付能力/价格",
        "left_keys": ["Core_Pain_Point", "Current_Pain"],
        "right_keys": ["Disposable_Income", "Price", "Unit_Price"],
        "hint": "请补充：谁付钱、为什么愿意付、价格锚点是什么。",
    },
    "R8": {
        "dimension": "痛点 × 替代方案/竞品",
        "left_keys": ["Core_Pain_Point", "Current_Pain"],
        "right_keys": ["Alternative_Solution", "Competitor_Pool"],
        "hint": "请至少说清：用户不用你时现在靠什么解决问题。",
    },
    "R9": {
        "dimension": "TAM/SAM/SOM 漏斗",
        "left_keys": ["TAM", "SAM"],
        "right_keys": ["SOM", "Marketing_Budget"],
        "hint": "请保证 TAM ≥ SAM ≥ SOM，并说明每一层筛选口径。",
    },
    "R10": {
        "dimension": "差异化 × 可验证指标/竞品",
        "left_keys": ["Differentiation", "Value_Proposition"],
        "right_keys": ["Verifiable_Metric", "Control_Experiment", "Competitor_Pool"],
        "hint": "请补充：和谁比、比什么指标、提升了多少。",
    },
    "R11": {
        "dimension": "LTV × CAC",
        "left_keys": ["LTV"],
        "right_keys": ["CAC"],
        "hint": "请至少给出 LTV 与 CAC 的粗算值，再谈规模化。",
    },
    "R12": {
        "dimension": "价格 × 成本",
        "left_keys": ["Price", "Unit_Price"],
        "right_keys": ["Fixed_Cost", "Variable_Cost"],
        "hint": "请至少补一条：单位履约成本、渠道成本或固定成本分摊。",
    },
    "R13": {
        "dimension": "账期 × 现金缓冲",
        "left_keys": ["Account_Period"],
        "right_keys": ["Startup_Capital", "Burn_Rate"],
        "hint": "请补充：账期多久、月 burn 多少、资金能撑多久。",
    },
    "R14": {
        "dimension": "产品形态/交付 × 供应网络",
        "left_keys": ["Product_Form", "Delivery_Method"],
        "right_keys": ["Fulfill_Cost", "Supplier_Network"],
        "hint": "请说明：谁供货、谁履约、单位交付成本是多少。",
    },
    "R15": {
        "dimension": "平台模式/种子用户 × 冷启动",
        "left_keys": ["Platform_Model", "Seed_Users"],
        "right_keys": ["Cold_Start_Strategy", "Marketing_Channel"],
        "hint": "请补清：前 50~100 个用户从哪来，靠什么留下。",
    },
    "R16": {
        "dimension": "TRL/技术路线 × 团队背景",
        "left_keys": ["TRL", "Tech_Route"],
        "right_keys": ["Team_Background"],
        "hint": "请说明：谁负责关键技术，是否有外部合作方。",
    },
    "R17": {
        "dimension": "资源清单 × 里程碑计划",
        "left_keys": ["Resource_List", "Tech_Route"],
        "right_keys": ["Milestone_Plan"],
        "hint": "请补充：30/60/90 天分别做什么、验证什么、谁负责。",
    },
    "R18": {
        "dimension": "财务模型 × 关键假设",
        "left_keys": ["Financial_Model"],
        "right_keys": ["Key_Assumption", "Sensitivity_Analysis"],
        "hint": "请至少补一条：如果转化率/客单价/复购率下降，会发生什么。",
    },
    "R19": {
        "dimension": "使用频次 × 收费方式",
        "left_keys": ["Usage_Frequency"],
        "right_keys": ["Revenue_Model", "Unit_Price"],
        "hint": "请补清：用户多久使用一次，你打算按什么频率收费。",
    },
    "R20": {
        "dimension": "社会价值 × 商业转化",
        "left_keys": ["Scenario_Research", "Pilot_Cooperation"],
        "right_keys": ["Revenue_Model", "Translation_Roadmap"],
        "hint": "请补清：从社会价值/试点走向商业可持续的桥梁是什么。",
    },

    # ========== Public welfare ==========
    "PR1": {
        "dimension": "受益对象 × 服务场景",
        "left_keys": ["Beneficiary_Group"],
        "right_keys": ["Service_Scenario", "Urgency_Pain"],
        "hint": "请补清：到底服务谁，在什么场景下发生问题。",
    },
    "PR2": {
        "dimension": "需求证据 × 问题严重度",
        "left_keys": ["Research_Sample", "Field_Observation", "Needs_Quote"],
        "right_keys": ["Problem_Severity"],
        "hint": "请补充：样本、观察、引述或问题严重度中的任意两项。",
    },
    "PR3": {
        "dimension": "需求证据 × 干预方案",
        "left_keys": ["Problem_Severity", "Needs_Quote", "Field_Observation"],
        "right_keys": ["Intervention_Solution", "Core_Service", "Expected_Outcome"],
        "hint": "请说明：哪一个真实需求，对应哪一个服务动作。",
    },
    "PR4": {
        "dimension": "服务对象 × 协同方",
        "left_keys": ["Beneficiary_Group", "Service_Scenario"],
        "right_keys": ["Government_Link", "NGO_Partner", "Community_Leader", "Volunteer_Source"],
        "hint": "请补清：谁和你一起做，协同发生在哪个场景。",
    },
    "PR5": {
        "dimension": "受益对象 × 伦理保护",
        "left_keys": ["Beneficiary_Group", "Vulnerable_Group"],
        "right_keys": ["Ethical_Risk", "Privacy_Protection", "Consent_Process"],
        "hint": "请补一句：项目如何处理隐私、知情同意或弱势群体保护。",
    },
    "PR6": {
        "dimension": "筹资来源 × 筹资渠道",
        "left_keys": ["Funding_Source", "Donation_Product"],
        "right_keys": ["Grant_Channel", "Revenue_Supplement"],
        "hint": "请补一个主要资金来源，和一个可执行的获得渠道。",
    },
    "PR7": {
        "dimension": "服务成本 × 资金效率",
        "left_keys": ["Single_Service_Cost", "Management_Cost"],
        "right_keys": ["Fund_Use_Ratio", "Budget_Ceiling"],
        "hint": "请补一个成本口径和一个资金使用效率口径。",
    },
    "PR8": {
        "dimension": "影响目标 × 指标/评估方法",
        "left_keys": ["Impact_Goal", "Expected_Outcome"],
        "right_keys": ["Indicator_System", "Baseline_Data", "Evaluation_Method"],
        "hint": "请补清：要改变什么，用什么指标衡量，怎么评估。",
    },
    "PR9": {
        "dimension": "触达路径 × 留存/转介",
        "left_keys": ["Reach_Channel", "Participation_Motivation"],
        "right_keys": ["Retention_Mechanism", "Referral_Path"],
        "hint": "请补清：怎么找到人、怎么让人参与、怎么留住人。",
    },
    "PR10": {
        "dimension": "筹资/服务 × 公示/背书",
        "left_keys": ["Funding_Source", "Core_Service"],
        "right_keys": ["Disclosure_Frequency", "Financial_Disclosure", "Third_Party_Endorsement", "Story_Evidence"],
        "hint": "请补一个公示机制，或一个第三方背书。",
    },
    "PR11": {
        "dimension": "试点结果 × 复制扩散",
        "left_keys": ["Pilot_Site", "Pilot_Result"],
        "right_keys": ["Replication_Condition", "Expansion_Path"],
        "hint": "请补清：试点证明了什么，怎样复制到更多场景。",
    },
    "PR12": {
        "dimension": "志愿者角色 × 培训/调度",
        "left_keys": ["Volunteer_Role"],
        "right_keys": ["Training_Process", "Scheduling_Mechanism", "Incentive_NonCash"],
        "hint": "如果项目依赖志愿者，请补清角色、培训或排班中的任意两项。",
    },
    "PR13": {
        "dimension": "关键资源 × 替代/缓冲",
        "left_keys": ["Key_Resource", "Resource_Gap"],
        "right_keys": ["Replacement_Plan", "Risk_Buffer"],
        "hint": "请补一个关键资源，以及失效时的替代/缓冲方案。",
    },
    "PR14": {
        "dimension": "政策依据 × 资质/安全边界",
        "left_keys": ["Policy_Basis"],
        "right_keys": ["Qualification_Requirement", "Safety_Redline", "Public_Opinion_Risk"],
        "hint": "请补一个政策依据，和一个执行边界（资质/安全/舆情）。",
    },
    "PR15": {
        "dimension": "合作伙伴 × 长期共创",
        "left_keys": ["Enterprise_Partner", "School_Hospital_Community"],
        "right_keys": ["CoCreation_Mode", "Longterm_Mechanism"],
        "hint": "请补清：和谁长期合作，以什么机制持续共创。",
    },
}

RULE_EDGE_BINDINGS = {
    "R1": ["Core_Business_Loop"],
    "R2": ["Tech_Barrier", "Core_Business_Loop"],
    "R3": ["Narrative_Causality"],
    "R4": ["Compliance_Ethics", "Core_Business_Loop"],
    "R5": ["Core_Business_Loop"],
    "R6": ["Channel_Physical_Access", "Core_Business_Loop"],
    "R7": ["Willingness_To_Pay"],
    "R8": ["Real_Competition"],
    "R9": ["Market_Reachability"],
    "R10": ["Innovation_Verification", "Real_Competition"],
    "R11": ["Unit_Economics"],
    "R12": ["Pricing_Space"],
    "R13": ["Cash_Flow_Health"],
    "R14": ["Supply_Chain_Sync"],
    "R15": ["Cold_Start_Engine"],
    "R16": ["R&D_Team_Match"],
    "R17": ["Resource_Feasibility"],
    "R18": ["Financial_Reasonableness"],
    "R19": ["Frequency_Mismatch"],
    "R20": ["Social_Value_Translation"],

    "PR1": ["Public_Welfare_Targeting"],
    "PR2": ["Public_Welfare_Demand_Evidence"],
    "PR3": ["Public_Welfare_Demand_Evidence", "Public_Welfare_Value_Design"],
    "PR4": ["Stakeholder_Collaboration", "Public_Welfare_Targeting"],
    "PR5": ["Public_Welfare_Ethics_Safeguard", "Public_Welfare_Targeting"],
    "PR6": ["Fundraising_Model"],
    "PR7": ["Benefit_Cost_Efficiency"],
    "PR8": ["Impact_Measurement", "Public_Welfare_Value_Design"],
    "PR9": ["Beneficiary_Conversion_Path", "Public_Welfare_Targeting"],
    "PR10": ["Public_Trust_Transparency", "Fundraising_Model"],
    "PR11": ["Pilot_Replication"],
    "PR12": ["Volunteer_Operations"],
    "PR13": ["Resource_Sustainability"],
    "PR14": ["Policy_Compliance_Public"],
    "PR15": ["Social_Value_CoCreation", "Pilot_Replication"],
}


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _display_key_label(key: str | None) -> str:
    return KEY_LABELS.get(str(key or "").strip(), str(key or "").strip() or "待补字段")


def _normalize_node_token(raw: str) -> Tuple[str, str]:
    raw = _normalize_text(raw)
    if not raw:
        return "", ""
    if ":" in raw:
        key, value = raw.split(":", 1)
        return key.strip(), value.strip()
    if "：" in raw:
        key, value = raw.split("：", 1)
        return key.strip(), value.strip()
    return raw.strip(), raw.strip()


def _extract_field_values(extracted_edges: Dict[str, List[str]] | None) -> Dict[str, List[str]]:
    extracted_edges = extracted_edges or {}
    field_values: Dict[str, List[str]] = {}
    for _, nodes in extracted_edges.items():
        for node in nodes or []:
            key, value = _normalize_node_token(str(node))
            if not key:
                continue
            field_values.setdefault(key, [])
            if value and value not in field_values[key]:
                field_values[key].append(value)
    return field_values


def _pick_first(field_values: Dict[str, List[str]], keys: List[str]) -> Tuple[str, str]:
    for key in keys:
        values = field_values.get(key) or []
        if values:
            return key, str(values[0]).strip()
    return (keys[0] if keys else ""), "(待补充)"


def _parse_number(text: str) -> float | None:
    text = _normalize_text(text).replace(",", "")
    if not text or text == "(待补充)":
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    if not m:
        return None
    try:
        return float(m.group(0))
    except Exception:
        return None


def _contains_any(text: str, words: List[str]) -> bool:
    text = _normalize_text(text).lower()
    return any(w.lower() in text for w in words if str(w).strip())


def _severity(rule_id: str, fallback: str = "medium") -> str:
    return RULE_DEFAULT_SEVERITY.get(rule_id, fallback)


def _build_check(
    *,
    check_id: str,
    dimension: str,
    rule_id: str,
    left_key: str,
    left_value: str,
    right_key: str,
    right_value: str,
    status: str,
    severity: str,
    reason: str,
    evidence_hint: str,
    structural_hit_fields: List[str] | None = None,
) -> Dict[str, Any]:
    return {
        "id": check_id,
        "dimension": dimension,
        "rule_id": rule_id,
        "left_key": left_key,
        "left_value": left_value,
        "right_key": right_key,
        "right_value": right_value,
        "status": status,
        "severity": severity,
        "reason": reason,
        "evidence_hint": evidence_hint,
        "structural_hit_fields": structural_hit_fields or [],
    }


def _best_status(a: str, b: str) -> str:
    return a if STATUS_RANK.get(a, 0) >= STATUS_RANK.get(b, 0) else b


def _worst_status_of_checks(checks: List[Dict[str, Any]]) -> str:
    worst = "unknown"
    for item in checks:
        worst = _best_status(worst, str(item.get("status") or "unknown"))
    return worst


def _rule_hit_fields(rule_id: str, field_values: Dict[str, List[str]]) -> List[str]:
    spec = RULE_SPECS.get(rule_id) or {}
    hits = []
    for key in list(spec.get("left_keys", [])) + list(spec.get("right_keys", [])):
        if field_values.get(key):
            hits.append(f"{_display_key_label(key)}：{field_values[key][0]}")
    return hits[:6]


def _package_semantic_report(
    checks: List[Dict[str, Any]],
    field_values: Dict[str, List[str]],
    source_text: str,
    extracted_edges: Dict[str, List[str]],
) -> Dict[str, Any]:
    checks = sorted(
        checks,
        key=lambda item: (
            -STATUS_RANK.get(str(item.get("status") or "unknown"), 0),
            -SEVERITY_RANK.get(str(item.get("severity") or "low"), 0),
            str(item.get("rule_id") or ""),
            str(item.get("id") or ""),
        )
    )

    by_rule: Dict[str, Dict[str, Any]] = {}
    for item in checks:
        rule_id = str(item.get("rule_id") or "")
        if not rule_id:
            continue
        current = by_rule.get(rule_id)
        candidate_status = str(item.get("status") or "unknown")
        if current is None or STATUS_RANK.get(candidate_status, 0) > STATUS_RANK.get(current.get("worst_status", "unknown"), 0):
            by_rule[rule_id] = {
                "rule_id": rule_id,
                "worst_status": candidate_status,
                "severity": item.get("severity") or "medium",
                "dimension": item.get("dimension") or RULE_NAMES.get(rule_id, rule_id),
            }

    risky_count = len([item for item in checks if str(item.get("status") or "") in {"contradictory", "suspicious"}])
    needs_evidence_count = len([item for item in checks if str(item.get("status") or "") == "needs_evidence"])
    confirmed_count = len([item for item in checks if str(item.get("status") or "") == "confirmed"])

    return {
        "checks": checks,
        "summary": {
            "total_checks": len(checks),
            "risky_count": risky_count,
            "needs_evidence_count": needs_evidence_count,
            "confirmed_count": confirmed_count,
            "by_rule": by_rule,
        },
        "field_values": field_values,
        "source_text": source_text,
        "extracted_edges": extracted_edges,
    }


def build_structural_field_notes(
    extracted_edges: Dict[str, List[str]] | None,
    *,
    stage_rule_ids: Iterable[str] | None = None,
    source_text: str = "",
) -> List[Dict[str, Any]]:
    extracted_edges = extracted_edges or {}
    field_values = _extract_field_values(extracted_edges)
    target_rule_ids = [str(item).strip() for item in (stage_rule_ids or []) if str(item).strip()]

    notes = []
    for rule_id in target_rule_ids:
        spec = RULE_SPECS.get(rule_id)
        if not spec:
            continue

        left_key, left_value = _pick_first(field_values, list(spec.get("left_keys", [])))
        right_key, right_value = _pick_first(field_values, list(spec.get("right_keys", [])))

        left_missing = left_value == "(待补充)"
        right_missing = right_value == "(待补充)"
        if not left_missing and not right_missing:
            continue

        if left_missing and right_missing:
            issue = (
                f"该规则的结构关联可能已经出现，但当前还没标准化写出“{_display_key_label(left_key)}”与“{_display_key_label(right_key)}”两侧字段。"
                f" 这不会直接否掉结构判定，但会降低语义复核置信度。"
            )
        elif left_missing:
            issue = (
                f"该规则结构已形成，但“{_display_key_label(left_key)}”这一侧字段还不够明确。"
                f" 这不会直接否掉结构判定，但会降低语义复核置信度。"
            )
        else:
            issue = (
                f"该规则结构已形成，但“{_display_key_label(right_key)}”这一侧字段还不够明确。"
                f" 这不会直接否掉结构判定，但会降低语义复核置信度。"
            )

        notes.append({
            "rule": rule_id,
            "name": RULE_NAMES.get(rule_id, rule_id),
            "issue": issue,
            "severity": "medium",
            "left_key": left_key,
            "left_value": left_value,
            "right_key": right_key,
            "right_value": right_value,
        })
    return notes


build_structural_field_alerts = build_structural_field_notes


def _contextual_reason_generic(rule_id: str, left_value: str, right_value: str) -> Tuple[str, str, str]:
    if left_value == "(待补充)" and right_value == "(待补充)":
        return (
            "needs_evidence",
            "medium",
            "两侧关键字段都还未标准化表达，当前无法稳定完成语义复核。",
        )
    if left_value == "(待补充)" or right_value == "(待补充)":
        return (
            "needs_evidence",
            "medium",
            "一侧关键字段仍缺失，当前只能做弱语义判断，建议先补关键表达。",
        )
    return (
        "confirmed",
        _severity(rule_id, "medium"),
        "两侧关键字段均已出现，当前语义上能够形成基本对应关系。",
    )


def _eval_rule(rule_id: str, field_values: Dict[str, List[str]], source_text: str = "") -> List[Dict[str, Any]]:
    spec = RULE_SPECS.get(rule_id)
    if not spec:
        return []

    left_key, left_value = _pick_first(field_values, list(spec["left_keys"]))
    right_key, right_value = _pick_first(field_values, list(spec["right_keys"]))
    dimension = str(spec["dimension"])
    hint = str(spec["hint"])
    structural_hit_fields = _rule_hit_fields(rule_id, field_values)

    status, severity, reason = _contextual_reason_generic(rule_id, left_value, right_value)
    src = _normalize_text(source_text).lower()

    # ---------- Commercial targeted refinements ----------
    if rule_id == "R1":
        if left_value == "(待补充)" and right_value == "(待补充)":
            status, severity, reason = "suspicious", "high", "当前既没有清晰的目标客户/价值主张，也没有收入/成本闭环，整体商业链路仍偏散。"
    elif rule_id == "R2":
        if left_value != "(待补充)" and right_value != "(待补充)":
            if not (_contains_any(left_value, ["降本", "效率", "准确", "壁垒", "算法", "专利", "技术"]) or _contains_any(right_value, ["技术", "壁垒", "优势", "价值", "收入"])):
                status, severity, reason = "needs_evidence", "medium", "技术路线和商业闭环都出现了，但还没看清技术究竟如何变成用户价值或收费优势。"
    elif rule_id == "R3":
        if left_value == "(待补充)" or right_value == "(待补充)":
            status, severity, reason = "needs_evidence", "high", "痛点或解决方案仍未说清，因果链难以成立。"
        elif _contains_any(right_value, ["平台", "系统", "app", "小程序", "模型"]) and not _contains_any(left_value, ["慢", "贵", "难", "低效", "损失", "风险", "焦虑", "麻烦"]):
            status, severity, reason = "suspicious", "high", "当前更像是在报功能名，还没有把方案直接钉到真实痛点上。"
    elif rule_id == "R6":
        if left_value != "(待补充)" and right_value != "(待补充)":
            if _contains_any(left_value, ["老人", "儿童", "农户", "企业"]) and _contains_any(right_value, ["抖音", "小红书", "公众号", "社群", "地推", "渠道"]):
                status, severity, reason = "confirmed", "medium", "客群与渠道表达基本可配对，具备进一步验证条件。"
    elif rule_id == "R7":
        price_num = _parse_number(right_value)
        if left_value != "(待补充)" and right_value != "(待补充)" and price_num is not None and price_num > 100000:
            status, severity, reason = "suspicious", "high", "当前价格表达过高，但缺少足够强的付费理由或支付方说明。"
    elif rule_id == "R9":
        tam = _parse_number(" ".join(field_values.get("TAM", [])) or "")
        sam = _parse_number(" ".join(field_values.get("SAM", [])) or "")
        som = _parse_number(" ".join(field_values.get("SOM", [])) or "")
        if tam is not None and sam is not None and som is not None:
            if not (tam >= sam >= som):
                status, severity, reason = "contradictory", "high", "TAM/SAM/SOM 的口径顺序不成立，市场漏斗存在明显冲突。"
            else:
                status, severity, reason = "confirmed", "medium", "市场漏斗顺序基本成立。"
        else:
            status, severity, reason = "needs_evidence", "medium", "市场漏斗字段还不完整，建议至少补齐 TAM/SAM/SOM 三层中的两层以上。"
    elif rule_id == "R11":
        ltv = _parse_number(left_value)
        cac = _parse_number(right_value)
        if ltv is None or cac is None:
            status, severity, reason = "needs_evidence", "high", "LTV 或 CAC 尚未量化，暂时无法判断单位经济是否成立。"
        elif ltv < cac:
            status, severity, reason = "contradictory", "critical", "当前 LTV 低于 CAC，单位经济不成立。"
        elif ltv < cac * 1.2:
            status, severity, reason = "suspicious", "high", "虽然 LTV 略高于 CAC，但安全边际很薄。"
        else:
            status, severity, reason = "confirmed", "high", "LTV 与 CAC 的关系基本健康。"
    elif rule_id == "R12":
        price_num = _parse_number(left_value)
        cost_values = [
            _parse_number(v)
            for k in ["Fixed_Cost", "Variable_Cost"]
            for v in field_values.get(k, [])
        ]
        cost_values = [v for v in cost_values if v is not None]
        if price_num is None or not cost_values:
            status, severity, reason = "needs_evidence", "high", "价格或成本项未写清，利润空间还无法判断。"
        elif price_num < max(cost_values):
            status, severity, reason = "suspicious", "high", "当前价格低于已写出的主要成本项，利润空间存在风险。"
    elif rule_id == "R13":
        account = _parse_number(left_value)
        startup = _parse_number(" ".join(field_values.get("Startup_Capital", [])) or "")
        burn = _parse_number(" ".join(field_values.get("Burn_Rate", [])) or "")
        if account is None or startup is None or burn is None:
            status, severity, reason = "needs_evidence", "high", "账期、启动资金或 burn 率有缺口，现金流风险无法完整判断。"
        elif burn > 0 and startup / burn < 3:
            status, severity, reason = "suspicious", "critical", "按当前资金与 burn 速度估算，现金缓冲偏短。"
    elif rule_id == "R19":
        if left_value != "(待补充)" and right_value != "(待补充)":
            low_freq = _contains_any(left_value, ["低频", "偶尔", "一年", "半年", "季"])
            sub_model = _contains_any(right_value, ["订阅", "包月", "会员", "年费"])
            if low_freq and sub_model:
                status, severity, reason = "suspicious", "high", "当前场景偏低频，但收费方式像高频订阅，存在错配风险。"

    # ---------- Public welfare targeted refinements ----------
    elif rule_id == "PR1":
        if left_value == "(待补充)" or right_value == "(待补充)":
            status, severity, reason = "needs_evidence", "high", "受益对象或服务场景还没说清，公益边界仍然偏模糊。"
    elif rule_id == "PR2":
        evidence_count = sum(
            1 for k in ["Research_Sample", "Field_Observation", "Needs_Quote", "Problem_Severity"]
            if field_values.get(k)
        )
        if evidence_count <= 1:
            status, severity, reason = "needs_evidence", "high", "需求证据仍偏少，至少补样本、观察、引述、严重度中的任意两项。"
        elif evidence_count >= 2:
            status, severity, reason = "confirmed", "medium", "需求证据已有基本支撑。"
    elif rule_id == "PR3":
        demand_text = " ".join(
            (field_values.get("Problem_Severity") or [])
            + (field_values.get("Needs_Quote") or [])
            + (field_values.get("Field_Observation") or [])
        )
        service_text = " ".join(
            (field_values.get("Intervention_Solution") or [])
            + (field_values.get("Core_Service") or [])
            + (field_values.get("Expected_Outcome") or [])
        )
        if not demand_text or not service_text:
            status, severity, reason = "needs_evidence", "high", "需求证据和干预方案还没有同时写清，无法判断是否贴着真实问题。"
        elif _contains_any(service_text, ["活动", "宣传", "平台"]) and not _contains_any(demand_text, ["失学", "孤独", "康复", "照护", "焦虑", "抑郁", "困难", "复诊", "随访", "安全"]):
            status, severity, reason = "suspicious", "high", "当前方案更像通用动作，还没看出它如何精确回应已识别的真实问题。"
        else:
            status, severity, reason = "confirmed", "medium", "需求与方案之间已形成基本对应。"
    elif rule_id == "PR5":
        if left_value != "(待补充)" and right_value == "(待补充)":
            status, severity, reason = "needs_evidence", "medium", "既然面向明确受益对象，建议至少补一句隐私、知情同意或弱势群体保护措施。"
    elif rule_id == "PR6":
        if left_value == "(待补充)" and right_value == "(待补充)":
            status, severity, reason = "suspicious", "high", "当前完全没有形成筹资路径，公益项目难以持续运行。"
    elif rule_id == "PR7":
        cost = _parse_number(" ".join(field_values.get("Single_Service_Cost", [])) or "")
        ratio = _parse_number(" ".join(field_values.get("Fund_Use_Ratio", [])) or "")
        if cost is None and ratio is None:
            status, severity, reason = "needs_evidence", "medium", "成本和资金效率两侧都还缺口较大。"
    elif rule_id == "PR8":
        metric_count = sum(
            1 for k in ["Impact_Goal", "Indicator_System", "Baseline_Data", "Evaluation_Method"]
            if field_values.get(k)
        )
        if metric_count <= 1:
            status, severity, reason = "needs_evidence", "high", "影响评估还没有形成可验证框架，建议至少补目标+指标或指标+方法。"
        else:
            status, severity, reason = "confirmed", "medium", "影响评估结构已具备基本可验证性。"
    elif rule_id == "PR9":
        if left_value == "(待补充)" and right_value == "(待补充)":
            status, severity, reason = "needs_evidence", "medium", "触达、参与、留存、转介这条路径还没建立起来。"
    elif rule_id == "PR10":
        if left_value != "(待补充)" and right_value == "(待补充)":
            status, severity, reason = "needs_evidence", "medium", "当前已有筹资/服务，但公示、披露或第三方背书还不够。"
    elif rule_id == "PR11":
        if left_value == "(待补充)" or right_value == "(待补充)":
            status, severity, reason = "needs_evidence", "high", "试点结果或复制扩散路径仍不完整，暂时还无法判断能否规模复制。"
    elif rule_id == "PR12":
        if left_value != "(待补充)" and right_value == "(待补充)":
            status, severity, reason = "needs_evidence", "low", "如果项目依赖志愿者，建议进一步补培训、排班或激励机制。"
    elif rule_id == "PR13":
        if left_value != "(待补充)" and right_value == "(待补充)":
            status, severity, reason = "needs_evidence", "medium", "关键资源已经写到，但缺替代方案或风险缓冲。"
    elif rule_id == "PR14":
        if left_value == "(待补充)" or right_value == "(待补充)":
            status, severity, reason = "needs_evidence", "high", "政策依据或执行边界仍不够完整，合规落地风险无法充分排查。"
    elif rule_id == "PR15":
        if left_value != "(待补充)" and right_value == "(待补充)":
            status, severity, reason = "needs_evidence", "low", "合作伙伴已出现，但长期共创机制还不够清楚。"

    return [
        _build_check(
            check_id=f"{rule_id.lower()}::0",
            dimension=dimension,
            rule_id=rule_id,
            left_key=left_key,
            left_value=left_value,
            right_key=right_key,
            right_value=right_value,
            status=status,
            severity=severity,
            reason=reason,
            evidence_hint=hint,
            structural_hit_fields=structural_hit_fields,
        )
    ]


def _aggregate_alerts(checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in checks:
        rule_id = str(item.get("rule_id") or "").strip()
        if not rule_id:
            continue
        grouped.setdefault(rule_id, []).append(item)

    results = []
    for rule_id, items in grouped.items():
        worst = sorted(
            items,
            key=lambda x: (
                -STATUS_RANK.get(str(x.get("status") or "unknown"), 0),
                -SEVERITY_RANK.get(str(x.get("severity") or "low"), 0),
            )
        )[0]
        status = str(worst.get("status") or "needs_evidence")
        status_label = {
            "contradictory": "语义冲突",
            "suspicious": "语义存疑",
            "needs_evidence": "待补证",
            "confirmed": "语义通过",
            "unknown": "语义未知",
        }.get(status, "语义存疑")

        results.append({
            "rule": rule_id,
            "name": RULE_NAMES.get(rule_id, rule_id),
            "issue": (
                f"{status_label}：{_display_key_label(worst.get('left_key'))}={worst.get('left_value')} "
                f"× {_display_key_label(worst.get('right_key'))}={worst.get('right_value')}。{worst.get('reason')}"
            ),
            "severity": worst.get("severity") or _severity(rule_id, "medium"),
            "left_key": worst.get("left_key"),
            "left_value": worst.get("left_value"),
            "right_key": worst.get("right_key"),
            "right_value": worst.get("right_value"),
        })
    return results


def _build_contextual_missing_semantic_check(
    rule_id: str,
    field_values: Dict[str, List[str]],
    source_text: str = "",
) -> Dict[str, Any]:
    spec = RULE_SPECS.get(rule_id, {})
    left_key = (spec.get("left_keys") or [""])[0]
    right_key = (spec.get("right_keys") or [""])[0]
    return _build_check(
        check_id=f"{rule_id.lower()}::missing",
        dimension=str(spec.get("dimension") or RULE_NAMES.get(rule_id, rule_id)),
        rule_id=rule_id,
        left_key=left_key,
        left_value="(待补充)",
        right_key=right_key,
        right_value="(待补充)",
        status="needs_evidence",
        severity="medium",
        reason="该规则在结构上已达成，但当前还没有足够的标准字段可供稳定完成语义复核。",
        evidence_hint=str(spec.get("hint") or "请补充该规则对应的关键表达。"),
        structural_hit_fields=_rule_hit_fields(rule_id, field_values),
    )


def _compact_stage_semantic_checks(checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    compacted: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for item in checks or []:
        rule_id = str(item.get("rule_id") or "")
        dimension = str(item.get("dimension") or "")
        key = (rule_id, dimension)
        existing = compacted.get(key)
        if existing is None:
            compacted[key] = item
            continue
        current_status = str(item.get("status") or "unknown")
        existing_status = str(existing.get("status") or "unknown")
        if STATUS_RANK.get(current_status, 0) > STATUS_RANK.get(existing_status, 0):
            compacted[key] = item
    return list(compacted.values())


def filter_semantic_report_by_rule_ids(
    semantic_report: Dict[str, Any] | None,
    allowed_rule_ids: Iterable[str] | None,
) -> Dict[str, Any]:
    semantic_report = semantic_report or {}
    allowed = {str(item).strip() for item in (allowed_rule_ids or []) if str(item).strip()}
    checks = list(semantic_report.get("checks") or [])
    if allowed:
        checks = [item for item in checks if str(item.get("rule_id") or "") in allowed]

    return _package_semantic_report(
        checks,
        semantic_report.get("field_values") or {},
        semantic_report.get("source_text") or "",
        semantic_report.get("extracted_edges") or {},
    )


def build_stage_semantic_report(
    semantic_report: Dict[str, Any] | None,
    *,
    stage_rule_ids: Iterable[str] | None = None,
    structurally_passed_rule_ids: Iterable[str] | None = None,
    fill_missing_for_passed_rules: bool = True,
    source_text: str = "",
) -> Dict[str, Any]:
    semantic_report = semantic_report or {}
    filtered = filter_semantic_report_by_rule_ids(semantic_report, stage_rule_ids)
    checks = list(filtered.get("checks") or [])

    if structurally_passed_rule_ids is not None:
        passed = {str(item).strip() for item in (structurally_passed_rule_ids or []) if str(item).strip()}
        checks = [item for item in checks if str(item.get("rule_id") or "") in passed]

        if fill_missing_for_passed_rules and passed:
            existing_rule_ids = {str(item.get("rule_id") or "") for item in checks if str(item.get("rule_id") or "").strip()}
            for rule_id in sorted(passed):
                if rule_id in SEMANTIC_CAPABLE_RULE_IDS and rule_id not in existing_rule_ids:
                    checks.append(
                        _build_contextual_missing_semantic_check(
                            rule_id,
                            semantic_report.get("field_values") or {},
                            source_text or semantic_report.get("source_text") or "",
                        )
                    )

    checks = _compact_stage_semantic_checks(checks)

    return _package_semantic_report(
        checks,
        semantic_report.get("field_values") or {},
        source_text or semantic_report.get("source_text") or "",
        semantic_report.get("extracted_edges") or {},
    )


def build_blocking_semantic_alerts(semantic_report: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    semantic_report = semantic_report or {}
    blocking_checks = [
        item for item in (semantic_report.get("checks") or [])
        if str(item.get("status") or "") in SEMANTIC_BLOCKING_STATUSES
    ]
    return _aggregate_alerts(blocking_checks)


def evaluate_hyperedge_semantics(
    extracted_edges: Dict[str, List[str]] | None,
    *,
    source_text: str = "",
) -> Dict[str, Any]:
    extracted_edges = extracted_edges or {}
    field_values = _extract_field_values(extracted_edges)

    checks: List[Dict[str, Any]] = []
    for rule_id in sorted(SEMANTIC_CAPABLE_RULE_IDS):
        checks.extend(_eval_rule(rule_id, field_values, source_text))

    return _package_semantic_report(
        checks,
        field_values,
        source_text,
        extracted_edges,
    )