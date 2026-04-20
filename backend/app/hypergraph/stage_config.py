from __future__ import annotations

from typing import Dict, List

PROJECT_TYPE_COMMERCIAL = "commercial"
PROJECT_TYPE_PUBLIC_WELFARE = "public_welfare"

PUBLIC_WELFARE_KEYWORDS = [
    "公益", "公益性", "社会价值", "社会效益", "助农", "乡村振兴", "帮扶", "扶困", "扶弱", "弱势群体",
    "公共利益", "公益组织", "基金会", "慈善", "捐赠", "志愿者", "社区服务", "普惠", "社会问题", "社会创新",
    "非营利", "ngo", "npo", "csr", "政府购买服务", "民生", "残障", "留守", "养老", "支教", "环保公益",
]

PUBLIC_WELFARE_EDGE_NAMES = {
    "Public_Welfare_Targeting",
    "Public_Welfare_Demand_Evidence",
    "Public_Welfare_Value_Design",
    "Stakeholder_Collaboration",
    "Public_Welfare_Ethics_Safeguard",
    "Fundraising_Model",
    "Benefit_Cost_Efficiency",
    "Impact_Measurement",
    "Beneficiary_Conversion_Path",
    "Public_Trust_Transparency",
    "Pilot_Replication",
    "Volunteer_Operations",
    "Resource_Sustainability",
    "Policy_Compliance_Public",
    "Social_Value_CoCreation",
}

RULE_METADATA: Dict[str, Dict[str, object]] = {
    "System": {"name": "图谱元素过少", "severity": "high", "weight": 18},
    "R1": {"name": "全局逻辑散架", "severity": "critical", "weight": 30},
    "R2": {"name": "技术与商业双轨孤岛", "severity": "critical", "weight": 30},
    "R3": {"name": "叙事因果断裂", "severity": "high", "weight": 18},
    "R4": {"name": "合规逻辑游离", "severity": "medium", "weight": 10},
    "R5": {"name": "闭环要素严重缺失", "severity": "high", "weight": 18},
    "R6": {"name": "渠道与客群脱节", "severity": "medium", "weight": 10},
    "R7": {"name": "支付意愿支撑不足", "severity": "high", "weight": 18},
    "R8": {"name": "无竞争对手幻觉", "severity": "critical", "weight": 30},
    "R9": {"name": "市场漏斗断层", "severity": "medium", "weight": 10},
    "R10": {"name": "创新缺乏竞争对标", "severity": "medium", "weight": 10},
    "R11": {"name": "单位经济模型崩塌", "severity": "critical", "weight": 30},
    "R12": {"name": "利润空间黑盒", "severity": "high", "weight": 18},
    "R13": {"name": "现金流断裂高危", "severity": "critical", "weight": 30},
    "R14": {"name": "供应链脱离业务", "severity": "high", "weight": 18},
    "R15": {"name": "冷启动策略空转", "severity": "medium", "weight": 10},
    "R16": {"name": "技术壁垒无团队支撑", "severity": "medium", "weight": 10},
    "R17": {"name": "执行方案空壳", "severity": "medium", "weight": 10},
    "R18": {"name": "财务预测漂浮", "severity": "high", "weight": 18},
    "R19": {"name": "频次与收入模型错配", "severity": "high", "weight": 18},
    "R20": {"name": "公益属性过重", "severity": "medium", "weight": 10},
    "PR1": {"name": "受益对象界定模糊", "severity": "critical", "weight": 30},
    "PR2": {"name": "公益需求证据薄弱", "severity": "high", "weight": 18},
    "PR3": {"name": "服务设计脱离真实问题", "severity": "critical", "weight": 30},
    "PR4": {"name": "关键协同方缺位", "severity": "high", "weight": 18},
    "PR5": {"name": "伦理保护失焦", "severity": "critical", "weight": 30},
    "PR6": {"name": "筹资路径不成立", "severity": "critical", "weight": 30},
    "PR7": {"name": "公益成本效率黑箱", "severity": "high", "weight": 18},
    "PR8": {"name": "影响评估不可验证", "severity": "critical", "weight": 30},
    "PR9": {"name": "受益者转化路径断裂", "severity": "high", "weight": 18},
    "PR10": {"name": "公信力与透明度不足", "severity": "high", "weight": 18},
    "PR11": {"name": "试点无法复制扩散", "severity": "critical", "weight": 30},
    "PR12": {"name": "志愿者运营失控", "severity": "medium", "weight": 10},
    "PR13": {"name": "关键资源不可持续", "severity": "critical", "weight": 30},
    "PR14": {"name": "政策合规落地风险", "severity": "critical", "weight": 30},
    "PR15": {"name": "社会共创机制悬空", "severity": "medium", "weight": 10},
}

