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
    "R2": "技术与商业双轨孤岛",
    "R3": "叙事因果断裂",
    "R4": "合规逻辑游离",
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


SEMANTIC_CAPABLE_RULE_IDS = {
    'R2', 'R3', 'R4', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15', 'R16', 'R17', 'R18', 'R19', 'R20',
    'PR1', 'PR2', 'PR3', 'PR4', 'PR5', 'PR6', 'PR7', 'PR8', 'PR9', 'PR10', 'PR11', 'PR12', 'PR13', 'PR14', 'PR15'
}

SEMANTIC_BLOCKING_STATUSES = {'contradictory', 'suspicious'}


RULE_DEFAULT_SEVERITY = {
    "R2": "critical",
    "R3": "high",
    "R4": "medium",
    "R6": "medium",
    "R7": "high",
    "R8": "critical",
    "R9": "medium",
    "R10": "medium",
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
    "PR3": "critical",
    "PR4": "high",
    "PR5": "critical",
    "PR6": "critical",
    "PR7": "high",
    "PR8": "critical",
    "PR9": "high",
    "PR10": "high",
    "PR11": "critical",
    "PR12": "medium",
    "PR13": "critical",
    "PR14": "critical",
    "PR15": "medium",
}

RULE_EDGE_BINDINGS = {
    "R2": ["Core_Business_Loop", "Tech_Barrier"],
    "R3": ["Narrative_Causality"],
    "R4": ["Compliance_Ethics", "Core_Business_Loop"],
    "R6": ["Channel_Physical_Access", "Core_Business_Loop"],
    "R7": ["Willingness_To_Pay", "Core_Business_Loop"],
    "R8": ["Real_Competition"],
    "R9": ["Market_Reachability"],
    "R10": ["Innovation_Verification", "Real_Competition"],
    "R11": ["Unit_Economics"],
    "R12": ["Pricing_Space"],
    "R13": ["Cash_Flow_Health"],
    "R14": ["Supply_Chain_Sync", "Core_Business_Loop"],
    "R15": ["Cold_Start_Engine", "Core_Business_Loop"],
    "R16": ["R&D_Team_Match"],
    "R17": ["Resource_Feasibility"],
    "R18": ["Financial_Reasonableness"],
    "R19": ["Frequency_Mismatch"],
    "R20": ["Social_Value_Translation", "Core_Business_Loop"],
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

RULE_REVIEW_SPECS = {
    "R3": {
        "dimension": "痛点 × 方案因果",
        "left_keys": ["Core_Pain_Point", "Current_Pain"],
        "right_keys": ["Solution", "Value_Proposition"],
        "reason": "当前规则已通过结构判定，但用于复核“痛点是否真的被方案正面回应”的关键成对表达还不够明确。",
        "hint": "请补充：用户具体因什么而痛，你的方案具体改变了哪个动作或结果。",
    },
    "R6": {
        "dimension": "渠道 × 客群",
        "left_keys": ["Target_Customer"],
        "right_keys": ["Marketing_Channel"],
        "reason": "当前规则已通过结构判定，但用于复核“这个渠道是否真的能触达这类人”的成对表达还不够明确。",
        "hint": "请补充：首批用户在哪里、谁先看到、谁点击、谁决策购买。",
    },
    "R7": {
        "dimension": "付费对象 × 价格表达",
        "left_keys": ["Target_Customer", "Customer_Type"],
        "right_keys": ["Price", "Revenue_Model"],
        "reason": "当前规则已通过结构判定，但文本里还缺少“谁来付钱、为什么愿意按这个价格付”的明确成对表达。",
        "hint": "请补充：使用者、付费者、采购者是否同一人，以及价格依据。",
    },
    "R8": {
        "dimension": "痛点 × 竞争/替代",
        "left_keys": ["Core_Pain_Point", "Current_Pain"],
        "right_keys": ["Competitor_Pool", "Alternative_Solution"],
        "reason": "当前规则已通过结构判定，但还缺少更具体的竞品、旧方案或替代做法，无法继续细化复核竞争真实性。",
        "hint": "请补充：用户不用你时靠什么凑合解决，以及至少 1-3 个明确对手。",
    },
    "R9": {
        "dimension": "市场漏斗 × 细分边界",
        "left_keys": ["TAM", "SAM"],
        "right_keys": ["SOM", "Target_Customer"],
        "reason": "当前规则已通过结构判定，但市场漏斗与真实切入边界的对应关系还不够具体。",
        "hint": "请补充：前 100 个用户来自哪里、先打哪个细分市场，而不是只写大盘规模。",
    },
    "R10": {
        "dimension": "创新点 × 竞争对标",
        "left_keys": ["Differentiation", "Value_Proposition"],
        "right_keys": ["Competitor_Pool", "Control_Experiment", "Verifiable_Metric"],
        "reason": "当前规则已通过结构判定，但还缺少足够清晰的对标对象、验证指标或对照实验表达，难以继续细化复核创新是否真的成立。",
        "hint": "请补充：你比谁强、强在哪个指标、证据来自什么测试或样本。",
    },
    "R11": {
        "dimension": "LTV × CAC",
        "left_keys": ["LTV"],
        "right_keys": ["CAC"],
        "reason": "当前规则已通过结构判定，但用于复核单位经济是否真成立的单客收益/获客成本表达还不够明确。",
        "hint": "请补充：单客收入、单客成本、毛利和回本周期。",
    },
    "R12": {
        "dimension": "价格 × 成本",
        "left_keys": ["Price", "Unit_Price"],
        "right_keys": ["Fixed_Cost", "Variable_Cost", "Cost_Structure"],
        "reason": "当前规则已通过结构判定，但用于复核利润空间的价格—成本成对表达仍不足。",
        "hint": "请补充：价格下限由什么决定，上限由什么价值支撑。",
    },
    "R13": {
        "dimension": "资金 × 账期/消耗",
        "left_keys": ["Startup_Capital"],
        "right_keys": ["Account_Period", "Burn_Rate"],
        "reason": "当前规则已通过结构判定，但用于复核现金流健康度的启动资金、账期与消耗速度表达仍不够成对。",
        "hint": "请补充：账上资源能撑多久，最先断裂的是哪一环。",
    },
    "R18": {
        "dimension": "财务预测 × 关键假设",
        "left_keys": ["Financial_Model"],
        "right_keys": ["Key_Assumption", "Sensitivity_Analysis"],
        "reason": "当前规则已通过结构判定，但财务预测与关键假设/敏感性分析的成对表达不足，暂时无法进一步核实其合理性。",
        "hint": "请补充：收入、成本、转化率等关键假设分别来自哪里。",
    },
    "R19": {
        "dimension": "使用频次 × 收费方式",
        "left_keys": ["Usage_Frequency"],
        "right_keys": ["Revenue_Model", "Unit_Price"],
        "reason": "当前规则已通过结构判定，但使用频次与收费方式之间的成对表达还不够明确。",
        "hint": "请补充：用户多久用一次、每次付费还是持续订阅、为什么能成立。",
    },
    "R2": {
        "dimension": "技术路线 × 商业价值",
        "left_keys": ["Tech_Route", "Core_Advantage", "IP"],
        "right_keys": ["Value_Proposition", "Target_Customer"],
        "reason": "当前规则已通过结构判定，但还缺少足够清晰的“技术到底改变了什么商业价值”的成对表达。",
        "hint": "请补充：技术带来了什么更快、更省、更准的结果，对谁产生价值。",
    },
    "R4": {
        "dimension": "合规要求 × 行业场景",
        "left_keys": ["Industry", "Data_Source"],
        "right_keys": ["Policy_Constraints"],
        "reason": "当前规则已通过结构判定，但合规要求与业务场景之间的对应关系还不够明确。",
        "hint": "请补充：涉及哪类监管、哪项数据、哪个审批/备案环节。",
    },
    "R14": {
        "dimension": "产品交付 × 供应保障",
        "left_keys": ["Product_Form", "Delivery_Method"],
        "right_keys": ["Supplier_Network", "Fulfill_Cost"],
        "reason": "当前规则已通过结构判定，但产品交付与供应保障之间的成对表达仍不完整。",
        "hint": "请补充：谁供货、谁安装/配送、成本和交付时效如何保证。",
    },
    "R15": {
        "dimension": "平台模式 × 冷启动",
        "left_keys": ["Platform_Model", "Seed_Users"],
        "right_keys": ["Cold_Start_Strategy"],
        "reason": "当前规则已通过结构判定，但平台型项目的首批用户与冷启动路径仍不够具体。",
        "hint": "请补充：先供给还是先需求，前 50-100 个种子用户具体从哪里来。",
    },
    "R16": {
        "dimension": "技术路线 × 团队背景",
        "left_keys": ["Tech_Route", "TRL"],
        "right_keys": ["Team_Background"],
        "reason": "当前规则已通过结构判定，但用于复核“团队是否真能做出这条技术路线”的成对表达仍不足。",
        "hint": "请补充：谁负责核心技术、谁负责工程落地、是否有外部合作方。",
    },
    "R17": {
        "dimension": "资源路径 × 里程碑",
        "left_keys": ["Resource_List", "Tech_Route"],
        "right_keys": ["Milestone_Plan"],
        "reason": "当前规则已通过结构判定，但资源投入与时间里程碑之间的成对表达仍不够具体。",
        "hint": "请补充：30/60/90 天分别做什么，用什么资源验证什么结果。",
    },
    "R20": {
        "dimension": "社会价值 × 商业转化",
        "left_keys": ["Scenario_Research", "Pilot_Cooperation"],
        "right_keys": ["Translation_Roadmap", "Revenue_Model"],
        "reason": "当前规则已通过结构判定，但社会价值如何转成可持续商业闭环的成对表达仍不足。",
        "hint": "请补充：谁为社会价值买单，或者如何从试点走向收入。",
    },







    "PR1": {
        "dimension": "受益对象 × 服务场景",
        "left_keys": ["Beneficiary_Group"],
        "right_keys": ["Service_Scenario", "Urgency_Pain"],
        "reason": "当前规则已通过结构判定，但受益对象与服务场景/紧迫问题之间的成对表达还不够明确。",
        "hint": "请补充：具体是谁、在什么场景、遇到什么紧迫问题。",
    },
    "PR2": {
        "dimension": "需求证据 × 问题严重度",
        "left_keys": ["Research_Sample", "Field_Observation", "Needs_Quote"],
        "right_keys": ["Problem_Severity"],
        "reason": "当前规则已通过结构判定，但需求证据与问题严重度的成对表达仍不足，难以继续复核问题是否真实且值得介入。",
        "hint": "请补充：样本、走访观察、原话引述、问题严重度中的至少两类。",
    },
    "PR3": {
        "dimension": "需求证据 × 干预方案",
        "left_keys": ["Needs_Quote", "Field_Observation", "Problem_Severity"],
        "right_keys": ["Intervention_Solution", "Core_Service", "Expected_Outcome"],
        "reason": "当前规则已通过结构判定，但还缺少“哪个问题对应哪个干预动作”的明确成对表达。",
        "hint": "请补充：真实需求证据如何对应具体服务方案与预期改变。",
    },
    "PR4": {
        "dimension": "服务对象 × 协同方",
        "left_keys": ["Beneficiary_Group", "Service_Scenario"],
        "right_keys": ["Government_Link", "NGO_Partner", "Community_Leader", "Volunteer_Source"],
        "reason": "当前规则已通过结构判定，但服务对象与关键协同方之间的嵌合关系还不够明确。",
        "hint": "请补充：谁和你一起做，分别在哪个服务场景中起作用。",
    },
    "PR5": {
        "dimension": "受益对象 × 伦理保护",
        "left_keys": ["Beneficiary_Group", "Vulnerable_Group"],
        "right_keys": ["Ethical_Risk", "Privacy_Protection", "Consent_Process"],
        "reason": "当前规则已通过结构判定，但受益对象与隐私/同意/伦理保护动作之间的成对表达仍不足。",
        "hint": "请补充：面对这类对象时，如何做隐私保护、知情同意或风险规避。",
    },
    "PR6": {
        "dimension": "资金来源 × 筹资渠道",
        "left_keys": ["Funding_Source", "Donation_Product"],
        "right_keys": ["Grant_Channel", "Revenue_Supplement"],
        "reason": "当前规则已通过结构判定，但资金来源与获取渠道/补充造血之间的成对表达仍不清楚。",
        "hint": "请补充：主要资金从哪里来，通过什么方式拿到，是否有补充造血路径。",
    },
    "PR7": {
        "dimension": "服务成本 × 资金效率",
        "left_keys": ["Single_Service_Cost", "Management_Cost"],
        "right_keys": ["Fund_Use_Ratio", "Budget_Ceiling"],
        "reason": "当前规则已通过结构判定，但单次服务成本与资金使用效率之间的成对表达仍不足。",
        "hint": "请补充：每服务 1 人/1 次大概花多少钱，资金主要花在哪，效率如何。",
    },
    "PR8": {
        "dimension": "影响目标 × 评估方法",
        "left_keys": ["Impact_Goal", "Expected_Outcome"],
        "right_keys": ["Indicator_System", "Baseline_Data", "Evaluation_Method"],
        "reason": "当前规则已通过结构判定，但“想改变什么”与“如何验证真的改变了”之间的成对表达仍不够明确。",
        "hint": "请补充：目标、指标、基线和评估方法如何一一对应。",
    },
    "PR9": {
        "dimension": "触达方式 × 留存/转介",
        "left_keys": ["Reach_Channel", "Participation_Motivation"],
        "right_keys": ["Retention_Mechanism", "Referral_Path"],
        "reason": "当前规则已通过结构判定，但受益者从触达到留存/转介的路径仍不够具体。",
        "hint": "请补充：怎么找到人、为什么愿意参与、如何留下来并转介给更多人。",
    },
    "PR10": {
        "dimension": "透明机制 × 外部信任",
        "left_keys": ["Disclosure_Frequency", "Financial_Disclosure"],
        "right_keys": ["Story_Evidence", "Third_Party_Endorsement"],
        "reason": "当前规则已通过结构判定，但信息披露、公示与外部信任背书之间的成对表达仍不足。",
        "hint": "请补充：多久公示一次、公开什么、谁来背书。",
    },
    "PR11": {
        "dimension": "试点结果 × 复制扩散",
        "left_keys": ["Pilot_Site", "Pilot_Result"],
        "right_keys": ["Replication_Condition", "Expansion_Path"],
        "reason": "当前规则已通过结构判定，但试点结果与复制扩散条件之间的成对表达仍不够清楚。",
        "hint": "请补充：试点证明了什么，复制需要哪些条件，下一步怎么扩散。",
    },
    "PR12": {
        "dimension": "志愿者角色 × 培训/排班",
        "left_keys": ["Volunteer_Role"],
        "right_keys": ["Training_Process", "Scheduling_Mechanism", "Incentive_NonCash"],
        "reason": "当前规则已通过结构判定，但志愿者角色与培训、排班、激励机制之间的成对表达仍不足。",
        "hint": "请补充：志愿者负责什么、怎么培训、怎么排班、靠什么激励。",
    },
    "PR13": {
        "dimension": "关键资源 × 风险缓冲",
        "left_keys": ["Key_Resource", "Resource_Gap"],
        "right_keys": ["Replacement_Plan", "Risk_Buffer"],
        "reason": "当前规则已通过结构判定，但关键资源与替代/缓冲方案之间的成对表达仍不足。",
        "hint": "请补充：最关键资源是什么，断掉时用什么替代，怎么兜底。",
    },
    "PR14": {
        "dimension": "政策依据 × 执行边界",
        "left_keys": ["Policy_Basis"],
        "right_keys": ["Qualification_Requirement", "Safety_Redline", "Public_Opinion_Risk"],
        "reason": "当前规则已通过结构判定，但政策依据与资质/安全/舆情边界之间的成对表达仍不够明确。",
        "hint": "请补充：依据哪条政策，具体要满足什么资质、安全或舆情要求。",
    },
    "PR15": {
        "dimension": "合作伙伴 × 长期共创",
        "left_keys": ["Enterprise_Partner", "School_Hospital_Community"],
        "right_keys": ["CoCreation_Mode", "Longterm_Mechanism"],
        "reason": "当前规则已通过结构判定，但合作伙伴与长期共创机制之间的成对表达仍不足。",
        "hint": "请补充：和谁长期合作，以什么机制持续共创。",
    },
}

DISPLAY_KEY_LABELS = {
    "Target_Customer": "目标客群",
    "Value_Proposition": "价值主张",
    "Marketing_Channel": "营销渠道",
    "Revenue_Model": "收入模型",
    "Cost_Structure": "成本结构",
    "Core_Pain_Point": "核心痛点",
    "Price": "产品定价",
    "LTV": "客户终身价值",
    "CAC": "获客成本",
    "Startup_Capital": "启动资金",
    "Account_Period": "账期",
    "Seed_Users": "种子用户",
    "Tech_Route": "技术路线",
    "Team_Background": "团队背景",
    "Competitor_Pool": "竞争对手",
    "IP": "知识产权",
    "Fulfill_Cost": "履约成本",
    "Supplier_Network": "供应链",
    "Control_Experiment": "对照实验",
    "TAM": "总潜在市场",
    "SAM": "可服务市场",
    "SOM": "可获得市场",
    "Usage_Frequency": "使用频次",
    "Milestone_Plan": "里程碑",
    "Policy_Constraints": "政策约束",
    "Beneficiary": "受益对象",
    "Service_Object": "服务对象",
    "Social_Issue": "社会问题",
    "Survey_Data": "调研数据",
    "Interview_Record": "访谈记录",
    "Case_Study": "案例研究",
    "Service_Process": "服务流程",
    "Donation_Source": "捐赠来源",
    "Partnership_Model": "合作模式",
    "Volunteer_System": "志愿者机制",
    "Impact_Metric": "成效指标",
    "KPI": "关键指标",
    "Outcome_Index": "结果指标",
    "Replication_Path": "复制路径",
    "Solution": "解决方案",
    "Alternative_Solution": "替代方案",
    "Differentiation": "差异化",
    "Financial_Model": "财务模型",
    "Key_Assumption": "关键假设",
    "Sensitivity_Analysis": "敏感性分析",
    "Industry": "行业",
    "Scenario_Research": "场景调研",
    "Pilot_Cooperation": "试点合作",
    "Translation_Roadmap": "转化路径",
    "Core_Advantage": "核心优势",
    "Competitor_Status": "竞品现状",
    "Switching_Cost": "迁移成本",
    "Resource_List": "资源清单",
    "Product_Form": "产品形态",
    "Delivery_Method": "交付方式",
    "Platform_Model": "平台模式",
    "Cold_Start_Strategy": "冷启动策略",
    "TRL": "技术成熟度",
    "Data_Source": "数据来源",
    "Current_Pain": "当前痛点",
    "Customer_Type": "客户类型",
    "Burn_Rate": "资金消耗速度",
    "Unit_Price": "单次价格",
    "Disposable_Income": "可支配收入",
    "Marketing_Budget": "营销预算",
    "Fixed_Cost": "固定成本",
    "Variable_Cost": "可变成本",
    "Verifiable_Metric": "可验证指标",
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
    "Pilot_Site": "试点点位",
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


def _display_key_label(key: str) -> str:
    return DISPLAY_KEY_LABELS.get(str(key or '').strip(), str(key or '').strip())



FIELD_KEY_ALIASES: Dict[str, List[str]] = {
    "Core_Pain_Point": ["Problem_Statement", "Problem_Solution_Link", "Pain_Point", "User_Pain", "Problem", "核心痛点", "痛点"],
    "Current_Pain": ["Problem_Statement", "Problem_Solution_Link", "Current_Problem", "当前问题", "现状痛点"],
    "Solution": ["Solution_Fit", "Solution_Statement", "Problem_Solution_Link", "解决方案", "方案"],
    "Value_Proposition": ["Vision_Statement", "Value_Statement", "核心价值", "价值主张"],
    "Competitor_Pool": ["Competitive_Landscape", "Competitive_Threat", "Potential_Threat", "Competitor_Status", "Competitor_Weakness", "竞争格局", "竞争对手"],
    "Alternative_Solution": ["Alternative_Solution", "Legacy_Solution", "旧方案", "替代方案", "现有做法"],
    "TAM": ["Target_Market", "Market_Size", "Market_Size_Data", "Market_Growth", "总潜在市场", "市场规模"],
    "SAM": ["Target_Segment", "Application_Scenario", "Scenario_Research", "细分市场", "应用场景"],
    "SOM": ["Pilot_Cooperation", "Seed_Users", "可获得市场", "首批客户"],
    "Target_Customer": ["Customer_Profile", "Target_User", "Target_Segment", "目标客户", "目标用户", "客户画像"],
    "Beneficiary": ["受益对象", "受益人", "帮扶对象", "服务对象"],
    "Service_Object": ["服务对象", "重点人群", "服务人群"],
    "Social_Issue": ["社会问题", "公益痛点", "公共问题"],
    "Survey_Data": ["调研数据", "问卷数据", "统计数据"],
    "Interview_Record": ["访谈记录", "深访记录", "入户访谈"],
    "Case_Study": ["案例研究", "试点案例", "典型案例"],
    "Service_Process": ["服务流程", "干预流程", "执行流程"],
    "Donation_Source": ["捐赠来源", "资助来源", "基金支持"],
    "Partnership_Model": ["合作模式", "合作伙伴", "联动机制"],
    "Volunteer_System": ["志愿者体系", "志愿者机制", "志愿者招募"],
    "Impact_Metric": ["成效指标", "影响指标", "社会影响指标"],
    "KPI": ["关键指标", "KPI", "考核指标"],
    "Outcome_Index": ["结果指标", "产出指标", "效果指标"],
    "Replication_Path": ["复制路径", "扩散路径", "推广路径"],
    "Marketing_Channel": ["Sales_Channel", "Go_To_Market", "获客渠道", "营销渠道", "推广渠道"],
    "Differentiation": ["Tech_Achievement", "Competitive_Advantage", "Defensive_Strategy", "核心优势", "差异化"],
    "Verifiable_Metric": ["Validation", "Metric", "Control_Experiment", "验证", "指标"],
    "LTV": ["Customer_Lifetime_Value", "单客价值", "客户终身价值"],
    "CAC": ["Acquisition_Cost", "获客成本", "拉新成本"],
    "Price": ["Pricing", "Price_Model", "产品定价", "价格"],
    "Fixed_Cost": ["Cost_Breakdown", "成本结构", "固定成本"],
    "Variable_Cost": ["Cost_Breakdown", "成本结构", "可变成本"],
    "Startup_Capital": ["Funding", "Budget", "启动资金", "账上现金"],
    "Account_Period": ["Payment_Cycle", "回款周期", "账期"],
    "Burn_Rate": ["Burn_Rate", "资金消耗", "月消耗"],
    "Financial_Model": ["Financial_Model", "财务模型", "收入预测"],
    "Key_Assumption": ["Key_Assumption", "关键假设"],
    "Sensitivity_Analysis": ["Sensitivity_Analysis", "敏感性分析"],
    "Usage_Frequency": ["Usage_Frequency", "使用频次", "使用周期"],
    "Tech_Route": ["Tech_Route", "Technology_Route", "Technical_Architecture", "技术路线", "技术方案"],
    "TRL": ["Tech_Achievement", "技术成熟度", "技术成果"],
    "Team_Background": ["Founder_Background", "Team_Profile", "团队背景", "团队介绍"],
    "Milestone_Plan": ["Milestone", "Roadmap", "里程碑", "阶段计划"],
    "Resource_List": ["Resource_List", "资源清单", "资源投入"],
    "Beneficiary_Group": ["受益对象", "服务对象", "受助群体", "受益群体", "帮扶对象"],
    "Urgency_Pain": ["紧迫问题", "紧急痛点", "迫切需求", "突出困难"],
    "Service_Scenario": ["服务场景", "应用场景", "发生场景", "介入场景"],
    "Accessibility_Constraint": ["可及性约束", "可及性障碍", "接触门槛"],
    "Research_Sample": ["调研样本", "样本量", "访谈样本", "调查样本"],
    "Field_Observation": ["实地观察", "走访观察", "现场观察", "田野观察"],
    "Needs_Quote": ["需求引述", "访谈原话", "受访者原话", "用户原话"],
    "Problem_Severity": ["问题严重度", "问题程度", "紧迫性", "严重性"],
    "Intervention_Solution": ["干预方案", "介入方案", "服务方案", "解决方案"],
    "Expected_Outcome": ["预期成效", "预期结果", "预期影响", "目标结果"],
    "Core_Service": ["核心服务", "核心动作", "主要服务内容"],
    "Trust_Mechanism": ["信任机制", "信任建立", "公信机制"],
    "Government_Link": ["政府链接", "政府合作", "政府支持"],
    "NGO_Partner": ["公益伙伴", "ngo伙伴", "公益组织合作方"],
    "Community_Leader": ["社区关键人", "社区负责人", "社区骨干"],
    "Volunteer_Source": ["志愿者来源", "志愿者渠道", "志愿者招募来源"],
    "Vulnerable_Group": ["弱势群体", "脆弱群体", "重点保护对象"],
    "Ethical_Risk": ["伦理风险", "伦理问题", "伦理隐患"],
    "Privacy_Protection": ["隐私保护", "信息保护", "数据保护"],
    "Consent_Process": ["知情同意流程", "知情同意", "授权流程"],
    "Funding_Source": ["资金来源", "筹资来源", "资助方", "捐赠来源"],
    "Donation_Product": ["捐赠产品", "捐赠项目", "募资产品"],
    "Grant_Channel": ["资助渠道", "申报渠道", "筹资渠道", "政府购买服务"],
    "Revenue_Supplement": ["补充收入", "配套收入", "造血收入", "服务收费"],
    "Single_Service_Cost": ["单次服务成本", "单人服务成本", "单次干预成本"],
    "Management_Cost": ["管理成本", "运营管理成本"],
    "Fund_Use_Ratio": ["资金使用比例", "资金效率", "使用效率"],
    "Budget_Ceiling": ["预算上限", "预算边界"],
    "Impact_Goal": ["影响目标", "公益目标", "社会目标", "成效目标"],
    "Indicator_System": ["指标体系", "衡量指标", "评估指标", "KPI"],
    "Baseline_Data": ["基线数据", "前测数据", "初始数据"],
    "Evaluation_Method": ["评估方法", "评估方式", "验证方法"],
    "Reach_Channel": ["触达渠道", "接触渠道", "覆盖渠道"],
    "Participation_Motivation": ["参与动机", "参与理由", "参加动力"],
    "Retention_Mechanism": ["留存机制", "持续参与机制"],
    "Referral_Path": ["转介路径", "转介绍路径", "扩散转介"],
    "Disclosure_Frequency": ["披露频率", "公示频率", "公开频率"],
    "Financial_Disclosure": ["财务披露", "财务公开", "资金公示"],
    "Story_Evidence": ["故事证据", "案例故事", "服务故事"],
    "Third_Party_Endorsement": ["第三方背书", "第三方认证", "外部背书"],
    "Pilot_Site": ["试点点位", "试点地区", "试点学校", "试点社区"],
    "Pilot_Result": ["试点结果", "试点成效", "试点反馈"],
    "Replication_Condition": ["复制条件", "复制前提", "扩散条件"],
    "Expansion_Path": ["扩散路径", "复制路径", "推广路径", "规模化路径"],
    "Volunteer_Role": ["志愿者角色", "志愿者分工", "志愿者岗位"],
    "Training_Process": ["培训流程", "培训机制", "培训体系"],
    "Scheduling_Mechanism": ["排班机制", "排班流程", "调度机制"],
    "Incentive_NonCash": ["非现金激励", "荣誉激励", "成长激励"],
    "Key_Resource": ["关键资源", "核心资源", "关键要素"],
    "Resource_Gap": ["资源缺口", "资源不足"],
    "Replacement_Plan": ["替代方案", "替补方案", "资源替代方案"],
    "Risk_Buffer": ["风险缓冲", "风险预案", "备用方案"],
    "Policy_Basis": ["政策依据", "政策基础", "法规依据"],
    "Qualification_Requirement": ["资质要求", "准入要求", "执业要求"],
    "Safety_Redline": ["安全红线", "安全要求", "安全底线"],
    "Public_Opinion_Risk": ["舆情风险", "公众舆情风险"],
    "Enterprise_Partner": ["企业伙伴", "企业合作方", "企业资源方"],
    "School_Hospital_Community": ["学校/医院/社区", "学校", "医院", "社区"],
    "CoCreation_Mode": ["共创模式", "协同模式", "合作机制"],
    "Longterm_Mechanism": ["长期机制", "长效机制", "持续机制"],
}

_ALIAS_TO_CANONICAL: Dict[str, str] = {}
for _canonical, _aliases in FIELD_KEY_ALIASES.items():
    for _alias in [_canonical, *(_aliases or [])]:
        _ALIAS_TO_CANONICAL[str(_alias).strip().lower()] = _canonical


def _canonicalize_field_key(key: str) -> str:
    raw = str(key or '').strip()
    if not raw:
        return ''
    return _ALIAS_TO_CANONICAL.get(raw.lower(), raw)


def _append_field_value(bucket: Dict[str, List[str]], key: str, value: str) -> None:
    key = _canonicalize_field_key(key)
    value = str(value or '').strip()
    if not key or not _has_real_value(value):
        return
    bucket.setdefault(key, [])
    if value not in bucket[key]:
        bucket[key].append(value)

AUDIENCE_PATTERNS: Dict[str, List[str]] = {
    "elderly": ["老年", "老人", "银发", "中老年", "退休", "高龄", "养老"],
    "student": ["学生", "大学生", "中学生", "小学生", "校园", "考研"],
    "farmer": ["农户", "农民", "种植户", "养殖户", "合作社", "乡村", "农村"],
    "parent": ["家长", "宝妈", "宝爸", "父母", "监护人", "妈妈", "爸爸"],
    "caregiver": ["子女", "儿女", "家属", "照护者", "护工", "护理员", "看护"],
    "women": ["女性", "女生", "白领女性", "宝妈"],
    "enterprise": ["企业", "学校", "医院", "政府", "机构", "门店", "商家", "店主", "诊所", "社区卫生服务中心"],
    "general_consumer": ["白领", "上班族", "年轻人", "职场人", "消费者", "个人用户", "大众"],
    "professional": ["医生", "教师", "律师", "设计师", "工程师", "程序员", "销售", "飞手"],
}

DOMAIN_PATTERNS: Dict[str, List[str]] = {
    "health": ["医疗", "健康", "医院", "诊所", "医生", "慢病", "药", "护理", "养老", "康复", "体征", "问诊"],
    "education": ["教育", "学习", "学校", "学生", "教师", "课堂", "作业", "培训", "考研", "教学"],
    "agriculture": ["农业", "农户", "农民", "农药", "化肥", "植保", "农机", "耕地", "种植", "养殖"],
    "logistics": ["物流", "配送", "外卖", "履约", "仓储", "冷链", "运力", "司机", "路线", "快递", "运单"],
    "finance": ["金融", "保险", "信贷", "支付", "理赔", "风控", "证券", "贷款", "征信"],
    "retail": ["零售", "门店", "电商", "商超", "sku", "货架", "到店", "导购", "店主"],
    "manufacturing": ["工厂", "制造", "工业", "设备", "产线", "零部件", "硬件", "传感器", "机器人"],
    "government": ["政务", "政府", "监管", "审批", "公共服务", "民政"],
}

CHANNEL_PROFILES: List[Dict[str, Any]] = [
    {
        "id": "xiaohongshu",
        "tokens": ["小红书", "red"],
        "affinity": ["women", "parent", "student", "general_consumer"],
        "weak_for": ["elderly", "farmer", "enterprise"],
        "label": "小红书",
    },
    {
        "id": "douyin",
        "tokens": ["抖音", "短视频", "直播"],
        "affinity": ["general_consumer", "parent", "farmer", "elderly", "women", "student"],
        "weak_for": ["enterprise"],
        "label": "抖音/短视频",
    },
    {
        "id": "wechat",
        "tokens": ["微信", "朋友圈", "微信群", "社群", "公众号", "企业微信"],
        "affinity": ["elderly", "parent", "caregiver", "general_consumer", "professional", "enterprise"],
        "weak_for": [],
        "label": "微信/社群",
    },
    {
        "id": "offline",
        "tokens": ["线下", "地推", "社区", "村委", "居委会", "养老院", "药店", "诊所", "社区医院", "展会", "路演"],
        "affinity": ["elderly", "farmer", "enterprise", "parent", "caregiver"],
        "weak_for": [],
        "label": "线下触达",
    },
    {
        "id": "ecommerce",
        "tokens": ["淘宝", "天猫", "京东", "拼多多", "电商"],
        "affinity": ["general_consumer", "parent", "elderly", "farmer"],
        "weak_for": ["enterprise"],
        "label": "电商平台",
    },
    {
        "id": "b2b_sales",
        "tokens": ["销售", "拜访", "渠道商", "经销商", "代理商", "招投标", "bd", "商务拓展", "ka"],
        "affinity": ["enterprise", "professional"],
        "weak_for": ["student", "women", "general_consumer", "elderly"],
        "label": "B端销售",
    },
]

TECH_COMPLEXITY_PATTERNS: Dict[str, List[str]] = {
    "advanced_tech": [
        "ai", "算法", "大模型", "机器学习", "深度学习", "识别", "预测", "无人机", "硬件", "传感器",
        "医学影像", "嵌入式", "机器人", "平台调度", "区块链", "数字孪生", "边缘计算", "多模态", "脑机"
    ],
    "team_tech_ready": [
        "研发", "工程师", "算法", "计算机", "软件", "硬件", "技术负责人", "博士", "硕士", "实验室",
        "飞手", "产品经理", "架构师", "数据科学", "前端", "后端", "电子", "自动化"
    ],
}

GENERIC_DIFFERENTIATION_PATTERNS = ["更智能", "更高效", "更方便", "更便捷", "更精准", "首创", "领先", "创新", "体验更好", "效率更高"]
NO_COMPETITION_PATTERNS = ["没有竞争对手", "无竞争对手", "市场空白", "没人做", "暂无竞品", "没有替代", "独一无二"]
GENERIC_MARKET_PATTERNS = ["全国", "所有人", "全部用户", "所有用户", "海量用户", "亿级用户"]
AGGRESSIVE_FINANCIAL_PATTERNS = ["三年上市", "一年回本", "100%", "零获客成本", "零成本", "全国复制", "垄断", "十倍增长", "百倍增长"]
GENERIC_POLICY_PATTERNS = ["遵守法律", "合法合规", "按规定", "注意合规", "符合政策"]
STRICT_REGULATION_PATTERNS = {
    "health": ["医疗", "诊疗", "处方", "病历", "健康数据", "药品", "器械", "护理"],
    "finance": ["金融", "证券", "支付", "保险", "贷款", "征信", "理财"],
    "minor_education": ["未成年人", "儿童", "青少年", "小学生", "中学生", "学生数据"],
    "privacy": ["人脸", "定位", "轨迹", "身份证", "隐私", "个人信息", "生物识别", "摄像头"],
}

LOW_FREQUENCY_PATTERNS = ["低频", "偶尔", "应急", "一年", "半年", "一次", "按次", "突发", "季节性"]
HIGH_FREQUENCY_PATTERNS = ["高频", "每天", "每日", "每周", "日常", "持续使用", "复购", "经常"]
SUBSCRIPTION_PATTERNS = ["订阅", "会员", "包月", "月费", "年费", "连续付费", "saas"]
TRANSACTION_PATTERNS = ["抽成", "佣金", "按次收费", "单次", "买断", "项目制", "按单", "服务费"]
PREMIUM_PRICE_CUES = ["高端", "高净值", "中高收入", "企业付费", "保险支付", "机构采购", "子女付费", "家属付费"]
PROXY_USER_CUES = ["子女", "家属", "照护者", "护理员", "护工", "医生", "社区工作人员", "社工", "采购", "管理员", "老师"]
TIME_MARKERS = ["天", "周", "月", "季度", "年", "mvp", "试点", "里程碑", "阶段", "版本", "第1期", "第一期"]
PHYSICAL_PRODUCT_PATTERNS = ["硬件", "设备", "药品", "食品", "农资", "机器", "无人机", "手环", "仪器", "实物", "安装", "物流", "配送"]
DIGITAL_PRODUCT_PATTERNS = ["app", "小程序", "平台", "saas", "软件", "系统", "网站", "算法服务", "订阅"]
PLATFORM_PATTERNS = ["平台", "撮合", "双边", "商家入驻", "供需匹配", "市场", "生态", "社区"]
SOCIAL_VALUE_PATTERNS = ["公益", "社会价值", "乡村振兴", "助农", "普惠", "公益性", "帮扶", "社会效益", "弱势群体", "公共利益"]
ROADMAP_TOKENS = ["转化路径", "路线图", "roadmap", "阶段", "先", "再", "后续", "里程碑"]
PILOT_TOKENS = ["试点", "试运行", "样板", "示范", "合作点", "首批", "小范围", "mvp"]
ROI_VALUE_PATTERNS = ["降本", "提效", "提高", "减少", "提升", "节省", "准确率", "时效", "转化率", "客单价", "复购", "满意度"]
GENERIC_SOLUTION_PATTERNS = ["app", "平台", "系统", "解决方案", "工具", "服务", "小程序"]


def _normalize_text(text: str) -> str:
    return (text or "").strip().lower()



def _parse_raw_node(raw: str) -> Tuple[str, str]:
    raw = str(raw or "").strip()
    if not raw:
        return "", ""
    if ":" in raw:
        key, value = raw.split(":", 1)
    elif "：" in raw:
        key, value = raw.split("：", 1)
    else:
        return "", raw
    return _canonicalize_field_key(key.strip()), value.strip()


def _infer_textual_field_values(source_text: str) -> Dict[str, List[str]]:
    inferred: Dict[str, List[str]] = {}
    for unit in _split_source_units(source_text):
        lowered = _normalize_text(unit)
        if not unit or len(unit) < 6:
            continue

        if _contains_any(lowered, ["核心痛点", "痛点", "传不通", "连不上", "待机短", "高功耗", "预约接入", "多径干扰", "火情", "人工巡检", "无法覆盖", "维护成本", "响应迟缓", "高功耗待机"]):
            _append_field_value(inferred, "Core_Pain_Point", unit)
            _append_field_value(inferred, "Current_Pain", unit)

        if _contains_any(lowered, ["我们提供", "价值主张", "解决", "终端", "随遇接入", "超长待机", "灵活组网", "降本", "提效", "防火通信终端"]):
            _append_field_value(inferred, "Value_Proposition", unit)
            if _contains_any(lowered, ["解决", "实现", "提供"]):
                _append_field_value(inferred, "Solution", unit)

        if _contains_any(lowered, ["竞争对手", "华为", "中兴", "巨头", "现有方案", "替代", "手持卫星电话", "人工巡检", "旧方案", "巡护员"]):
            if _contains_any(lowered, ["替代", "手持卫星电话", "人工巡检", "旧方案", "巡护员"]):
                _append_field_value(inferred, "Alternative_Solution", unit)
            else:
                _append_field_value(inferred, "Competitor_Pool", unit)

        if _contains_any(lowered, ["市场规模", "亿元", "万亿", "2030", "2025", "市场空间", "中国卫星互联网"]):
            _append_field_value(inferred, "TAM", unit)
        if _contains_any(lowered, ["森林防火", "国土安全", "应急救援", "农业", "运输业", "军事", "细分市场", "应用场景", "无人区", "荒山密林"]):
            _append_field_value(inferred, "SAM", unit)
        if _contains_any(lowered, ["目标客户", "b端客户", "林业集团", "船舶集团", "电子科技集团", "航天科技集团", "前100个用户", "大兴安岭"]):
            _append_field_value(inferred, "Target_Customer", unit)
            if _contains_any(lowered, ["前100个用户", "首批", "试点", "意向客户"]):
                _append_field_value(inferred, "SOM", unit)

        if _contains_any(lowered, ["收入", "收费", "销售终端", "技术开发合同", "服务费", "硬件升级服务"]):
            _append_field_value(inferred, "Revenue_Model", unit)
        if _contains_any(lowered, ["采购", "付钱", "付费", "客户"]):
            _append_field_value(inferred, "Customer_Type", unit)
        if _contains_any(lowered, ["成本", "单价", "价格"]):
            _append_field_value(inferred, "Price", unit)
            _append_field_value(inferred, "Cost_Structure", unit)

        if _contains_any(lowered, ["技术", "协议", "算法", "ota", "嵌入式", "组网", "卫星通信"]):
            _append_field_value(inferred, "Tech_Route", unit)
            _append_field_value(inferred, "TRL", unit)
        if _contains_any(lowered, ["团队", "研发", "工程师", "研究生团队", "合作方", "专家"]):
            _append_field_value(inferred, "Team_Background", unit)

        if _contains_any(lowered, ["阶段", "6个月", "30/60/90", "里程碑", "试点", "未来"]):
            _append_field_value(inferred, "Milestone_Plan", unit)
        if _contains_any(lowered, ["资源", "合同", "815万元", "资金", "合作单位"]):
            _append_field_value(inferred, "Resource_List", unit)
            _append_field_value(inferred, "Startup_Capital", unit)

    return inferred


def _collect_field_values(extracted_edges: Dict[str, List[str]], source_text: str = "") -> Dict[str, List[str]]:
    field_values: Dict[str, List[str]] = {}
    for nodes in (extracted_edges or {}).values():
        for raw in nodes or []:
            key, value = _parse_raw_node(raw)
            if not key or not value:
                continue
            _append_field_value(field_values, key, value)
    inferred = _infer_textual_field_values(source_text)
    for key, values in inferred.items():
        for value in values:
            _append_field_value(field_values, key, value)
    return field_values


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    lowered = _normalize_text(text)
    return any(str(keyword).lower() in lowered for keyword in keywords)


def _infer_audience_tags(text: str) -> List[str]:
    tags: List[str] = []
    lowered = _normalize_text(text)
    for tag, patterns in AUDIENCE_PATTERNS.items():
        if any(pattern.lower() in lowered for pattern in patterns):
            tags.append(tag)
    return tags


def _infer_domain_tags(text: str) -> List[str]:
    tags: List[str] = []
    lowered = _normalize_text(text)
    for tag, patterns in DOMAIN_PATTERNS.items():
        if any(pattern.lower() in lowered for pattern in patterns):
            tags.append(tag)
    return tags


def _infer_channel_profiles(text: str) -> List[Dict[str, Any]]:
    lowered = _normalize_text(text)
    profiles: List[Dict[str, Any]] = []
    for profile in CHANNEL_PROFILES:
        if any(token.lower() in lowered for token in profile.get("tokens", [])):
            profiles.append(profile)
    return profiles


def _extract_amount(text: str) -> float | None:
    if not text:
        return None
    normalized = text.replace(",", "").replace("，", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*(亿|万元|万|千|k|K|元|块|rmb|￥|¥)?", normalized, re.IGNORECASE)
    if not match:
        return None
    try:
        value = float(match.group(1))
    except Exception:
        return None
    unit = (match.group(2) or "").lower()
    multiplier = 1.0
    if unit == "亿":
        multiplier = 100000000.0
    elif unit in {"万", "万元"}:
        multiplier = 10000.0
    elif unit in {"千", "k"}:
        multiplier = 1000.0
    return value * multiplier


def _extract_days(text: str) -> int | None:
    if not text:
        return None
    normalized = text.replace("个", "")
    patterns = [
        (r"(\d+)\s*天", 1),
        (r"(\d+)\s*周", 7),
        (r"(\d+)\s*月", 30),
        (r"(\d+)\s*季", 90),
    ]
    for pattern, multiplier in patterns:
        match = re.search(pattern, normalized)
        if match:
            try:
                return int(match.group(1)) * multiplier
            except Exception:
                return None
    return None


def _extract_monthly_amount(text: str) -> float | None:
    if not text:
        return None
    amount = _extract_amount(text)
    if amount is None:
        return None
    lowered = _normalize_text(text)
    if any(token in lowered for token in ["每天", "日耗", "/天", "每日电"]):
        return amount * 30
    if any(token in lowered for token in ["每周", "/周"]):
        return amount * 4
    if any(token in lowered for token in ["每年", "/年"]):
        return amount / 12
    return amount


def _severity_max(left: str, right: str) -> str:
    if SEVERITY_RANK.get(left, 0) >= SEVERITY_RANK.get(right, 0):
        return left
    return right


def _best_status(current: str, candidate: str) -> str:
    return current if STATUS_RANK.get(current, 0) >= STATUS_RANK.get(candidate, 0) else candidate


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
    source_excerpt: str = "",
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
        "source_excerpt": source_excerpt,
    }



def _sanitize_excerpt(text: str, max_chars: int = 96) -> str:
    text = re.sub(r"\s+", " ", str(text or "").strip())
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def _is_meaningful_excerpt(text: str) -> bool:
    text = str(text or "").strip()
    if not text:
        return False
    if re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", text):
        return False
    if text in {"(待补充)", "待补充", "无", "暂无"}:
        return False
    if len(text) < 4 and not re.search(r"[A-Za-z]{3,}|[一-鿿]{2,}", text):
        return False
    return True


def _has_real_value(value: str) -> bool:
    value = str(value or "").strip()
    return bool(value) and value not in {"(待补充)", "待补充", "(缺失)", "缺失"}


def _split_source_units(source_text: str) -> List[str]:
    raw = str(source_text or "").replace("\r", "\n")
    parts = re.split(r"[\n。！？!?；;]", raw)
    return [re.sub(r"\s+", " ", part).strip() for part in parts if part and part.strip()]


def _keyword_tokens(value: str) -> List[str]:
    value = str(value or "").strip()
    if not _has_real_value(value):
        return []
    tokens: List[str] = []
    candidates = [value]
    candidates.extend(re.split(r"[、,，/（）()\-\s]+", value))
    for item in candidates:
        item = str(item or "").strip()
        if not item:
            continue
        if re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", item):
            continue
        if len(item) < 2 and not re.search(r"[A-Za-z]{3,}|[一-鿿]{2,}", item):
            continue
        if item not in tokens:
            tokens.append(item)
    return tokens[:8]


def _find_supporting_excerpt(source_text: str, *values: str) -> str:
    units = _split_source_units(source_text)
    if not units:
        return ""
    keywords: List[str] = []
    for value in values:
        for token in _keyword_tokens(value):
            if token not in keywords:
                keywords.append(token)
    if not keywords:
        return ""

    best_unit = ""
    best_score = -1
    for unit in units:
        score = sum(1 for token in keywords if token and token.lower() in unit.lower())
        if score > best_score:
            best_unit = unit
            best_score = score
    if best_score <= 0:
        for token in keywords:
            lowered = source_text.lower()
            idx = lowered.find(token.lower())
            if idx >= 0:
                start = max(0, idx - 24)
                end = min(len(source_text), idx + max(len(token), 20) + 36)
                excerpt = _sanitize_excerpt(source_text[start:end])
                return excerpt if _is_meaningful_excerpt(excerpt) else ""
        return ""
    excerpt = _sanitize_excerpt(best_unit)
    return excerpt if _is_meaningful_excerpt(excerpt) else ""


def _enrich_check_with_excerpt(check: Dict[str, Any], source_text: str) -> Dict[str, Any]:
    check = dict(check or {})
    if check.get("source_excerpt"):
        return check
    excerpt = _find_supporting_excerpt(
        source_text,
        check.get("left_value", ""),
        check.get("right_value", ""),
        check.get("reason", ""),
    )
    if excerpt:
        check["source_excerpt"] = excerpt
    return check


def _pick_first(field_values: Dict[str, List[str]], candidate_keys: List[str]) -> Tuple[str, str]:
    for key in candidate_keys:
        values = field_values.get(key, [])
        if values:
            return key, values[0]
    if candidate_keys:
        return candidate_keys[0], "(待补充)"
    return "", "(待补充)"

def _collect_rule_structural_hits(rule_id: str, field_values: Dict[str, List[str]], extracted_edges: Dict[str, List[str]] | None) -> List[str]:
    hits: List[str] = []
    extracted_edges = extracted_edges or {}

    for edge_name in RULE_EDGE_BINDINGS.get(rule_id, []):
        for raw in extracted_edges.get(edge_name, []) or []:
            raw = str(raw or "").strip()
            if raw and raw not in hits:
                hits.append(raw)

    spec = RULE_REVIEW_SPECS.get(rule_id) or {}
    for key in list(spec.get("left_keys", [])) + list(spec.get("right_keys", [])):
        for value in field_values.get(key, []) or []:
            raw = f"{key}: {value}"
            if raw not in hits:
                hits.append(raw)
    return hits[:10]


def _enrich_check_with_structural_hits(check: Dict[str, Any], field_values: Dict[str, List[str]], extracted_edges: Dict[str, List[str]] | None) -> Dict[str, Any]:
    check = dict(check or {})
    rule_id = str(check.get("rule_id") or "").strip()
    if rule_id and not check.get("structural_hit_fields"):
        check["structural_hit_fields"] = _collect_rule_structural_hits(rule_id, field_values or {}, extracted_edges or {})
    check["review_pair_complete"] = _has_real_value(check.get("left_value", "")) and _has_real_value(check.get("right_value", ""))
    return check


def build_structural_field_notes(
    extracted_edges: Dict[str, List[str]] | None,
    *,
    stage_rule_ids: Iterable[str] | None = None,
    source_text: str = "",
) -> List[Dict[str, Any]]:
    """
    仅用于提示“标准字段完备度”，不再阻断结构判定。
    结构是否达成，仍以拓扑规则是否通过为准；如果某条规则在拓扑上已通过，
    但用于语义复核的标准字段不完整，就在面板里给出提示，帮助用户理解为什么
    后续语义复核置信度较低。
    """
    extracted_edges = extracted_edges or {}
    field_values = _collect_field_values(extracted_edges, source_text)
    allowed_rule_ids = {str(item).strip() for item in (stage_rule_ids or RULE_REVIEW_SPECS.keys()) if str(item).strip()}
    notes: List[Dict[str, Any]] = []

    for rule_id in sorted(allowed_rule_ids):
        spec = RULE_REVIEW_SPECS.get(rule_id)
        if not spec:
            continue
        left_key, left_value = _pick_first(field_values, list(spec.get("left_keys", [])))
        right_key, right_value = _pick_first(field_values, list(spec.get("right_keys", [])))
        left_real = _has_real_value(left_value)
        right_real = _has_real_value(right_value)
        if left_real and right_real:
            continue

        hits = _collect_rule_structural_hits(rule_id, field_values, extracted_edges)
        if not left_real and not right_real:
            issue = f"字段完备度提示：该规则虽然在拓扑上已形成相关结构，但当前尚未标准化写出“{_display_key_label(left_key)}”与“{_display_key_label(right_key)}”两侧字段；这不会直接否掉结构判定，但会降低后续语义复核的置信度。"
        elif not left_real:
            issue = f"字段完备度提示：该规则虽然在拓扑上已形成相关结构，但“{_display_key_label(left_key)}”这一侧仍未标准化写出；这不会直接否掉结构判定，但会降低后续语义复核的置信度。"
        else:
            issue = f"字段完备度提示：该规则虽然在拓扑上已形成相关结构，但“{_display_key_label(right_key)}”这一侧仍未标准化写出；这不会直接否掉结构判定，但会降低后续语义复核的置信度。"
        if hits:
            issue += f" 当前已命中的相关字段包括：{'；'.join(hits[:4])}。"

        notes.append({
            "rule": rule_id,
            "name": RULE_NAMES.get(rule_id, rule_id),
            "issue": issue,
            "severity": RULE_DEFAULT_SEVERITY.get(rule_id, "medium"),
            "source": "semantic_guard_field_note",
            "field_completeness_note": True,
            "left_key": left_key,
            "left_value": left_value,
            "right_key": right_key,
            "right_value": right_value,
            "structural_hit_fields": hits,
        })

    return notes


# 兼容旧调用名
build_structural_field_alerts = build_structural_field_notes


def _build_contextual_missing_semantic_check(rule_id: str, field_values: Dict[str, List[str]], source_text: str) -> Dict[str, Any]:
    spec = RULE_REVIEW_SPECS.get(rule_id)

    if not spec:
        return _build_missing_semantic_placeholder(rule_id)

    left_key, left_value = _pick_first(field_values, spec["left_keys"])
    right_key, right_value = _pick_first(field_values, spec["right_keys"])
    left_real = _has_real_value(left_value)
    right_real = _has_real_value(right_value)
    excerpt = _find_supporting_excerpt(source_text, left_value, right_value)

    if not left_real and not right_real:
        status = "suspicious"
        severity = "high"
        reason = f"当前规则虽然通过了结构判定，但用于语义复核的两侧关键字段都没有被明确写出来，暂时无法证明“{spec['dimension']}”真的成立。"
        evidence_hint = spec["hint"]
    elif not left_real or not right_real:
        missing_side = "左侧" if not left_real else "右侧"
        status = "suspicious"
        severity = "high"
        reason = f"当前规则虽然通过了结构判定，但{missing_side}关键字段仍未明确写出，语义复核对象不完整，暂时不能视为语义成立。"
        evidence_hint = spec["hint"]
    else:
        status = "needs_evidence"
        severity = "medium"
        reason = spec["reason"]
        evidence_hint = spec["hint"]

    return _build_check(
        check_id=f"semantic_placeholder::{rule_id}",
        dimension=spec["dimension"],
        rule_id=rule_id,
        left_key=left_key,
        left_value=left_value,
        right_key=right_key,
        right_value=right_value,
        status=status,
        severity=severity,
        reason=reason,
        evidence_hint=evidence_hint,
        source_excerpt=excerpt,
    )

def _aggregate_alerts(checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_rule: Dict[str, Dict[str, Any]] = {}
    status_labels = {
        "contradictory": "明显冲突",
        "suspicious": "高风险存疑",
        "needs_evidence": "需补证据",
    }
    for check in checks:
        if check.get("status") not in {"contradictory", "suspicious", "needs_evidence"}:
            continue
        rule_id = str(check.get("rule_id") or "")
        if not rule_id:
            continue
        status = str(check.get("status") or "needs_evidence")
        alert = {
            "rule": rule_id,
            "name": RULE_NAMES.get(rule_id, rule_id),
            "issue": f"{status_labels.get(status, '语义待确认')}：{_display_key_label(check.get('left_key'))}={check.get('left_value')} 与 {_display_key_label(check.get('right_key'))}={check.get('right_value')} 的语义适配存在问题。{check.get('reason')}",
            "severity": check.get("severity") or ("medium" if status == "needs_evidence" else "high"),
            "source": "semantic_guard",
            "semantic_status": status,
            "left_key": check.get('left_key'),
            "left_value": check.get('left_value'),
            "right_key": check.get('right_key'),
            "right_value": check.get('right_value'),
            "reason": check.get('reason'),
        }
        previous = by_rule.get(rule_id)
        if previous is None:
            by_rule[rule_id] = alert
            continue
        prev_rank = SEVERITY_RANK.get(previous.get("severity", "medium"), 0)
        new_rank = SEVERITY_RANK.get(alert.get("severity", "medium"), 0)
        if new_rank > prev_rank:
            by_rule[rule_id] = alert
        elif new_rank == prev_rank and len(alert["issue"]) > len(previous["issue"]):
            by_rule[rule_id] = alert
    return list(by_rule.values())


def _build_edge_quality(checks: List[Dict[str, Any]]) -> Dict[str, Any]:
    edge_quality: Dict[str, Dict[str, Any]] = {}
    for check in checks:
        rule_id = str(check.get("rule_id") or "")
        bucket = edge_quality.setdefault(
            rule_id,
            {
                "worst_status": "unknown",
                "worst_severity": "low",
                "count": 0,
                "risky_count": 0,
                "items": [],
            },
        )
        bucket["count"] += 1
        if check.get("status") in {"contradictory", "suspicious"}:
            bucket["risky_count"] += 1
        bucket["worst_status"] = _best_status(bucket["worst_status"], str(check.get("status") or "unknown"))
        bucket["worst_severity"] = _severity_max(bucket["worst_severity"], str(check.get("severity") or "low"))
        bucket["items"].append(check)
    return edge_quality


def _pair_or_placeholder(
    left_values: List[str],
    right_values: List[str],
    *,
    left_missing_placeholder: str = "(待补充)",
    right_missing_placeholder: str = "(待补充)",
) -> List[Tuple[str, str]]:
    if left_values and right_values:
        return [(l, r) for l in left_values for r in right_values]
    if left_values:
        return [(l, right_missing_placeholder) for l in left_values]
    if right_values:
        return [(left_missing_placeholder, r) for r in right_values]
    return []


def _limit_pairs(pairs: List[Tuple[str, str]], limit: int = 6) -> List[Tuple[str, str]]:
    return pairs[:limit]


def _has_number(value: str) -> bool:
    return bool(re.search(r"\d", str(value or "")))


def _looks_negative_or_empty(value: str) -> bool:
    lowered = _normalize_text(value)
    return any(token in lowered for token in ["无明确", "暂无", "没有", "缺少", "待补充", "待定", "空白", "未"] )


def _is_generic_claim(text: str) -> bool:
    lowered = _normalize_text(text)
    if not lowered:
        return True
    has_generic = any(token in lowered for token in [item.lower() for item in GENERIC_DIFFERENTIATION_PATTERNS + GENERIC_SOLUTION_PATTERNS])
    has_metric = bool(re.search(r"\d", lowered)) or _contains_any(lowered, ROI_VALUE_PATTERNS)
    has_domain = bool(_infer_domain_tags(lowered))
    return has_generic and not has_metric and not has_domain


def _evaluate_field_type_consistency(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []

    for idx, value in enumerate(field_values.get("Target_Customer", [])):
        if _infer_channel_profiles(value) and not _infer_audience_tags(value):
            checks.append(
                _build_check(
                    check_id=f"field_type_customer::{idx}",
                    dimension="字段类型一致性",
                    rule_id="R6",
                    left_key="Target_Customer",
                    left_value=value,
                    right_key="Marketing_Channel",
                    right_value="(待核对字段)",
                    status="suspicious",
                    severity="high",
                    reason="该值更像渠道/平台，而不像目标客群，疑似发生了字段误挂或抽取漂移。",
                    evidence_hint="请检查：这是目标用户，还是投放渠道/触达平台。",
                )
            )

    for idx, value in enumerate(field_values.get("Marketing_Channel", [])):
        if _infer_audience_tags(value) and not _infer_channel_profiles(value):
            checks.append(
                _build_check(
                    check_id=f"field_type_channel::{idx}",
                    dimension="字段类型一致性",
                    rule_id="R6",
                    left_key="Marketing_Channel",
                    left_value=value,
                    right_key="Target_Customer",
                    right_value="(待核对字段)",
                    status="suspicious",
                    severity="high",
                    reason="该值更像用户画像，而不像渠道描述，疑似发生了字段误挂或抽取漂移。",
                    evidence_hint="请检查：这是目标客群，还是实际的触达渠道。",
                )
            )

    return checks


def _evaluate_channel_customer(field_values: Dict[str, List[str]], source_text: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    customers = field_values.get("Target_Customer", [])
    channels = field_values.get("Marketing_Channel", [])
    proxy_tags = _infer_audience_tags(source_text)
    has_proxy_user_cue = _contains_any(source_text, PROXY_USER_CUES)

    for idx, customer in enumerate(customers):
        customer_tags = _infer_audience_tags(customer)
        for jdx, channel in enumerate(channels):
            channel_profiles = _infer_channel_profiles(channel)
            if not channel_profiles:
                continue

            status = "confirmed"
            severity = "low"
            reason = "当前渠道与客群未发现明显的语义适配冲突。"
            evidence_hint = "可继续补充首批用户触达路径、转化链路与实际投放数据。"

            for profile in channel_profiles:
                weak_for = set(profile.get("weak_for", []))
                affinity = set(profile.get("affinity", []))
                customer_tag_set = set(customer_tags)
                proxy_tag_set = set(proxy_tags)

                if customer_tag_set.intersection(weak_for):
                    if has_proxy_user_cue and proxy_tag_set.intersection(affinity):
                        status = _best_status(status, "needs_evidence")
                        severity = _severity_max(severity, "medium")
                        reason = (
                            f"识别到目标客群“{customer}”与渠道“{profile.get('label')}”天然匹配度偏低，但文本中出现了“子女/照护者/采购者”等代理触达人线索，"
                            "因此不是直接判错，而是需要你明确‘真正被触达的人是谁’。"
                        )
                        evidence_hint = "请补充：实际投放对象是谁、谁点击广告、谁做购买决策、谁最终使用产品。"
                    else:
                        status = _best_status(status, "suspicious")
                        severity = _severity_max(severity, "high")
                        reason = (
                            f"渠道“{profile.get('label')}”通常并不是“{customer}”的高自然触达渠道；如果它承担首要获客角色，"
                            "目前文本缺少对代理决策人、代际传播链路或特殊投放场景的解释。"
                        )
                        evidence_hint = "请说明：为什么这个渠道能有效接触该客群；若真实触达对象并非该客群本人，也请显式写清。"
                elif customer_tag_set and customer_tag_set.intersection(affinity):
                    status = _best_status(status, "confirmed")
                    severity = _severity_max(severity, "low")
                    reason = f"渠道“{profile.get('label')}”与客群“{customer}”在常见传播路径上基本一致。"

            checks.append(
                _build_check(
                    check_id=f"channel_customer::{idx}-{jdx}",
                    dimension="渠道 × 客群",
                    rule_id="R6",
                    left_key="Target_Customer",
                    left_value=customer,
                    right_key="Marketing_Channel",
                    right_value=channel,
                    status=status,
                    severity=severity,
                    reason=reason,
                    evidence_hint=evidence_hint,
                )
            )
    return checks


def _evaluate_narrative_causality(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    pains = field_values.get("Core_Pain_Point", []) + field_values.get("Current_Pain", [])
    solutions = field_values.get("Solution", []) + field_values.get("Value_Proposition", [])

    for idx, pain in enumerate(pains):
        pain_domains = set(_infer_domain_tags(pain))
        for jdx, solution in enumerate(solutions):
            solution_domains = set(_infer_domain_tags(solution))
            status = "confirmed"
            severity = "low"
            reason = "痛点与方案叙事基本处在同一问题域内。"
            evidence_hint = "可继续用“上线前后动作变化”补强因果链。"

            if pain_domains and solution_domains and pain_domains.isdisjoint(solution_domains):
                status = "suspicious"
                severity = "high"
                reason = "痛点描述与方案描述落在两个不同领域，像是把不相干的需求和产品硬拼在一起。"
                evidence_hint = "请重写：用户究竟因为什么痛，方案如何直接改变这个痛点，而不是只报功能名。"
            elif _is_generic_claim(solution):
                status = "needs_evidence"
                severity = "medium"
                reason = "方案表达偏空泛，更像“做一个平台/系统”而不是解释它如何直接改变痛点。"
                evidence_hint = "请补充：如果没有你的方案，用户今天怎么凑合；有了之后哪个关键动作被改变。"

            checks.append(
                _build_check(
                    check_id=f"narrative::{idx}-{jdx}",
                    dimension="痛点 × 方案因果",
                    rule_id="R3",
                    left_key="Core_Pain_Point",
                    left_value=pain,
                    right_key="Solution/Value_Proposition",
                    right_value=solution,
                    status=status,
                    severity=severity,
                    reason=reason,
                    evidence_hint=evidence_hint,
                )
            )
    return checks


def _evaluate_competition_realism(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    alternatives = field_values.get("Alternative_Solution", [])
    competitors = field_values.get("Competitor_Pool", [])
    pains = field_values.get("Current_Pain", []) + field_values.get("Core_Pain_Point", [])

    if competitors:
        for idx, comp in enumerate(competitors):
            status = "confirmed"
            severity = "low"
            reason = "已看到明确竞品/替代对象表达。"
            evidence_hint = "可继续补充：和它相比你到底强在何处。"
            if _contains_any(comp, NO_COMPETITION_PATTERNS):
                status = "suspicious"
                severity = "critical"
                reason = "文本直接把竞争格局描述成“没有竞争对手/市场空白”，这通常意味着忽略了旧习惯、替代方案或隐形竞品。"
                evidence_hint = "请至少说出：用户今天不用你时靠什么凑合解决问题。"
            elif _contains_any(comp, ["很多", "若干", "一些", "传统方式"]) and not _contains_any(comp, ["app", "平台", "人工", "线下", "人工服务", "excel", "微信", "电话"]):
                status = "needs_evidence"
                severity = "medium"
                reason = "竞品表述偏笼统，缺少可对比的具体对象，容易把“竞争分析”写成空话。"
                evidence_hint = "请补充 1-3 个明确对手或旧方案，并说明它们各自的优缺点。"
            checks.append(
                _build_check(
                    check_id=f"competition::{idx}",
                    dimension="竞争格局真实性",
                    rule_id="R8",
                    left_key="Competitor_Pool",
                    left_value=comp,
                    right_key="Alternative_Solution",
                    right_value=" / ".join(alternatives[:2]) if alternatives else "(待补充)",
                    status=status,
                    severity=severity,
                    reason=reason,
                    evidence_hint=evidence_hint,
                )
            )

    if pains and not (alternatives or competitors):
        for idx, pain in enumerate(pains[:2]):
            checks.append(
                _build_check(
                    check_id=f"competition_missing::{idx}",
                    dimension="竞争格局真实性",
                    rule_id="R8",
                    left_key="Core_Pain_Point/Current_Pain",
                    left_value=pain,
                    right_key="Competitor_Pool",
                    right_value="(待补充)",
                    status="suspicious",
                    severity="high",
                    reason="你描述了痛点，但完全没有说明用户目前靠什么替代方案解决，容易掉进“只有我能做”的幻觉。",
                    evidence_hint="请补充：用户现在怎么做、为什么它不够好、你的切入点在哪。",
                )
            )
    return checks


def _evaluate_market_funnel_consistency(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    tam_values = field_values.get("TAM", [])
    sam_values = field_values.get("SAM", [])
    som_values = field_values.get("SOM", [])

    tam_amounts = [value for value in (_extract_amount(item) for item in tam_values) if value is not None]
    sam_amounts = [value for value in (_extract_amount(item) for item in sam_values) if value is not None]
    som_amounts = [value for value in (_extract_amount(item) for item in som_values) if value is not None]

    if tam_values or sam_values or som_values:
        tam_text = " / ".join(tam_values[:1]) if tam_values else "(待补充)"
        sam_text = " / ".join(sam_values[:1]) if sam_values else "(待补充)"
        som_text = " / ".join(som_values[:1]) if som_values else "(待补充)"
        status = "confirmed"
        severity = "low"
        reason = "TAM/SAM/SOM 漏斗关系未发现明显冲突。"
        evidence_hint = "建议继续补充口径来源、时间范围和测算方法。"

        if tam_amounts and sam_amounts and som_amounts:
            tam = tam_amounts[0]
            sam = sam_amounts[0]
            som = som_amounts[0]
            if not (tam >= sam >= som):
                status = "contradictory"
                severity = "high"
                reason = "TAM/SAM/SOM 数值顺序出现反转，漏斗口径本身不成立。"
                evidence_hint = "请重新核对定义：TAM ≥ SAM ≥ SOM，且三者不能混用不同口径。"
            elif tam > 0 and som / tam > 0.3:
                status = "suspicious"
                severity = "medium"
                reason = "SOM 在总市场中的占比偏大，像是把“最终可拿下的份额”写得过于乐观。"
                evidence_hint = "请说明：为什么你在初期就能拿到这么高的市场份额。"
        elif sum(1 for item in [tam_values, sam_values, som_values] if item) < 2:
            status = "needs_evidence"
            severity = "medium"
            reason = "市场规模只给出了单点，没有形成从总市场到可获得市场的漏斗。"
            evidence_hint = "至少补齐两层以上，并说明每一层的筛选条件。"
        elif any(_contains_any(text, GENERIC_MARKET_PATTERNS) for text in tam_values + sam_values + som_values):
            status = "needs_evidence"
            severity = "medium"
            reason = "市场规模描述过于泛化，更像口号而不是有边界的测算。"
            evidence_hint = "请把“全国所有人”收缩到可触达、可验证、可拿下的细分群体。"

        checks.append(
            _build_check(
                check_id="market_funnel::0",
                dimension="市场漏斗一致性",
                rule_id="R9",
                left_key="TAM/SAM",
                left_value=f"TAM={tam_text} ; SAM={sam_text}",
                right_key="SOM",
                right_value=som_text,
                status=status,
                severity=severity,
                reason=reason,
                evidence_hint=evidence_hint,
            )
        )
    return checks


def _evaluate_innovation_against_competition(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    differentiation = field_values.get("Differentiation", []) + field_values.get("Value_Proposition", [])
    metrics = field_values.get("Verifiable_Metric", [])
    experiments = field_values.get("Control_Experiment", [])
    competitors = field_values.get("Competitor_Pool", []) + field_values.get("Alternative_Solution", [])

    if not differentiation:
        return checks

    for idx, diff in enumerate(differentiation[:3]):
        status = "confirmed"
        severity = "low"
        reason = "创新表述具备一定可验证性或对标对象。"
        evidence_hint = "建议继续补充：胜出的证据来自什么指标。"

        if _is_generic_claim(diff) and competitors and not (metrics or experiments):
            status = "suspicious"
            severity = "high"
            reason = "你的差异化表述更像“更智能/更高效”的宣传语，但没有给出竞品对照、可验证指标或实验结果。"
            evidence_hint = "请补充：与哪个对手比、比什么指标、提升了多少。"
        elif competitors and not (metrics or experiments):
            status = "needs_evidence"
            severity = "medium"
            reason = "虽然提到了竞争对象，但差异化还没有落到可验证证据。"
            evidence_hint = "请补充一项可测指标，或一个和现有方案的对照实验。"

        checks.append(
            _build_check(
                check_id=f"innovation::{idx}",
                dimension="创新 × 竞争验证",
                rule_id="R10",
                left_key="Differentiation/Value_Proposition",
                left_value=diff,
                right_key="Competitor_Pool/Control_Experiment",
                right_value=(" / ".join((competitors[:1] + metrics[:1] + experiments[:1])) or "(待补充)"),
                status=status,
                severity=severity,
                reason=reason,
                evidence_hint=evidence_hint,
            )
        )
    return checks


def _evaluate_price_customer(field_values: Dict[str, List[str]], source_text: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    customers = field_values.get("Target_Customer", [])
    prices = field_values.get("Price", [])
    has_premium_cue = _contains_any(source_text, PREMIUM_PRICE_CUES)

    for idx, customer in enumerate(customers):
        customer_tags = set(_infer_audience_tags(customer))
        for jdx, price_text in enumerate(prices):
            amount = _extract_amount(price_text)
            if amount is None:
                continue

            status = "confirmed"
            severity = "low"
            reason = "当前价格与客群未发现明显的支付矛盾。"
            evidence_hint = "建议继续补充价格依据、付费方与复购逻辑。"

            if customer_tags.intersection({"elderly", "student", "farmer"}) and amount >= 999:
                status = "suspicious" if not has_premium_cue else "needs_evidence"
                severity = "high" if not has_premium_cue else "medium"
                reason = (
                    f"识别到客群“{customer}”与高价位“{price_text}”的组合。这个组合不是绝对不成立，"
                    "但若没有更高收入子群、机构报销或代付方设计，支付意愿与支付能力都可能承压。"
                )
                evidence_hint = "请补充：真实付费方是谁、价格对比锚点是什么、为什么该客群愿意接受这一价格。"
            elif customer_tags.intersection({"elderly", "student", "farmer"}) and amount >= 299:
                status = "needs_evidence"
                severity = "medium"
                reason = f"客群“{customer}”对“{price_text}”的价格敏感度可能偏高，建议补充支付场景与价格依据。"
                evidence_hint = "请说明：价格是否由子女/机构承担，或者是否存在高频刚需和强 ROI 支撑。"

            checks.append(
                _build_check(
                    check_id=f"price_customer::{idx}-{jdx}",
                    dimension="客群 × 定价",
                    rule_id="R7",
                    left_key="Target_Customer",
                    left_value=customer,
                    right_key="Price",
                    right_value=price_text,
                    status=status,
                    severity=severity,
                    reason=reason,
                    evidence_hint=evidence_hint,
                )
            )
    return checks


def _evaluate_unit_economics(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    ltv_values = field_values.get("LTV", [])
    cac_values = field_values.get("CAC", [])

    pairs = _pair_or_placeholder(ltv_values, cac_values)
    for idx, (ltv_text, cac_text) in enumerate(pairs):
        ltv = _extract_amount(ltv_text) if ltv_text != "(待补充)" else None
        cac = _extract_amount(cac_text) if cac_text != "(待补充)" else None

        status = "unknown"
        severity = "low"
        reason = "当前单客收益/获客成本信息不足。"
        evidence_hint = "请至少给出 LTV 与 CAC 的粗算值，再谈规模化。"

        if ltv is not None and cac is not None:
            status = "confirmed"
            severity = "low"
            reason = "LTV/CAC 数值未发现明显冲突。"
            evidence_hint = "建议继续补充回本周期与留存假设。"
            if ltv <= cac:
                status = "contradictory"
                severity = "critical"
                reason = "当前 LTV 小于或等于 CAC，意味着单客越做越亏，单位经济模型本身不成立。"
                evidence_hint = "请重新核对：单客收入来自哪里，获客成本是否被低估，是否应换更低成本渠道或更高 ARPU 方案。"
            elif cac > 0 and ltv / cac < 1.5:
                status = "suspicious"
                severity = "high"
                reason = "LTV/CAC 比值过低，留给履约、售后和组织成本的安全垫很薄。"
                evidence_hint = "请说明：除了首单收入，还有没有复购、加购或高毛利增值服务。"
            elif cac > 0 and ltv / cac < 3:
                status = "needs_evidence"
                severity = "medium"
                reason = "LTV/CAC 刚刚拉开，但模型仍偏脆弱，稍有获客波动就可能失稳。"
                evidence_hint = "请补充：乐观/中性/保守三档下的单客经济对比。"
        elif ltv_text != "(待补充)" or cac_text != "(待补充)":
            status = "needs_evidence"
            severity = "medium"
            reason = "只给出了 LTV 或 CAC 的一边，无法完成最基本的单位经济闭环。"

        checks.append(
            _build_check(
                check_id=f"unit_economics::{idx}",
                dimension="LTV × CAC",
                rule_id="R11",
                left_key="LTV",
                left_value=ltv_text,
                right_key="CAC",
                right_value=cac_text,
                status=status,
                severity=severity,
                reason=reason,
                evidence_hint=evidence_hint,
            )
        )
    return checks


def _collect_cost_candidates(field_values: Dict[str, List[str]]) -> List[str]:
    values: List[str] = []
    for key in ["Variable_Cost", "Fulfill_Cost", "Cost_Structure", "Fixed_Cost"]:
        values.extend(field_values.get(key, []))
    return values


def _evaluate_pricing_space(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    prices = field_values.get("Price", [])
    costs = _collect_cost_candidates(field_values)
    if not prices:
        return checks

    for idx, price_text in enumerate(prices):
        price = _extract_amount(price_text)
        status = "needs_evidence"
        severity = "medium"
        reason = "存在定价表达，但成本与利润空间仍不够可计算。"
        evidence_hint = "请补充：至少一个单位履约成本或变动成本。"
        right_value = " / ".join(costs[:2]) if costs else "(待补充)"

        numeric_costs = [value for value in (_extract_amount(item) for item in costs) if value is not None]
        if price is not None and numeric_costs:
            unit_cost = min(numeric_costs)
            status = "confirmed"
            severity = "low"
            reason = "价格与已披露成本未见明显倒挂。"
            evidence_hint = "建议继续拆分：履约、售后、渠道返佣与固定成本摊销。"
            if unit_cost >= price:
                status = "contradictory"
                severity = "high"
                reason = "已披露的单位成本已经接近或超过售价，利润空间出现明显倒挂。"
                evidence_hint = "请检查：定价是否过低，或成本是否遗漏了分摊逻辑。"
            elif unit_cost / price >= 0.7:
                status = "suspicious"
                severity = "high"
                reason = "已披露成本占售价比例过高，毛利安全垫很薄，稍有波动就会挤压利润空间。"
                evidence_hint = "请说明：规模化后成本是否能下降，或者是否有高毛利附加服务支撑。"
            elif unit_cost / price >= 0.5:
                status = "needs_evidence"
                severity = "medium"
                reason = "基础毛利不算宽裕，建议进一步拆开固定成本与变动成本。"
        elif price is not None:
            if _contains_any(" ".join(costs), ["高", "很多", "较大", "不低", "昂贵"]):
                status = "needs_evidence"
                severity = "medium"
                reason = "文本暗示成本不低，但没有给出任何可核算数字，利润空间仍像黑盒。"

        checks.append(
            _build_check(
                check_id=f"pricing_space::{idx}",
                dimension="价格 × 成本",
                rule_id="R12",
                left_key="Price",
                left_value=price_text,
                right_key="Cost_Structure/Fulfill_Cost",
                right_value=right_value,
                status=status,
                severity=severity,
                reason=reason,
                evidence_hint=evidence_hint,
            )
        )
    return checks


def _evaluate_cash_flow_health(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    account_values = field_values.get("Account_Period", [])
    startup_values = field_values.get("Startup_Capital", [])
    burn_values = field_values.get("Burn_Rate", [])

    if not (account_values or startup_values or burn_values):
        return checks

    account_days = _extract_days(account_values[0]) if account_values else None
    startup_capital = _extract_amount(startup_values[0]) if startup_values else None
    monthly_burn = _extract_monthly_amount(burn_values[0]) if burn_values else None

    status = "needs_evidence"
    severity = "medium"
    reason = "现金流缓冲能力还不够清楚。"
    evidence_hint = "请补充：账期多久、月 burn 多少、启动资金能撑多久。"

    if account_days is not None:
        status = "confirmed"
        severity = "low"
        reason = "已看到账期相关描述。"
        if startup_capital is None and monthly_burn is None and account_days >= 60:
            status = "suspicious"
            severity = "high"
            reason = "存在较长账期，但没有给出启动资金或 burn rate，现金流缓冲完全不可见。"
        elif startup_capital is not None and monthly_burn is not None and monthly_burn > 0:
            runway_months = startup_capital / monthly_burn
            if runway_months < 3:
                status = "suspicious"
                severity = "critical"
                reason = "按当前 burn rate 估算，启动资金可支撑时间过短，而账期又较长，现金流断裂风险很高。"
                evidence_hint = "请说明：是否有预付款、里程碑回款或垫资方；否则账期会直接压垮现金流。"
            elif account_days >= 90 and runway_months < 6:
                status = "suspicious"
                severity = "high"
                reason = "账期很长而资金缓冲不厚，稍有回款延迟就可能出现资金链紧张。"
            elif runway_months < 9:
                status = "needs_evidence"
                severity = "medium"
                reason = "账期与资金缓冲虽未直接冲突，但安全垫仍不算厚。"
        elif account_days >= 90:
            status = "needs_evidence"
            severity = "medium"
            reason = "存在超长账期，但未提供足够信息证明项目能扛过回款窗口。"

    checks.append(
        _build_check(
            check_id="cash_flow::0",
            dimension="账期 × 资金缓冲",
            rule_id="R13",
            left_key="Account_Period",
            left_value=account_values[0] if account_values else "(待补充)",
            right_key="Startup_Capital/Burn_Rate",
            right_value=" / ".join((startup_values[:1] + burn_values[:1])) if (startup_values or burn_values) else "(待补充)",
            status=status,
            severity=severity,
            reason=reason,
            evidence_hint=evidence_hint,
        )
    )
    return checks


def _evaluate_financial_reasonableness(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    models = field_values.get("Financial_Model", [])
    assumptions = field_values.get("Key_Assumption", [])
    sensitivity = field_values.get("Sensitivity_Analysis", [])

    if not (models or assumptions or sensitivity):
        return checks

    model_text = " / ".join(models[:1]) if models else "(待补充)"
    assumption_text = " / ".join(assumptions[:1]) if assumptions else "(待补充)"
    sensitivity_text = " / ".join(sensitivity[:1]) if sensitivity else "(待补充)"
    combined = " ".join(models + assumptions)

    status = "confirmed"
    severity = "low"
    reason = "财务模型表述未发现明显的激进跳跃。"
    evidence_hint = "建议继续保留保守/中性/乐观三档假设。"

    if _contains_any(combined, AGGRESSIVE_FINANCIAL_PATTERNS) and not sensitivity:
        status = "suspicious"
        severity = "high"
        reason = "财务假设明显偏激进，但没有给出敏感性分析或回撤场景，预测像“立 Flag”而不是模型。"
        evidence_hint = "请补充：关键变量若下降 20%/50%，收入和现金流会怎样变化。"
    elif (models or assumptions) and not sensitivity:
        status = "needs_evidence"
        severity = "medium"
        reason = "已有财务模型或关键假设，但还没看到任何敏感性分析，风险承受边界不清楚。"
        evidence_hint = "至少补一条：如果转化率、客单价或复购率不达预期，会怎样。"

    checks.append(
        _build_check(
            check_id="financial_reasonableness::0",
            dimension="财务假设 × 敏感性分析",
            rule_id="R18",
            left_key="Financial_Model/Key_Assumption",
            left_value=f"{model_text} ; {assumption_text}",
            right_key="Sensitivity_Analysis",
            right_value=sensitivity_text,
            status=status,
            severity=severity,
            reason=reason,
            evidence_hint=evidence_hint,
        )
    )
    return checks


def _evaluate_frequency_revenue(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    frequencies = field_values.get("Usage_Frequency", [])
    revenues = field_values.get("Revenue_Model", [])

    for idx, freq in enumerate(frequencies):
        freq_low = _contains_any(freq, LOW_FREQUENCY_PATTERNS)
        freq_high = _contains_any(freq, HIGH_FREQUENCY_PATTERNS)
        for jdx, revenue in enumerate(revenues):
            is_subscription = _contains_any(revenue, SUBSCRIPTION_PATTERNS)
            is_transaction = _contains_any(revenue, TRANSACTION_PATTERNS)

            status = "confirmed"
            severity = "low"
            reason = "当前使用频次与收入方式没有发现明显冲突。"
            evidence_hint = "可继续补充复购率、留存率与收入频次的对应关系。"

            if freq_low and is_subscription:
                status = "suspicious"
                severity = "high"
                reason = "文本同时表现出低频/偶发使用特征，却采用会员/订阅型收费；这类组合很容易出现续费动力不足。"
                evidence_hint = "请解释：为什么用户即使低频也会持续付费，或者是否应该改成按次/按单收费。"
            elif freq_high and is_transaction:
                status = "needs_evidence"
                severity = "medium"
                reason = "场景呈现为高频使用，但收入设计更像一次性或按单收费，建议补充规模化后的收入上限。"
                evidence_hint = "请说明：高频场景下如何避免收入天花板过低。"
            elif not (freq_low or freq_high) and not (is_subscription or is_transaction):
                status = "unknown"
                severity = "low"
                reason = "当前频次或收入模型描述过于模糊，暂时无法做高可信判断。"
                evidence_hint = "请补充：用户多久使用一次，以及你打算按什么频率收费。"

            checks.append(
                _build_check(
                    check_id=f"frequency_revenue::{idx}-{jdx}",
                    dimension="频次 × 收入方式",
                    rule_id="R19",
                    left_key="Usage_Frequency",
                    left_value=freq,
                    right_key="Revenue_Model",
                    right_value=revenue,
                    status=status,
                    severity=severity,
                    reason=reason,
                    evidence_hint=evidence_hint,
                )
            )
    return checks


def _evaluate_tech_business_alignment(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    tech_values = field_values.get("Tech_Route", []) + field_values.get("Core_Advantage", []) + field_values.get("IP", [])
    value_values = field_values.get("Value_Proposition", []) + field_values.get("Solution", [])
    customers = field_values.get("Target_Customer", [])

    if not tech_values:
        return checks

    combined_value = " ".join(value_values)
    combined_customer = " ".join(customers)
    value_domains = set(_infer_domain_tags(combined_value))
    customer_domains = set(_infer_domain_tags(combined_customer))

    for idx, tech in enumerate(tech_values[:3]):
        tech_domains = set(_infer_domain_tags(tech))
        route_is_advanced = _contains_any(tech, TECH_COMPLEXITY_PATTERNS["advanced_tech"])

        status = "confirmed"
        severity = "low"
        reason = "技术表达与商业价值暂未发现明显脱节。"
        evidence_hint = "建议继续解释：该技术究竟带来了什么用户价值或商业优势。"

        if route_is_advanced and not value_values:
            status = "suspicious"
            severity = "high"
            reason = "讲了复杂技术，但没有对应的价值主张或方案表达，技术像独立展台，没有进入商业叙事。"
            evidence_hint = "请补充：这项技术到底让谁得到什么可感知的提升。"
        elif route_is_advanced and value_values and not _contains_any(combined_value, ROI_VALUE_PATTERNS) and _is_generic_claim(combined_value):
            status = "needs_evidence"
            severity = "medium"
            reason = "技术路线不轻，但价值表达仍然很泛，尚未看到“技术如何转成用户收益/商业收益”。"
            evidence_hint = "请补充：因为技术存在，所以成本、时效、准确率或交付方式具体改善了什么。"
        elif tech_domains and (value_domains or customer_domains) and tech_domains.isdisjoint(value_domains.union(customer_domains)):
            status = "needs_evidence"
            severity = "medium"
            reason = "技术叙事和商业对象的领域关键词联系不强，建议进一步解释两者如何闭环。"
            evidence_hint = "请补充：技术服务的是哪个环节、哪个用户、哪项关键指标。"

        checks.append(
            _build_check(
                check_id=f"tech_business::{idx}",
                dimension="技术 × 商业价值",
                rule_id="R2",
                left_key="Tech_Route/Core_Advantage/IP",
                left_value=tech,
                right_key="Value_Proposition/Target_Customer",
                right_value=(" / ".join((value_values[:1] + customers[:1])) or "(待补充)"),
                status=status,
                severity=severity,
                reason=reason,
                evidence_hint=evidence_hint,
            )
        )
    return checks


def _evaluate_compliance_industry(field_values: Dict[str, List[str]], source_text: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    industries = field_values.get("Industry", [])
    data_sources = field_values.get("Data_Source", [])
    policy_constraints = field_values.get("Policy_Constraints", [])

    combined_source = " ".join(industries + data_sources + [source_text])
    strict_tags = [tag for tag, patterns in STRICT_REGULATION_PATTERNS.items() if _contains_any(combined_source, patterns)]
    if not strict_tags and not policy_constraints:
        return checks

    status = "confirmed"
    severity = "low"
    reason = "已看到一定的行业/数据/政策约束表达。"
    evidence_hint = "建议继续指向具体监管要求、资质或数据授权路径。"

    if strict_tags and not policy_constraints:
        status = "suspicious"
        severity = "high"
        reason = f"项目触及 {', '.join(strict_tags)} 等强监管/高隐私场景，但没有看到任何具体的政策约束或合规路径。"
        evidence_hint = "请补充：涉及哪些监管要求、数据授权、资质、审查或审批节点。"
    elif policy_constraints and any(_contains_any(item, GENERIC_POLICY_PATTERNS) for item in policy_constraints):
        status = "needs_evidence"
        severity = "medium"
        reason = "虽然写了“合规”，但仍停留在泛泛口号，还没有落到具体规则、牌照或数据边界。"
        evidence_hint = "请明确：哪一条政策、哪个合规动作、由谁负责落实。"

    checks.append(
        _build_check(
            check_id="compliance::0",
            dimension="行业/数据 × 合规约束",
            rule_id="R4",
            left_key="Industry/Data_Source",
            left_value=(" / ".join((industries[:1] + data_sources[:1])) or "(待补充)"),
            right_key="Policy_Constraints",
            right_value=(" / ".join(policy_constraints[:1]) or "(待补充)"),
            status=status,
            severity=severity,
            reason=reason,
            evidence_hint=evidence_hint,
        )
    )
    return checks


def _evaluate_supply_chain_sync(field_values: Dict[str, List[str]], source_text: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    product_forms = field_values.get("Product_Form", [])
    delivery_methods = field_values.get("Delivery_Method", [])
    fulfill_costs = field_values.get("Fulfill_Cost", [])
    suppliers = field_values.get("Supplier_Network", [])
    combined = " ".join(product_forms + delivery_methods + [source_text])

    physical_like = _contains_any(combined, PHYSICAL_PRODUCT_PATTERNS)
    digital_like = _contains_any(combined, DIGITAL_PRODUCT_PATTERNS)

    if not (physical_like or delivery_methods or suppliers or fulfill_costs):
        return checks

    status = "confirmed"
    severity = "low"
    reason = "交付链路信息暂未发现明显错位。"
    evidence_hint = "建议继续补充：供应商、履约成本和交付 SLA。"

    if physical_like and not suppliers:
        status = "suspicious"
        severity = "high"
        reason = "项目明显包含实物/设备/物流交付，但没有看到供应商或上游协同安排，交付链路像悬空。"
        evidence_hint = "请补充：谁供货、谁安装/配送、出了问题由谁负责。"
    elif physical_like and suppliers and not fulfill_costs:
        status = "needs_evidence"
        severity = "medium"
        reason = "有供应侧表达，但履约成本仍是空白，难以评估交付能否跑通。"
        evidence_hint = "请补充：单位物流/安装/售后成本。"
    elif digital_like and fulfill_costs and _contains_any(" ".join(fulfill_costs), ["物流", "仓储", "配送", "安装"]):
        status = "needs_evidence"
        severity = "medium"
        reason = "项目看起来更像数字产品，但履约成本里出现大量实体交付词，建议核对是否混入了不属于核心业务的成本逻辑。"
        evidence_hint = "请区分：数字交付成本、线下实施成本、外包成本分别是什么。"

    checks.append(
        _build_check(
            check_id="supply_chain::0",
            dimension="产品形态 × 供应履约",
            rule_id="R14",
            left_key="Product_Form/Delivery_Method",
            left_value=(" / ".join((product_forms[:1] + delivery_methods[:1])) or "(待补充)"),
            right_key="Supplier_Network/Fulfill_Cost",
            right_value=(" / ".join((suppliers[:1] + fulfill_costs[:1])) or "(待补充)"),
            status=status,
            severity=severity,
            reason=reason,
            evidence_hint=evidence_hint,
        )
    )
    return checks


def _evaluate_cold_start_engine(field_values: Dict[str, List[str]], source_text: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    platform_models = field_values.get("Platform_Model", [])
    seed_users = field_values.get("Seed_Users", [])
    strategies = field_values.get("Cold_Start_Strategy", [])
    combined = " ".join(platform_models + [source_text])

    platform_like = _contains_any(combined, PLATFORM_PATTERNS)
    if not (platform_like or platform_models or seed_users or strategies):
        return checks

    status = "confirmed"
    severity = "low"
    reason = "冷启动链路至少有起点表达。"
    evidence_hint = "建议进一步明确：首批用户从哪里来、为什么愿意留下。"

    if platform_like and not seed_users:
        status = "suspicious"
        severity = "high"
        reason = "项目像双边/平台型业务，但没有看到首批种子用户是谁，容易陷入“平台先搭起来再说”的空转。"
        evidence_hint = "请补充：你先抓哪一边、前 50-100 个种子用户具体从哪来。"
    elif seed_users and not strategies:
        status = "needs_evidence"
        severity = "medium"
        reason = "提到了种子用户，但尚未解释通过什么机制把他们转成持续使用与口碑扩散。"
        evidence_hint = "请补充：补贴、裂变、渠道合作、地推或资源置换等具体策略。"

    checks.append(
        _build_check(
            check_id="cold_start::0",
            dimension="平台模型 × 冷启动",
            rule_id="R15",
            left_key="Platform_Model/Seed_Users",
            left_value=(" / ".join((platform_models[:1] + seed_users[:1])) or "(待补充)"),
            right_key="Cold_Start_Strategy",
            right_value=(" / ".join(strategies[:1]) or "(待补充)"),
            status=status,
            severity=severity,
            reason=reason,
            evidence_hint=evidence_hint,
        )
    )
    return checks


def _evaluate_team_tech(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    routes = field_values.get("Tech_Route", []) + field_values.get("TRL", [])
    teams = field_values.get("Team_Background", [])

    if routes and not teams:
        for idx, route in enumerate(routes[:2]):
            if _contains_any(route, TECH_COMPLEXITY_PATTERNS["advanced_tech"]):
                checks.append(
                    _build_check(
                        check_id=f"team_tech_missing::{idx}",
                        dimension="技术路线 × 团队背景",
                        rule_id="R16",
                        left_key="Tech_Route/TRL",
                        left_value=route,
                        right_key="Team_Background",
                        right_value="(待补充)",
                        status="suspicious",
                        severity="high",
                        reason="文本中出现了较复杂的技术路线，但团队背景完全未说明谁来做、谁负责、谁能交付。",
                        evidence_hint="请补充：团队里谁负责技术、是否有外部合作方、关键岗位是否到位。",
                    )
                )

    for idx, route in enumerate(routes):
        route_is_advanced = _contains_any(route, TECH_COMPLEXITY_PATTERNS["advanced_tech"])
        for jdx, team in enumerate(teams):
            team_is_ready = _contains_any(team, TECH_COMPLEXITY_PATTERNS["team_tech_ready"])

            status = "confirmed"
            severity = "low"
            reason = "当前技术路径与团队背景未发现明显的不匹配。"
            evidence_hint = "建议继续补充关键岗位、交付里程碑与外部合作资源。"

            if route_is_advanced and not team_is_ready:
                status = "needs_evidence"
                severity = "medium"
                reason = "文本中出现了较复杂的技术路线，但团队背景里暂未看到与之强匹配的研发/工程能力描述。"
                evidence_hint = "请补充：谁负责核心技术、是否有外部合作方、关键技术依赖如何落地。"

            checks.append(
                _build_check(
                    check_id=f"team_tech::{idx}-{jdx}",
                    dimension="技术路线 × 团队背景",
                    rule_id="R16",
                    left_key="Tech_Route/TRL",
                    left_value=route,
                    right_key="Team_Background",
                    right_value=team,
                    status=status,
                    severity=severity,
                    reason=reason,
                    evidence_hint=evidence_hint,
                )
            )
    return checks


def _evaluate_resource_feasibility(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    resources = field_values.get("Resource_List", [])
    milestones = field_values.get("Milestone_Plan", [])
    routes = field_values.get("Tech_Route", []) + field_values.get("TRL", [])
    complex_route = any(_contains_any(route, TECH_COMPLEXITY_PATTERNS["advanced_tech"]) for route in routes)

    if not (resources or milestones or routes):
        return checks

    milestone_text = " / ".join(milestones[:1]) if milestones else "(待补充)"
    resource_text = " / ".join(resources[:1]) if resources else "(待补充)"

    status = "confirmed"
    severity = "low"
    reason = "资源与落地计划至少有一部分被显式写出。"
    evidence_hint = "建议进一步拆出关键资源、负责人和阶段目标。"

    if complex_route and not milestones:
        status = "suspicious"
        severity = "high"
        reason = "技术路线不轻，但完全没有里程碑计划，执行看起来像“以后再说”。"
        evidence_hint = "请补充：30/60/90 天分别要做什么、验证什么。"
    elif complex_route and not resources:
        status = "suspicious"
        severity = "medium"
        reason = "技术方案较复杂，却没有说明需要哪些资源、人手、预算或合作方。"
        evidence_hint = "请补充：设备、数据、资金、人力、合作资源各缺什么。"
    elif milestones and not any(_contains_any(item, TIME_MARKERS) or re.search(r"\d", item) for item in milestones):
        status = "needs_evidence"
        severity = "medium"
        reason = "里程碑写了，但缺少时间、阶段或可验证节点，更像愿景而不是执行计划。"
        evidence_hint = "请补充：每个阶段的时间点、交付物和验收标准。"

    checks.append(
        _build_check(
            check_id="resource_feasibility::0",
            dimension="资源 × 里程碑",
            rule_id="R17",
            left_key="Resource_List/Tech_Route",
            left_value=(" / ".join((resources[:1] + routes[:1])) or "(待补充)"),
            right_key="Milestone_Plan",
            right_value=milestone_text,
            status=status,
            severity=severity,
            reason=reason,
            evidence_hint=evidence_hint,
        )
    )
    return checks


def _evaluate_social_value_translation(field_values: Dict[str, List[str]], source_text: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    roadmap = field_values.get("Translation_Roadmap", [])
    scenario = field_values.get("Scenario_Research", [])
    pilot = field_values.get("Pilot_Cooperation", [])
    revenue = field_values.get("Revenue_Model", [])
    combined = " ".join(roadmap + scenario + pilot + [source_text])

    if not _contains_any(combined, SOCIAL_VALUE_PATTERNS):
        return checks

    status = "confirmed"
    severity = "low"
    reason = "社会价值表达已开始和落地路径发生连接。"
    evidence_hint = "建议继续明确：谁付钱、谁合作、如何规模化。"

    if not roadmap and not pilot and not revenue:
        status = "suspicious"
        severity = "high"
        reason = "项目强调社会价值/公益性，但没有看到任何商业转化路线、试点合作或付费机制，容易停在“有意义但不造血”。"
        evidence_hint = "请补充：谁会为这件事买单，或者如何从试点走向可持续收入。"
    elif revenue and not (roadmap or pilot):
        status = "needs_evidence"
        severity = "medium"
        reason = "已经写到了收入方式，但社会价值如何过渡到商业化仍不清楚。"
        evidence_hint = "请补充：从公益试点到付费规模化的中间桥梁是什么。"

    checks.append(
        _build_check(
            check_id="social_translation::0",
            dimension="社会价值 × 商业转化",
            rule_id="R20",
            left_key="Scenario_Research/Pilot_Cooperation",
            left_value=(" / ".join((scenario[:1] + pilot[:1])) or "(待补充)"),
            right_key="Translation_Roadmap/Revenue_Model",
            right_value=(" / ".join((roadmap[:1] + revenue[:1])) or "(待补充)"),
            status=status,
            severity=severity,
            reason=reason,
            evidence_hint=evidence_hint,
        )
    )
    return checks




def _evaluate_market_path_clarity(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    tam = field_values.get("TAM", [])
    sam = field_values.get("SAM", [])
    som = field_values.get("SOM", [])
    customers = field_values.get("Target_Customer", [])
    status = "confirmed"
    severity = "low"
    reason = "商业项目已具备基本市场漏斗表达。"
    evidence_hint = "建议继续补充：各层市场口径和测算依据。"
    if len(tam) + len(sam) + len(som) < 2:
        status = "suspicious"
        severity = "high"
        reason = "缺少完整的 TAM/SAM/SOM 漏斗表达，市场边界不清。"
        evidence_hint = "请补充：总盘子、可服务盘子、首年可获得盘子。"
    elif not customers:
        status = "needs_evidence"
        severity = "medium"
        reason = "市场漏斗已出现，但尚未和具体切入客群绑定。"
        evidence_hint = "请补充：第一批客户是谁、在哪里。"
    return [_build_check(check_id="market_path::0", dimension="TAM/SAM × SOM边界", rule_id="C1", left_key="TAM/SAM", left_value=" / ".join((tam[:1] + sam[:1])) or "(待补充)", right_key="SOM/Target_Customer", right_value=" / ".join((som[:1] + customers[:1])) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]


def _evaluate_profit_loop_clarity(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    values = field_values.get("Value_Proposition", []) + field_values.get("Solution", [])
    revenue = field_values.get("Revenue_Model", [])
    prices = field_values.get("Price", [])
    status = "confirmed"
    severity = "low"
    reason = "价值主张与盈利方式已经形成初步连接。"
    evidence_hint = "建议继续补充：定价、毛利和收费节奏。"
    if not values or not (revenue or prices):
        status = "suspicious"
        severity = "high"
        reason = "商业项目还没有把“提供什么价值”和“怎么赚钱”连起来。"
        evidence_hint = "请补充：因什么价值付钱、按什么方式收钱。"
    return [_build_check(check_id="profit_loop::0", dimension="价值主张 × 盈利方式", rule_id="C2", left_key="Value_Proposition/Solution", left_value=" / ".join(values[:1]) or "(待补充)", right_key="Revenue_Model/Price", right_value=" / ".join((revenue[:1] + prices[:1])) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]


def _evaluate_payer_path(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    users = field_values.get("Target_Customer", []) + field_values.get("Beneficiary", [])
    payers = field_values.get("Revenue_Model", []) + field_values.get("Price", []) + field_values.get("Customer_Type", [])
    status = "confirmed"
    severity = "low"
    reason = "使用者与付费路径已有基本表达。"
    evidence_hint = "建议继续补充：采购者、决策者与支付者关系。"
    if not users or not payers:
        status = "suspicious"
        severity = "critical"
        reason = "项目没有说清谁使用、谁付费、钱从哪里回来。"
        evidence_hint = "请补充：使用者、决策者、付费者是否同一主体。"
    return [_build_check(check_id="payer_path::0", dimension="使用者 × 付费者", rule_id="C3", left_key="Target_Customer/Beneficiary", left_value=" / ".join(users[:1]) or "(待补充)", right_key="Revenue_Model/Price/Customer_Type", right_value=" / ".join(payers[:1]) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]


def _evaluate_public_beneficiary_boundary(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    beneficiaries = field_values.get("Beneficiary", []) + field_values.get("Service_Object", []) + field_values.get("Target_Customer", [])
    issues = field_values.get("Social_Issue", []) + field_values.get("Core_Pain_Point", [])
    status = "confirmed"
    severity = "low"
    reason = "公益对象与社会问题之间已有基本对应关系。"
    evidence_hint = "建议继续补充：场景、人数和地区边界。"
    if not beneficiaries or not issues:
        status = "suspicious"
        severity = "high"
        reason = "公益项目还没有把受益对象与其对应问题说清楚。"
        evidence_hint = "请补充：哪类人、在哪个场景、遇到什么问题。"
    return [_build_check(check_id="public_boundary::0", dimension="受益对象 × 社会问题", rule_id="P1", left_key="Beneficiary/Service_Object", left_value=" / ".join(beneficiaries[:1]) or "(待补充)", right_key="Social_Issue/Core_Pain_Point", right_value=" / ".join(issues[:1]) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]


def _evaluate_public_evidence(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    issues = field_values.get("Social_Issue", []) + field_values.get("Core_Pain_Point", [])
    evidence = field_values.get("Survey_Data", []) + field_values.get("Interview_Record", []) + field_values.get("Case_Study", []) + field_values.get("Pilot_Cooperation", [])
    status = "confirmed"
    severity = "low"
    reason = "公益主张已有调研、访谈或试点支撑。"
    evidence_hint = "建议继续补充：样本量、结果和前后对比。"
    if issues and not evidence:
        status = "suspicious"
        severity = "high"
        reason = "指出了社会问题，但没有给出足够证据来证明问题严重性和干预必要性。"
        evidence_hint = "请补充：调研、案例、样本或试点结果。"
    return [_build_check(check_id="public_evidence::0", dimension="社会问题 × 证据支撑", rule_id="P2", left_key="Social_Issue/Core_Pain_Point", left_value=" / ".join(issues[:1]) or "(待补充)", right_key="Survey/Interview/Case/Pilot", right_value=" / ".join(evidence[:1]) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]


def _evaluate_public_sustainability(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    impact = field_values.get("Impact_Metric", []) + field_values.get("Outcome_Index", []) + field_values.get("Scenario_Research", [])
    sustain = field_values.get("Donation_Source", []) + field_values.get("Partnership_Model", []) + field_values.get("Volunteer_System", []) + field_values.get("Revenue_Model", [])
    status = "confirmed"
    severity = "low"
    reason = "公益项目已出现初步的持续运营机制。"
    evidence_hint = "建议继续补充：资金、伙伴、志愿者的稳定性。"
    if (impact or field_values.get("Beneficiary", [])) and not sustain:
        status = "suspicious"
        severity = "critical"
        reason = "公益项目强调社会价值，但缺少长期资金、伙伴或组织机制，持续性不足。"
        evidence_hint = "请补充：长期资金来源、合作模式、志愿者与组织机制。"
    return [_build_check(check_id="public_sustain::0", dimension="社会价值 × 可持续机制", rule_id="P3", left_key="Impact/Outcome", left_value=" / ".join(impact[:1]) or "(待补充)", right_key="Donation/Partnership/Volunteer/Revenue", right_value=" / ".join(sustain[:1]) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]


def _evaluate_pr1_public_targeting(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    beneficiaries = field_values.get("Beneficiary_Group", [])
    scenarios = field_values.get("Service_Scenario", [])
    urgency = field_values.get("Urgency_Pain", [])
    left_value = " / ".join(beneficiaries[:1]) or "(待补充)"
    right_value = " / ".join((scenarios[:1] + urgency[:1])) or "(待补充)"
    status, severity = "confirmed", "low"
    reason = "受益对象、服务场景与问题紧迫性之间已有较完整对应。"
    evidence_hint = "建议继续补充：人群规模、地区边界与典型情境。"
    if not beneficiaries and not scenarios:
        status, severity = "suspicious", "high"
        reason = "受益对象与服务场景都还没有真正说清，公益边界尚未稳定。"
        evidence_hint = "请补充：具体是谁、在哪个场景、为什么这个问题迫切。"
    elif not beneficiaries or not scenarios:
        status, severity = "needs_evidence", "high"
        reason = "受益对象或服务场景只写清了一侧，当前还无法稳定复核公益边界。"
        evidence_hint = "请同时补清：受益对象 + 服务场景。"
    elif not urgency:
        status, severity = "needs_evidence", "medium"
        reason = "受益对象和场景已出现，但问题的紧迫性表达仍偏弱。"
        evidence_hint = "请补充：为什么这个问题现在必须解决。"
    return [_build_check(check_id="pr1_targeting::0", dimension="受益对象 × 服务场景", rule_id="PR1", left_key="Beneficiary_Group", left_value=left_value, right_key="Service_Scenario/Urgency_Pain", right_value=right_value, status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]

def _evaluate_pr2_public_demand(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    sample = field_values.get("Research_Sample", [])
    observation = field_values.get("Field_Observation", [])
    quote = field_values.get("Needs_Quote", [])
    severity_info = field_values.get("Problem_Severity", [])
    evidence = sample + observation + quote
    left_value = " / ".join(evidence[:1]) or "(待补充)"
    right_value = " / ".join(severity_info[:1]) or "(待补充)"
    status, severity = "confirmed", "low"
    reason = "需求证据与问题严重度之间已有较完整支撑。"
    evidence_hint = "建议继续补充：样本量、原话与前后对比。"
    if not evidence and not severity_info:
        status, severity = "suspicious", "high"
        reason = "需求证据与问题严重度都不充分，当前无法确认问题是否真实存在且值得介入。"
        evidence_hint = "请补充：样本、观察、原话、严重度中的至少两类。"
    elif not evidence or not severity_info:
        status, severity = "needs_evidence", "high"
        reason = "需求证据和问题严重度只写清了一侧，证据链还不完整。"
        evidence_hint = "请同时补清：需求证据 + 问题严重度。"
    elif len(sample) + len(observation) + len(quote) < 2:
        status, severity = "needs_evidence", "medium"
        reason = "虽然已有需求证据，但证据类型仍偏单薄。"
        evidence_hint = "建议至少补两类：样本、观察、原话。"
    return [_build_check(check_id="pr2_demand::0", dimension="需求证据 × 问题严重度", rule_id="PR2", left_key="Research/Field/Quote", left_value=left_value, right_key="Problem_Severity", right_value=right_value, status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]

def _evaluate_pr3_public_solution_fit(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    needs = field_values.get("Needs_Quote", []) + field_values.get("Field_Observation", []) + field_values.get("Problem_Severity", [])
    intervention = field_values.get("Intervention_Solution", [])
    core_service = field_values.get("Core_Service", [])
    outcome = field_values.get("Expected_Outcome", [])
    solution = intervention + core_service + outcome
    status, severity = "confirmed", "low"
    reason = "需求证据与干预方案之间已有较完整对应。"
    evidence_hint = "建议继续补充：哪个需求对应哪个服务动作与结果。"
    if not needs and not solution:
        status, severity = "suspicious", "critical"
        reason = "需求证据和干预方案都不充分，暂时无法确认方案真的贴着真实问题设计。"
        evidence_hint = "请补充：真实需求证据、干预动作和预期结果。"
    elif not needs or (not intervention and not core_service):
        status, severity = "needs_evidence", "high"
        reason = "需求证据或核心干预动作仍不完整，方案适配性还无法稳定判断。"
        evidence_hint = "请同时补清：需求证据 + 干预方案/核心服务。"
    elif not outcome:
        status, severity = "needs_evidence", "medium"
        reason = "虽然已有需求与干预，但预期改变仍不明确。"
        evidence_hint = "请补充：完成服务后，受益对象会发生什么具体变化。"
    return [_build_check(check_id="pr3_solution_fit::0", dimension="需求证据 × 干预方案", rule_id="PR3", left_key="Needs/Observation/Severity", left_value=" / ".join(needs[:1]) or "(待补充)", right_key="Intervention/Core_Service/Outcome", right_value=" / ".join(solution[:1]) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]

def _evaluate_pr4_stakeholder_fit(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    target = field_values.get("Beneficiary_Group", []) + field_values.get("Service_Scenario", [])
    stakeholders = field_values.get("Government_Link", []) + field_values.get("NGO_Partner", []) + field_values.get("Community_Leader", []) + field_values.get("Volunteer_Source", [])
    status, severity = "confirmed", "low"
    reason = "服务对象与关键协同方之间已有基本协同链路。"
    evidence_hint = "建议继续补充：每类协同方在服务流程中承担什么角色。"
    if not stakeholders:
        status, severity = "suspicious", "high"
        reason = "协同方仍不清楚，公益项目难以形成稳定执行网络。"
        evidence_hint = "请补充：政府、公益组织、社区关键人或志愿者来源。"
    return [_build_check(check_id="pr4_stakeholder::0", dimension="服务对象 × 协同方", rule_id="PR4", left_key="Beneficiary_Group/Service_Scenario", left_value=" / ".join(target[:1]) or "(待补充)", right_key="Stakeholder_Collaboration", right_value=" / ".join(stakeholders[:1]) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]


def _evaluate_pr5_ethics(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    beneficiaries = field_values.get("Beneficiary_Group", []) + field_values.get("Vulnerable_Group", [])
    ethics = field_values.get("Ethical_Risk", []) + field_values.get("Privacy_Protection", []) + field_values.get("Consent_Process", [])
    status, severity = "confirmed", "low"
    reason = "受益对象与伦理保护动作之间已有基本对应。"
    evidence_hint = "建议继续补充：隐私、同意、风险处置中的具体做法。"
    if beneficiaries and not ethics:
        status, severity = "suspicious", "critical"
        reason = "已经出现明确受益对象，但还没有形成对应的伦理与保护机制表达。"
        evidence_hint = "请补充：隐私保护、知情同意、敏感人群保护如何落地。"
    return [_build_check(check_id="pr5_ethics::0", dimension="受益对象 × 伦理保护", rule_id="PR5", left_key="Beneficiary/Vulnerable_Group", left_value=" / ".join(beneficiaries[:1]) or "(待补充)", right_key="Ethics/Privacy/Consent", right_value=" / ".join(ethics[:1]) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]


def _evaluate_pr6_fundraising(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    sources = field_values.get("Funding_Source", []) + field_values.get("Donation_Product", [])
    channels = field_values.get("Grant_Channel", []) + field_values.get("Revenue_Supplement", [])
    pairs = _limit_pairs(_pair_or_placeholder(sources, channels))
    checks: List[Dict[str, Any]] = []
    if not pairs:
        pairs = [("(待补充)", "(待补充)")]

    for idx, (left_value, right_value) in enumerate(pairs):
        status, severity = "confirmed", "low"
        reason = "资金来源与筹资渠道/补充造血之间已有较完整对应。"
        hint = "建议继续补充：主要来源、申报渠道和补充造血方式。"
        if not _has_real_value(left_value) and not _has_real_value(right_value):
            status, severity = "suspicious", "critical"
            reason = "筹资来源与获得渠道都不清楚，持续筹资逻辑尚未真正成立。"
        elif not _has_real_value(left_value) or not _has_real_value(right_value):
            status, severity = "needs_evidence", "high"
            reason = "资金来源和获取路径只写清了一侧，筹资机制还不完整。"
        elif _looks_negative_or_empty(left_value) or _looks_negative_or_empty(right_value):
            status, severity = "suspicious", "high"
            reason = "当前资金来源或补充造血表达带有明显空缺/否定，持续筹资能力仍不成立。"
        elif _contains_any(right_value, ["众筹", "推文", "募捐"]) and not _contains_any(left_value, ["基金会", "企业csr", "政府购买服务", "高校公益基金", "长期合作", "资助"]):
            status, severity = "needs_evidence", "medium"
            reason = "目前更像一次性筹资动作，长期稳定资金来源还不够清楚。"
        checks.append(_build_check(check_id=f"pr6_fundraising::{idx}", dimension="资金来源 × 筹资渠道", rule_id="PR6", left_key="Funding_Source/Donation_Product", left_value=left_value, right_key="Grant_Channel/Revenue_Supplement", right_value=right_value, status=status, severity=severity, reason=reason, evidence_hint=hint))
    return checks

def _evaluate_pr7_efficiency(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    costs = field_values.get("Single_Service_Cost", []) + field_values.get("Management_Cost", [])
    efficiency = field_values.get("Fund_Use_Ratio", []) + field_values.get("Budget_Ceiling", [])
    pairs = _limit_pairs(_pair_or_placeholder(costs, efficiency))
    checks: List[Dict[str, Any]] = []
    if not pairs:
        pairs = [("(待补充)", "(待补充)")]

    for idx, (left_value, right_value) in enumerate(pairs):
        status, severity = "confirmed", "low"
        reason = "服务成本与资金效率之间已有较完整对应。"
        hint = "建议继续补充：单次服务成本与资金使用效率。"
        if not _has_real_value(left_value) and not _has_real_value(right_value):
            status, severity = "needs_evidence", "high"
            reason = "成本与效率两侧都还没写清，当前无法判断资金是否花得值。"
        elif not _has_real_value(left_value) or not _has_real_value(right_value):
            status, severity = "needs_evidence", "high"
            reason = "成本与效率只写清了一侧，资源配置合理性仍难以判断。"
        elif not _has_number(left_value) or not _has_number(right_value):
            status, severity = "needs_evidence", "high"
            reason = "虽然有成本和预算描述，但缺少可量化数字或比例，暂时还不能算作真正的成本效率证据。"
        elif _contains_any(right_value, ["预算", "总额"]) and not _contains_any(right_value, ["比例", "%", "占比", "单次"]):
            status, severity = "needs_evidence", "medium"
            reason = "目前更多是总预算表达，还没有形成单次服务成本与资金使用效率的直接对应。"
        checks.append(_build_check(check_id=f"pr7_efficiency::{idx}", dimension="服务成本 × 资金效率", rule_id="PR7", left_key="Single/Management_Cost", left_value=left_value, right_key="Fund_Use_Ratio/Budget_Ceiling", right_value=right_value, status=status, severity=severity, reason=reason, evidence_hint=hint))
    return checks

def _evaluate_pr8_impact(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    goals = field_values.get("Impact_Goal", []) + field_values.get("Expected_Outcome", [])
    evals = field_values.get("Indicator_System", []) + field_values.get("Baseline_Data", []) + field_values.get("Evaluation_Method", [])
    pairs = _limit_pairs(_pair_or_placeholder(goals, evals))
    checks: List[Dict[str, Any]] = []
    if not pairs:
        pairs = [("(待补充)", "(待补充)")]

    has_indicator = bool(field_values.get("Indicator_System", []))
    has_baseline = bool(field_values.get("Baseline_Data", []))
    has_method = bool(field_values.get("Evaluation_Method", []))
    for idx, (left_value, right_value) in enumerate(pairs):
        status, severity = "confirmed", "low"
        reason = "影响目标与评估方法之间已有较完整对应。"
        hint = "建议继续补充：目标、指标、基线和评估方法如何一一对应。"
        if not _has_real_value(left_value) and not _has_real_value(right_value):
            status, severity = "suspicious", "critical"
            reason = "影响目标与评估方法都不明确，暂时无法验证项目是否真的带来改变。"
        elif not _has_real_value(left_value) or not _has_real_value(right_value):
            status, severity = "needs_evidence", "high"
            reason = "目标和评估只写清了一侧，影响验证链路还不完整。"
        elif not has_indicator or not has_method:
            status, severity = "needs_evidence", "high"
            reason = "虽然已有评估表达，但指标体系或评估方法仍不完整。"
        elif not has_baseline:
            status, severity = "needs_evidence", "medium"
            reason = "目标、指标和方法已有，但缺少基线数据，难以做前后变化判断。"
        checks.append(_build_check(check_id=f"pr8_impact::{idx}", dimension="影响目标 × 评估方法", rule_id="PR8", left_key="Impact_Goal/Expected_Outcome", left_value=left_value, right_key="Indicator/Baseline/Evaluation", right_value=right_value, status=status, severity=severity, reason=reason, evidence_hint=hint))
    return checks

def _evaluate_pr9_conversion(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    reach = field_values.get("Reach_Channel", []) + field_values.get("Participation_Motivation", [])
    retention = field_values.get("Retention_Mechanism", []) + field_values.get("Referral_Path", [])
    pairs = _limit_pairs(_pair_or_placeholder(reach, retention))
    checks: List[Dict[str, Any]] = []
    if not pairs:
        pairs = [("(待补充)", "(待补充)")]
    has_reach = bool(field_values.get("Reach_Channel", []))
    has_motivation = bool(field_values.get("Participation_Motivation", []))
    has_retention = bool(field_values.get("Retention_Mechanism", []))
    has_referral = bool(field_values.get("Referral_Path", []))
    for idx, (left_value, right_value) in enumerate(pairs):
        status, severity = "confirmed", "low"
        reason = "受益者触达与留存/转介路径之间已有较完整对应。"
        hint = "建议继续补充：触达、参与、留存、转介的完整路径。"
        if not _has_real_value(left_value) and not _has_real_value(right_value):
            status, severity = "suspicious", "high"
            reason = "触达与留存/转介路径都不清楚，参与链路尚未闭合。"
        elif not _has_real_value(left_value) or not _has_real_value(right_value):
            status, severity = "needs_evidence", "high"
            reason = "触达和留存/转介只写清了一侧，参与路径还不完整。"
        elif not has_motivation or not has_retention:
            status, severity = "needs_evidence", "medium"
            reason = "虽然已出现触达和陪伴动作，但参与动机或留存机制仍不够完整。"
        elif not has_referral:
            status, severity = "needs_evidence", "low"
            reason = "已有触达与留存表达，但转介/扩散链路仍不清楚。"
        checks.append(_build_check(check_id=f"pr9_conversion::{idx}", dimension="触达方式 × 留存/转介", rule_id="PR9", left_key="Reach/Participation", left_value=left_value, right_key="Retention/Referral", right_value=right_value, status=status, severity=severity, reason=reason, evidence_hint=hint))
    return checks

def _evaluate_pr10_transparency(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    disclosure = field_values.get("Disclosure_Frequency", []) + field_values.get("Financial_Disclosure", [])
    trust = field_values.get("Story_Evidence", []) + field_values.get("Third_Party_Endorsement", [])
    pairs = _limit_pairs(_pair_or_placeholder(disclosure, trust))
    checks: List[Dict[str, Any]] = []
    if not pairs:
        pairs = [("(待补充)", "(待补充)")]
    has_frequency = bool(field_values.get("Disclosure_Frequency", []))
    has_financial = bool(field_values.get("Financial_Disclosure", []))
    has_third_party = bool(field_values.get("Third_Party_Endorsement", []))
    has_story = bool(field_values.get("Story_Evidence", []))
    for idx, (left_value, right_value) in enumerate(pairs):
        status, severity = "confirmed", "low"
        reason = "透明机制与外部信任支撑之间已有较完整对应。"
        hint = "建议继续补充：公示频率、公开内容与第三方背书。"
        if not _has_real_value(left_value) and not _has_real_value(right_value):
            status, severity = "needs_evidence", "high"
            reason = "透明披露与外部信任支撑都不充分，公信力链路仍较弱。"
        elif not _has_real_value(left_value) or not _has_real_value(right_value):
            status, severity = "needs_evidence", "high"
            reason = "透明披露和外部信任只写清了一侧，公信力证据链还不完整。"
        elif not has_frequency or not has_third_party:
            status, severity = "needs_evidence", "high"
            reason = "虽然有财务/故事表达，但缺少披露频率或第三方背书，公信力仍不足。"
        elif not has_financial and has_story:
            status, severity = "needs_evidence", "medium"
            reason = "目前更像故事传播，还没有足够清晰的财务公开机制。"
        checks.append(_build_check(check_id=f"pr10_transparency::{idx}", dimension="透明机制 × 外部信任", rule_id="PR10", left_key="Disclosure/Financial_Disclosure", left_value=left_value, right_key="Story/Third_Party_Endorsement", right_value=right_value, status=status, severity=severity, reason=reason, evidence_hint=hint))
    return checks

def _evaluate_pr11_replication(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    pilot_left = field_values.get("Pilot_Site", []) + field_values.get("Pilot_Result", [])
    scale_right = field_values.get("Replication_Condition", []) + field_values.get("Expansion_Path", [])
    pairs = _limit_pairs(_pair_or_placeholder(pilot_left, scale_right))
    checks: List[Dict[str, Any]] = []
    if not pairs:
        pairs = [("(待补充)", "(待补充)")]
    has_site = bool(field_values.get("Pilot_Site", []))
    has_result = bool(field_values.get("Pilot_Result", []))
    has_replication = bool(field_values.get("Replication_Condition", []))
    has_expansion = bool(field_values.get("Expansion_Path", []))
    for idx, (left_value, right_value) in enumerate(pairs):
        status, severity = "confirmed", "low"
        reason = "试点结果与复制扩散路径之间已有较完整对应。"
        hint = "建议继续补充：试点证明了什么，复制需要什么条件。"
        if not _has_real_value(left_value) and not _has_real_value(right_value):
            status, severity = "suspicious", "critical"
            reason = "试点、结果、复制条件、扩散路径都不充分，暂时无法判断是否可复制扩散。"
        elif not has_result:
            status, severity = "suspicious", "high"
            reason = "目前只有试点地点或扩散设想，没有试点结果，复制能力还不能成立。"
        elif not has_replication and not has_expansion:
            status, severity = "needs_evidence", "high"
            reason = "已经有试点结果，但复制条件和扩散路径都还没写清。"
        elif not has_site:
            status, severity = "needs_evidence", "medium"
            reason = "已有试点结果与扩散设想，但试点发生在哪里仍不够明确。"
        elif not has_replication:
            status, severity = "needs_evidence", "medium"
            reason = "已有试点结果和扩散设想，但复制成立所需条件仍不明确。"
        checks.append(_build_check(check_id=f"pr11_replication::{idx}", dimension="试点结果 × 复制扩散", rule_id="PR11", left_key="Pilot_Site/Pilot_Result", left_value=left_value, right_key="Replication/Expansion", right_value=right_value, status=status, severity=severity, reason=reason, evidence_hint=hint))
    return checks

def _evaluate_pr12_volunteer(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    role = field_values.get("Volunteer_Role", [])
    ops = field_values.get("Training_Process", []) + field_values.get("Scheduling_Mechanism", []) + field_values.get("Incentive_NonCash", [])
    status, severity = "confirmed", "low"
    reason = "志愿者角色与运营机制之间已有基本对应。"
    evidence_hint = "建议继续补充：培训、排班与非现金激励。"
    if role and not ops:
        status, severity = "needs_evidence", "medium"
        reason = "已经出现志愿者角色，但培训、排班或激励机制仍不够具体。"
        evidence_hint = "请补充：志愿者怎么培训、怎么排班、怎么激励。"
    return [_build_check(check_id="pr12_volunteer::0", dimension="志愿者角色 × 培训/排班", rule_id="PR12", left_key="Volunteer_Role", left_value=" / ".join(role[:1]) or "(待补充)", right_key="Training/Scheduling/Incentive", right_value=" / ".join(ops[:1]) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]


def _evaluate_pr13_resource(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    resource = field_values.get("Key_Resource", []) + field_values.get("Resource_Gap", [])
    buffer = field_values.get("Replacement_Plan", []) + field_values.get("Risk_Buffer", [])
    status, severity = "confirmed", "low"
    reason = "关键资源与风险缓冲之间已有较完整对应。"
    evidence_hint = "建议继续补充：资源替代方案与兜底机制。"
    if not resource and not buffer:
        status, severity = "suspicious", "critical"
        reason = "关键资源与风险缓冲都不清楚，可持续性无法成立。"
        evidence_hint = "请补充：关键资源、资源缺口、替代方案和兜底机制。"
    elif not resource or not buffer:
        status, severity = "needs_evidence", "high"
        reason = "关键资源和风险缓冲只写清了一侧，可持续性证据链仍不完整。"
        evidence_hint = "请同时补清：关键资源 + 替代/缓冲方案。"
    return [_build_check(check_id="pr13_resource::0", dimension="关键资源 × 风险缓冲", rule_id="PR13", left_key="Key_Resource/Resource_Gap", left_value=" / ".join(resource[:1]) or "(待补充)", right_key="Replacement/Risk_Buffer", right_value=" / ".join(buffer[:1]) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]

def _evaluate_pr14_policy(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    policy = field_values.get("Policy_Basis", [])
    qualification = field_values.get("Qualification_Requirement", [])
    safety = field_values.get("Safety_Redline", [])
    opinion = field_values.get("Public_Opinion_Risk", [])
    boundary = qualification + safety + opinion
    status, severity = "confirmed", "low"
    reason = "政策依据与执行边界之间已有较完整对应。"
    evidence_hint = "建议继续补充：资质、安全和舆情三类边界。"
    if not policy and not boundary:
        status, severity = "suspicious", "critical"
        reason = "政策依据与执行边界都不完整，合规落地风险尚未说清。"
        evidence_hint = "请补充：依据哪条政策、要满足什么资质/安全/舆情要求。"
    elif not policy or not boundary:
        status, severity = "needs_evidence", "high"
        reason = "政策依据和执行边界只写清了一侧，合规链路仍不完整。"
        evidence_hint = "请同时补清：政策依据 + 执行边界。"
    elif not qualification or not safety:
        status, severity = "needs_evidence", "medium"
        reason = "已有政策依据和边界表达，但资质或安全要求还不够具体。"
        evidence_hint = "建议同时明确：资质要求 + 安全红线。"
    return [_build_check(check_id="pr14_policy::0", dimension="政策依据 × 执行边界", rule_id="PR14", left_key="Policy_Basis", left_value=" / ".join(policy[:1]) or "(待补充)", right_key="Qualification/Safety/Public_Opinion", right_value=" / ".join(boundary[:1]) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]

def _evaluate_pr15_cocreation(field_values: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    partner = field_values.get("Enterprise_Partner", []) + field_values.get("School_Hospital_Community", [])
    mechanism = field_values.get("CoCreation_Mode", []) + field_values.get("Longterm_Mechanism", [])
    status, severity = "confirmed", "low"
    reason = "合作伙伴与长期共创机制之间已有基本对应。"
    evidence_hint = "建议继续补充：合作方式与长效机制。"
    if partner and not mechanism:
        status, severity = "needs_evidence", "medium"
        reason = "合作伙伴已出现，但长期共创机制还不够明确。"
        evidence_hint = "请补充：怎么共创、靠什么长期持续。"
    return [_build_check(check_id="pr15_cocreation::0", dimension="合作伙伴 × 长期共创", rule_id="PR15", left_key="Enterprise/School_Hospital_Community", left_value=" / ".join(partner[:1]) or "(待补充)", right_key="CoCreation/Longterm_Mechanism", right_value=" / ".join(mechanism[:1]) or "(待补充)", status=status, severity=severity, reason=reason, evidence_hint=evidence_hint)]



def _build_summary(checks: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "total_checks": len(checks),
        "risky_count": sum(1 for item in checks if item.get("status") in {"contradictory", "suspicious"}),
        "needs_evidence_count": sum(1 for item in checks if item.get("status") == "needs_evidence"),
        "confirmed_count": sum(1 for item in checks if item.get("status") == "confirmed"),
        "rules_covered": sorted({item.get("rule_id") for item in checks if item.get("rule_id")}),
    }


def _package_semantic_report(
    checks: List[Dict[str, Any]],
    field_values: Dict[str, List[str]] | None = None,
    source_text: str = "",
    extracted_edges: Dict[str, List[str]] | None = None,
) -> Dict[str, Any]:
    field_values = field_values or {}
    extracted_edges = extracted_edges or {}
    checks = [
        _enrich_check_with_structural_hits(
            _enrich_check_with_excerpt(item, source_text),
            field_values,
            extracted_edges,
        )
        for item in list(checks or [])
    ]
    checks.sort(
        key=lambda item: (
            -STATUS_RANK.get(str(item.get("status") or "unknown"), 0),
            -SEVERITY_RANK.get(str(item.get("severity") or "low"), 0),
            str(item.get("rule_id") or ""),
        )
    )
    return {
        "summary": _build_summary(checks),
        "checks": checks,
        "alerts": _aggregate_alerts(checks),
        "field_values": field_values or {},
        "source_text": source_text or "",
        "extracted_edges": extracted_edges or {},
        "edge_quality": _build_edge_quality(checks),
    }


def _build_missing_semantic_placeholder(rule_id: str) -> Dict[str, Any]:
    return _build_check(
        check_id=f"semantic_placeholder::{rule_id}",
        dimension="语义复核补证",
        rule_id=rule_id,
        left_key="结构判定",
        left_value="该规则已通过结构判定",
        right_key="语义复核",
        right_value="缺少可复核的关键成对字段",
        status="suspicious",
        severity="high",
        reason="当前规则虽已通过结构判定，但文本中尚未形成足以复核语义的关键成对字段，暂时不能把结构命中直接当成语义成立。",
        evidence_hint="请把该规则涉及的关键对象、数值、对标对象或证据写得更明确，便于系统继续复核语义。",
    )




def _compact_stage_semantic_checks(checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    面板展示时，压缩同一规则下大量重复的“待补证”复核项。
    
    原始语义评估会对左右字段做笛卡尔配对，若某条规则命中了多个近似表达，
    很容易生成一长串 status 相同、结论近似的 checks，导致分析面板重复刷屏。
    这里不改变“最差状态”的判断逻辑，只保留少量具有代表性的项用于展示。
    """
    if not checks:
        return []

    def _norm_value(value: Any) -> str:
        return re.sub(r"\s+", " ", str(value or "").strip().lower())

    def _score(item: Dict[str, Any]) -> Tuple[int, int, int, int]:
        left_real = 1 if _has_real_value(item.get('left_value', '')) else 0
        right_real = 1 if _has_real_value(item.get('right_value', '')) else 0
        excerpt = 1 if _is_meaningful_excerpt(item.get('source_excerpt', '')) else 0
        hit_count = len(item.get('structural_hit_fields') or [])
        return (left_real + right_real, excerpt, hit_count, len(str(item.get('reason') or '')))

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in checks:
        rule_id = str(item.get('rule_id') or '').strip()
        grouped.setdefault(rule_id, []).append(item)

    compacted: List[Dict[str, Any]] = []
    for rule_id, items in grouped.items():
        # 先按风险/状态排序，保证更重要的项靠前
        items = sorted(
            items,
            key=lambda item: (
                -STATUS_RANK.get(str(item.get('status') or 'unknown'), 0),
                -SEVERITY_RANK.get(str(item.get('severity') or 'low'), 0),
                -_score(item)[0],
                -_score(item)[1],
                -_score(item)[2],
                -_score(item)[3],
            )
        )

        unique: List[Dict[str, Any]] = []
        seen = set()
        for item in items:
            key = (
                str(item.get('rule_id') or ''),
                str(item.get('status') or ''),
                str(item.get('dimension') or ''),
                str(item.get('left_key') or ''),
                str(item.get('right_key') or ''),
                _norm_value(item.get('left_value', '')),
                _norm_value(item.get('right_value', '')),
                _norm_value(item.get('reason', '')),
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)

        risky = [item for item in unique if str(item.get('status') or '') in {'contradictory', 'suspicious'}]
        pending = [item for item in unique if str(item.get('status') or '') == 'needs_evidence']
        confirmed = [item for item in unique if str(item.get('status') or '') == 'confirmed']
        unknown = [item for item in unique if str(item.get('status') or '') not in {'contradictory', 'suspicious', 'needs_evidence', 'confirmed'}]

        # 对同一规则：
        # - 风险项最多保留 2 条，避免真正不同的风险被吞掉
        # - 纯“待补证”项最多保留 2 条，避免刷屏
        # - confirmed / unknown 只保留 1 条代表项
        compacted.extend(risky[:2])
        compacted.extend(pending[:2])
        if not risky and not pending and confirmed:
            compacted.append(confirmed[0])
        elif confirmed:
            compacted.append(confirmed[0])
        if unknown:
            compacted.append(unknown[0])

    compacted.sort(
        key=lambda item: (
            -STATUS_RANK.get(str(item.get('status') or 'unknown'), 0),
            -SEVERITY_RANK.get(str(item.get('severity') or 'low'), 0),
            str(item.get('rule_id') or ''),
        )
    )
    return compacted

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
                    checks.append(_build_contextual_missing_semantic_check(rule_id, semantic_report.get("field_values") or {}, source_text or semantic_report.get("source_text") or ""))

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
        item
        for item in (semantic_report.get("checks") or [])
        if str(item.get("status") or "") in SEMANTIC_BLOCKING_STATUSES
    ]
    return _aggregate_alerts(blocking_checks)


def filter_semantic_report_by_rule_ids(
    semantic_report: Dict[str, Any] | None,
    allowed_rule_ids: Iterable[str] | None,
) -> Dict[str, Any]:
    semantic_report = semantic_report or {}
    allowed = {str(item).strip() for item in (allowed_rule_ids or []) if str(item).strip()}
    checks = list(semantic_report.get("checks") or [])
    if allowed:
        checks = [item for item in checks if str(item.get("rule_id") or "") in allowed]

    checks.sort(
        key=lambda item: (
            -STATUS_RANK.get(str(item.get("status") or "unknown"), 0),
            -SEVERITY_RANK.get(str(item.get("severity") or "low"), 0),
            str(item.get("rule_id") or ""),
        )
    )

    return _package_semantic_report(
        checks,
        semantic_report.get("field_values") or {},
        semantic_report.get("source_text") or "",
        semantic_report.get("extracted_edges") or {},
    )

def evaluate_hyperedge_semantics(
    extracted_edges: Dict[str, List[str]] | None,
    *,
    source_text: str = "",
) -> Dict[str, Any]:
    extracted_edges = extracted_edges or {}
    field_values = _collect_field_values(extracted_edges, source_text)

    checks: List[Dict[str, Any]] = []

    # 阶段一：客群、叙事、竞争、市场、创新
    checks.extend(_evaluate_field_type_consistency(field_values))
    checks.extend(_evaluate_channel_customer(field_values, source_text))
    checks.extend(_evaluate_narrative_causality(field_values))
    checks.extend(_evaluate_competition_realism(field_values))
    checks.extend(_evaluate_market_funnel_consistency(field_values))
    checks.extend(_evaluate_innovation_against_competition(field_values))

    # 阶段二：支付、单位经济、定价、现金流、财务、频次
    checks.extend(_evaluate_price_customer(field_values, source_text))
    checks.extend(_evaluate_unit_economics(field_values))
    checks.extend(_evaluate_pricing_space(field_values))
    checks.extend(_evaluate_cash_flow_health(field_values))
    checks.extend(_evaluate_financial_reasonableness(field_values))
    checks.extend(_evaluate_frequency_revenue(field_values))

    # 阶段三：技术-商业、合规、供应链、冷启动、团队、资源、社会价值
    checks.extend(_evaluate_tech_business_alignment(field_values))
    checks.extend(_evaluate_compliance_industry(field_values, source_text))
    checks.extend(_evaluate_supply_chain_sync(field_values, source_text))
    checks.extend(_evaluate_cold_start_engine(field_values, source_text))
    checks.extend(_evaluate_team_tech(field_values))
    checks.extend(_evaluate_resource_feasibility(field_values))
    checks.extend(_evaluate_social_value_translation(field_values, source_text))

    # 公益项目 PR1-PR15 语义复核（新增，不改动既有商业逻辑）
    checks.extend(_evaluate_pr1_public_targeting(field_values))
    checks.extend(_evaluate_pr2_public_demand(field_values))
    checks.extend(_evaluate_pr3_public_solution_fit(field_values))
    checks.extend(_evaluate_pr4_stakeholder_fit(field_values))
    checks.extend(_evaluate_pr5_ethics(field_values))
    checks.extend(_evaluate_pr6_fundraising(field_values))
    checks.extend(_evaluate_pr7_efficiency(field_values))
    checks.extend(_evaluate_pr8_impact(field_values))
    checks.extend(_evaluate_pr9_conversion(field_values))
    checks.extend(_evaluate_pr10_transparency(field_values))
    checks.extend(_evaluate_pr11_replication(field_values))
    checks.extend(_evaluate_pr12_volunteer(field_values))
    checks.extend(_evaluate_pr13_resource(field_values))
    checks.extend(_evaluate_pr14_policy(field_values))
    checks.extend(_evaluate_pr15_cocreation(field_values))

    checks.sort(
        key=lambda item: (
            -STATUS_RANK.get(str(item.get("status") or "unknown"), 0),
            -SEVERITY_RANK.get(str(item.get("severity") or "low"), 0),
            str(item.get("rule_id") or ""),
        )
    )

    return _package_semantic_report(checks, field_values, source_text, extracted_edges)
