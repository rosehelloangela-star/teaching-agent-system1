from __future__ import annotations

from typing import Dict, List

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
}

PROJECT_STAGE_DEFINITIONS: List[Dict[str, object]] = [
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
        "milestone_message": "恭喜你突破了第一阶段【价值主张与客户边界】，系统已进入第二阶段【盈利逻辑与生存压力测试】。",
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
        "milestone_message": "恭喜你突破了第二阶段【盈利逻辑与生存压力测试】，系统已进入第三阶段【资源杠杆与落地可行性】。",
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


def get_stage_definition(stage_id: str) -> Dict[str, object]:
    for stage in PROJECT_STAGE_DEFINITIONS:
        if stage["id"] == stage_id:
            return stage
    return PROJECT_STAGE_DEFINITIONS[0]
