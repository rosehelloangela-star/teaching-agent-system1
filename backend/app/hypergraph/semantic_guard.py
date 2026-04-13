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
}


SEMANTIC_CAPABLE_RULE_IDS = {
    'R2', 'R3', 'R4', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15', 'R16', 'R17', 'R18', 'R19', 'R20'
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

    checks.sort(
        key=lambda item: (
            -STATUS_RANK.get(str(item.get("status") or "unknown"), 0),
            -SEVERITY_RANK.get(str(item.get("severity") or "low"), 0),
            str(item.get("rule_id") or ""),
        )
    )

    return _package_semantic_report(checks, field_values, source_text, extracted_edges)