COMMERCIAL_STAGE_DEFINITIONS: List[Dict[str, object]] = [
    {
        "id": "stage_1_core",
        "index": 1,
        "label": "价值主张与客户边界",
        "short_label": "第一阶段",
        "subtitle": "The Core",
        "goal": "先证明你真的知道在替谁解决什么问题，再谈后面的盈利与落地。",
        "coach_hint": "本轮重点不是把产品讲得多高级，而是把用户、场景、痛点、替代方案与价值主张讲清楚；只要你已经拿到一手用户证据，就不应长期卡在第一阶段。",
        "pass_threshold": 75,
        "max_critical_carryover": 1,
        "anchor_min_groups": 3,
        "rule_ids": ["R1", "R3", "R5", "R6", "R8", "R9", "R10"],
        "guardrail_rule_ids": ["System", "R1", "R8"],
        "anchor_groups": [
            {"label": "目标用户", "keys": ["Target_Customer"], "min_hits": 1},
            {"label": "核心痛点", "keys": ["Core_Pain_Point", "Current_Pain"], "min_hits": 1},
            {"label": "价值/方案表达", "keys": ["Value_Proposition", "Solution"], "min_hits": 1},
        ],
        "entry_message": "第一阶段会重点检查：你是否真的说清了目标用户、痛点和价值主张。",
        "milestone_message": "恭喜你突破了第一阶段【价值主张与客户边界】，系统已进入第二阶段【盈利逻辑与生存压力测试】。为了降低后续的对话记忆负担，强烈建议您将当前阶段确认的内容更新到原商业计划书中，并重新点击“更新文档”进行绑定后再继续冲刺！",
    },
    {
        "id": "stage_2_logic",
        "index": 2,
        "label": "盈利逻辑与生存压力测试",
        "short_label": "第二阶段",
        "subtitle": "The Logic",
        "goal": "确认项目不是停留在“有产品就会有人买”的幻觉里，而是具备最基本的盈利与生存意识。",
        "coach_hint": "本轮重点是付费方、定价依据、单位经济和现金流，不再接受“以后再想赚钱”的模糊表达。",
        "pass_threshold": 70,
        "max_critical_carryover": 1,
        "anchor_min_groups": 2,
        "rule_ids": ["R7", "R11", "R12", "R13", "R18", "R19"],
        "guardrail_rule_ids": ["System", "R1", "R8", "R11"],
        "anchor_groups": [
            {"label": "收入/定价表达", "keys": ["Revenue_Model", "Price"], "min_hits": 1},
            {"label": "单位经济", "keys": ["CAC", "LTV", "Fixed_Cost", "Variable_Cost"], "min_hits": 1},
            {"label": "生存压力", "keys": ["Startup_Capital", "Burn_Rate", "Account_Period", "Financial_Model", "Key_Assumption"], "min_hits": 1},
        ],
        "entry_message": "第二阶段会重点检查：谁付钱、为什么愿意付、你不融资能活多久。",
        "milestone_message": "恭喜你突破了第二阶段【盈利逻辑与生存压力测试】，系统已进入第三阶段【资源杠杆与落地可行性】。同样强烈建议您先将本轮结论补充到BP中并重新更新绑定文档，以保持最佳的系统分析上下文！",
    },
    {
        "id": "stage_3_reality",
        "index": 3,
        "label": "资源杠杆与落地可行性",
        "short_label": "第三阶段",
        "subtitle": "The Reality",
        "goal": "判断项目是否具备真实落地条件，而不是只在纸面逻辑上自洽。",
        "coach_hint": "本轮会检查团队、资源、执行、冷启动与合规，逼出你真正的落地路径。",
        "pass_threshold": 70,
        "max_critical_carryover": 1,
        "anchor_min_groups": 2,
        "rule_ids": ["R2", "R4", "R14", "R15", "R16", "R17", "R20"],
        "guardrail_rule_ids": ["System", "R1", "R8", "R11"],
        "anchor_groups": [
            {"label": "团队/技术", "keys": ["Team_Background", "Tech_Route", "TRL"], "min_hits": 1},
            {"label": "资源/里程碑", "keys": ["Resource_List", "Milestone_Plan"], "min_hits": 1},
            {"label": "落地/合规", "keys": ["Supplier_Network", "Fulfill_Cost", "Policy_Constraints", "Pilot_Cooperation", "Translation_Roadmap", "Cold_Start_Strategy"], "min_hits": 1},
        ],
        "entry_message": "第三阶段会重点检查：谁来做、靠什么做、第一步怎么真的跑起来。",
        "milestone_message": "恭喜你完成项目模式三阶段基础逻辑闯关，后续可以继续围绕高危遗留问题做深挖优化。",
    },
]

PUBLIC_WELFARE_STAGE_DEFINITIONS: List[Dict[str, object]] = [
    {
        "id": "public_stage_1_need",
        "index": 1,
        "label": "公益对象识别与社会价值锚定",
        "short_label": "公益第一阶段",
        "subtitle": "Need Fit",
        "goal": "先证明你界定清楚了谁是受益对象、问题到底有多严重、方案是否真的贴着场景设计。",
        "coach_hint": "公益项目第一轮不先谈情怀，要先谈受益者、问题证据、协同方与伦理保护。",
        "pass_threshold": 75,
        "max_critical_carryover": 1,
        "anchor_min_groups": 3,
        "rule_ids": ["PR1", "PR2", "PR3", "PR4", "PR5"],
        "guardrail_rule_ids": ["System", "PR1", "PR3", "PR5"],
        "anchor_groups": [
            {"label": "受益对象", "keys": ["Beneficiary_Group", "Service_Scenario"], "min_hits": 1},
            {"label": "需求证据", "keys": ["Problem_Severity", "Research_Sample", "Field_Observation", "Needs_Quote"], "min_hits": 1},
            {"label": "干预方案", "keys": ["Intervention_Solution", "Expected_Outcome", "Core_Service", "Trust_Mechanism"], "min_hits": 1},
        ],
        "entry_message": "公益第一阶段会重点检查：你是否说清了服务谁、问题证据是什么、方案为何有效。",
        "milestone_message": "恭喜你突破了公益项目第一阶段【公益对象识别与社会价值锚定】，系统已进入第二阶段【公益造血与影响验证】。建议你把当前确认过的受益对象、需求证据和方案骨架同步补回原文档。",
    },
    {
        "id": "public_stage_2_sustainability",
        "index": 2,
        "label": "公益机制与资源协同设计",
        "short_label": "公益第二阶段",
        "subtitle": "Sustainability",
        "goal": "确认项目不是一次性活动，而是具备持续筹资、成本控制、影响评估与公信力机制。",
        "coach_hint": "本轮要回答四件事：钱从哪里来、钱怎么花得值、效果怎么证明、公众为什么持续信任你。",
        "pass_threshold": 70,
        "max_critical_carryover": 1,
        "anchor_min_groups": 2,
        "rule_ids": ["PR6", "PR7", "PR8", "PR9", "PR10"],
        "guardrail_rule_ids": ["System", "PR6", "PR8", "PR10"],
        "anchor_groups": [
            {"label": "筹资/造血", "keys": ["Funding_Source", "Donation_Product", "Grant_Channel", "Revenue_Supplement"], "min_hits": 1},
            {"label": "影响评估", "keys": ["Impact_Goal", "Indicator_System", "Baseline_Data", "Evaluation_Method"], "min_hits": 1},
            {"label": "成本与信任", "keys": ["Single_Service_Cost", "Fund_Use_Ratio", "Financial_Disclosure", "Third_Party_Endorsement"], "min_hits": 1},
        ],
        "entry_message": "公益第二阶段会重点检查：项目如何持续运转，以及如何证明你真的带来了改变。",
        "milestone_message": "恭喜你突破了公益项目第二阶段【公益机制与资源协同设计】，系统已进入第三阶段【复制扩散与长期协同落地】。建议先把筹资、评估、公示机制整理回BP或项目书。",
    },
    {
        "id": "public_stage_3_scale",
        "index": 3,
        "label": "持续运营与规模化扩散",
        "short_label": "公益第三阶段",
        "subtitle": "Scale & Governance",
        "goal": "判断项目能否从单点试点走向长期复制，而不是只停留在一次成功故事。",
        "coach_hint": "本轮会检查试点复制、志愿者运营、资源续航、政策合规与多方共创。",
        "pass_threshold": 70,
        "max_critical_carryover": 1,
        "anchor_min_groups": 2,
        "rule_ids": ["PR11", "PR12", "PR13", "PR14", "PR15"],
        "guardrail_rule_ids": ["System", "PR11", "PR13", "PR14"],
        "anchor_groups": [
            {"label": "复制与扩散", "keys": ["Pilot_Site", "Pilot_Result", "Replication_Condition", "Expansion_Path"], "min_hits": 1},
            {"label": "运营与资源", "keys": ["Volunteer_Role", "Training_Process", "Key_Resource", "Risk_Buffer"], "min_hits": 1},
            {"label": "合规与共创", "keys": ["Policy_Basis", "Qualification_Requirement", "Enterprise_Partner", "CoCreation_Mode", "Longterm_Mechanism"], "min_hits": 1},
        ],
        "entry_message": "公益第三阶段会重点检查：试点能否复制、资源能否续航、协同能否长期成立。",
        "milestone_message": "恭喜你完成公益项目三阶段基础逻辑闯关，后续可继续围绕高危遗留点做深挖优化。",
    },
]

PROJECT_STAGE_DEFINITIONS = COMMERCIAL_STAGE_DEFINITIONS


def infer_project_type_from_stage_flow(stage_flow: Dict[str, object] | None, fallback: str = PROJECT_TYPE_COMMERCIAL) -> str:
    stage_flow = stage_flow or {}
    explicit_type = str(stage_flow.get("project_type") or "").strip()
    if explicit_type in {PROJECT_TYPE_COMMERCIAL, PROJECT_TYPE_PUBLIC_WELFARE}:
        return explicit_type

    current_stage_id = str(stage_flow.get("current_stage_id") or "").strip()
    if current_stage_id.startswith("public_"):
        return PROJECT_TYPE_PUBLIC_WELFARE
    if current_stage_id.startswith("stage_"):
        return PROJECT_TYPE_COMMERCIAL

    for stage_id in (stage_flow.get("stages") or {}).keys():
        stage_id = str(stage_id or "").strip()
        if stage_id.startswith("public_"):
            return PROJECT_TYPE_PUBLIC_WELFARE
        if stage_id.startswith("stage_"):
            return PROJECT_TYPE_COMMERCIAL

    label_text = " ".join([
        str(stage_flow.get("project_type_label") or ""),
        str(stage_flow.get("current_stage_label") or ""),
        str(stage_flow.get("next_stage_label") or ""),
    ]).lower()
    if "公益" in label_text:
        return PROJECT_TYPE_PUBLIC_WELFARE
    if "商业" in label_text:
        return PROJECT_TYPE_COMMERCIAL
    return fallback


def detect_project_type(source_text: str = "", extracted_edges: Dict[str, List[str]] | None = None) -> str:
    text = (source_text or "").lower()
    extracted_edges = extracted_edges or {}
    public_edge_hits = len(PUBLIC_WELFARE_EDGE_NAMES.intersection(set(extracted_edges.keys())))
    keyword_hits = sum(1 for kw in PUBLIC_WELFARE_KEYWORDS if kw.lower() in text)

    if public_edge_hits >= 2:
        return PROJECT_TYPE_PUBLIC_WELFARE
    if keyword_hits >= 2 and not any(edge in extracted_edges for edge in ("Core_Business_Loop", "Unit_Economics", "Pricing_Space", "Cash_Flow_Health")):
        return PROJECT_TYPE_PUBLIC_WELFARE
    if keyword_hits >= 4:
        return PROJECT_TYPE_PUBLIC_WELFARE
    return PROJECT_TYPE_COMMERCIAL


def get_stage_definitions(project_type: str | None = None) -> List[Dict[str, object]]:
    if project_type == PROJECT_TYPE_PUBLIC_WELFARE:
        return PUBLIC_WELFARE_STAGE_DEFINITIONS
    return COMMERCIAL_STAGE_DEFINITIONS


def get_stage_definition(stage_id: str) -> Dict[str, object]:
    for stage in COMMERCIAL_STAGE_DEFINITIONS + PUBLIC_WELFARE_STAGE_DEFINITIONS:
        if stage["id"] == stage_id:
            return stage
    return COMMERCIAL_STAGE_DEFINITIONS[0]
