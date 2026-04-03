from __future__ import annotations

from typing import Dict, List

PROJECT_RULE_STRATEGIES: Dict[str, List[Dict[str, str]]] = {
    "R1": [
        {
            "strategy_id": "elevator_pitch",
            "strategy_name": "60秒电梯陈述压缩",
            "question": "先别介绍产品名。请你只用一句话回答：谁在什么场景下，因为哪个具体问题而痛苦？",
            "resolve_hint": "学生能明确给出“用户-场景-痛点”三连表达。",
        },
        {
            "strategy_id": "core_loop_fill",
            "strategy_name": "四点闭环补齐",
            "question": "请依次补齐这四个空：目标用户是谁、核心痛点是什么、现有替代方案是什么、你比它强在哪里？",
            "resolve_hint": "用户、痛点、替代方案和价值主张同时出现。",
        },
    ],
    "R3": [
        {
            "strategy_id": "remove_product_name",
            "strategy_name": "去产品名复述",
            "question": "先暂时删掉你的产品名，只说：如果没有这个方案，用户今天靠什么凑合解决这个问题？",
            "resolve_hint": "痛点和方案之间出现明确因果链，而不是功能堆叠。",
        },
        {
            "strategy_id": "before_after_change",
            "strategy_name": "痛点前后对比",
            "question": "你的方案上线前后，用户哪个关键动作会被明显改变？请举一个具体动作差异。",
            "resolve_hint": "说清使用前后差异，避免空泛“更方便”。",
        },
    ],
    "R5": [
        {
            "strategy_id": "five_slot_fill",
            "strategy_name": "五格补齐",
            "question": "请只回答五项：目标用户、核心痛点、价值主张、首个渠道、收入方式。不要展开成大段宣传文案。",
            "resolve_hint": "核心闭环要素补齐到最低可用程度。",
        },
    ],
    "R6": [
        {
            "strategy_id": "first_touch_path",
            "strategy_name": "第一次触达路径",
            "question": "你的第一批用户今天最常出现在哪个线下/线上场景？你为什么能在那里真正接触到他们？",
            "resolve_hint": "渠道与客群之间出现可执行接触点。",
        },
        {
            "strategy_id": "channel_counterfactual",
            "strategy_name": "渠道反证法",
            "question": "如果不用你现在说的这个渠道，你还能通过什么更便宜、更自然的方式接触他们？",
            "resolve_hint": "出现更贴近目标人群的替代触达方式。",
        },
    ],
    "R8": [
        {
            "strategy_id": "invisible_substitute",
            "strategy_name": "寻找隐形替代品",
            "question": "你的对手未必是同类产品。今天不用你，用户靠什么凑合解决这个问题？“保持现状”本身就是一个对手。",
            "resolve_hint": "至少说出一个替代方案、旧习惯或竞争对手。",
        },
        {
            "strategy_id": "giant_shadow",
            "strategy_name": "模拟巨头入场",
            "question": "如果字节、腾讯或行业龙头明天把类似功能做成免费插件，你剩下的护城河是什么？",
            "resolve_hint": "能回答真正的壁垒，而不是“我们更懂用户”。",
        },
        {
            "strategy_id": "switching_cost",
            "strategy_name": "迁移成本测试",
            "question": "即使你的方案理论上好20%，这个提升足以覆盖用户改变习惯、迁移数据或购买新硬件的成本吗？",
            "resolve_hint": "承认迁移成本，并解释何以值得切换。",
        },
    ],
    "R9": [
        {
            "strategy_id": "first_100_users",
            "strategy_name": "前100个用户定位",
            "question": "先别谈全国市场。你的前100个用户具体分布在哪个学校、社区或城市？请把边界收窄。",
            "resolve_hint": "从大市场收缩到可触达、可验证的细分边界。",
        },
    ],
    "R10": [
        {
            "strategy_id": "why_you_why_now",
            "strategy_name": "为何是你、为何是现在",
            "question": "同样的问题别人也在做。请回答：为什么偏偏现在值得做，而且为什么由你们来做？",
            "resolve_hint": "差异化落到可验证点，而不是“更智能、更方便”。",
        },
    ],
    "R7": [
        {
            "strategy_id": "who_pays",
            "strategy_name": "谁受益谁付费",
            "question": "使用者和付费者是同一个人吗？如果不是，真正愿意付钱的是谁？",
            "resolve_hint": "出现明确的付费方与支付理由。",
        },
    ],
    "R11": [
        {
            "strategy_id": "unit_econ_single_user",
            "strategy_name": "单客账本",
            "question": "先不谈一年。你服务一个用户，最保守情况下能赚多少钱、要花多少钱？",
            "resolve_hint": "至少给出一个单客收益-成本粗算式。",
        },
    ],
    "R12": [
        {
            "strategy_id": "price_floor_ceiling",
            "strategy_name": "定价上下界",
            "question": "你的价格下限由什么决定？上限又由什么决定？请拆成成本与客户价值两边说。",
            "resolve_hint": "说出基本的成本构成和定价依据。",
        },
    ],
    "R13": [
        {
            "strategy_id": "survival_window",
            "strategy_name": "不融资能活多久",
            "question": "如果一分钱新融资都没有，你现在账上的资源能撑几个月？最先断裂的是哪一环？",
            "resolve_hint": "出现 burn rate / 账期 / 启动资金 的关系表达。",
        },
    ],
    "R18": [
        {
            "strategy_id": "key_assumption",
            "strategy_name": "关键假设追问",
            "question": "你的财务预测里最关键的三个假设是什么？它们各自的依据是什么？",
            "resolve_hint": "财务模型不再只是拍脑袋数字。",
        },
    ],
    "R19": [
        {
            "strategy_id": "frequency_vs_charge",
            "strategy_name": "使用频率反推收费方式",
            "question": "你的产品是高频、低频还是超低频？那为什么适合现在这个收费方式？",
            "resolve_hint": "使用频次与收入模式至少逻辑一致。",
        },
    ],
    "R2": [
        {
            "strategy_id": "tech_to_value",
            "strategy_name": "技术翻译成收益",
            "question": "你的技术优势，最终给用户或客户带来的直接价值到底是什么？请别停留在技术术语本身。",
            "resolve_hint": "技术叙述能回到客户价值或商业壁垒。",
        },
    ],
    "R4": [
        {
            "strategy_id": "compliance_stress_test",
            "strategy_name": "政策收紧测试",
            "question": "如果监管明天更严格，你的流程哪一步最先出问题？谁来承担合规成本？",
            "resolve_hint": "合规进入商业逻辑，而非孤立提醒。",
        },
    ],
    "R14": [
        {
            "strategy_id": "delivery_chain",
            "strategy_name": "订单到交付链路图",
            "question": "从用户下单到交付完成，中间一共经过哪些环节？如果一个供应商临时退出，你最先受影响的是什么？",
            "resolve_hint": "出现真实履约路径与成本意识。",
        },
    ],
    "R15": [
        {
            "strategy_id": "seed_users",
            "strategy_name": "前10个用户计划",
            "question": "你的前10个种子用户从哪里来？不是“理论上”，而是明天能联系到谁？",
            "resolve_hint": "冷启动不再停留在“先宣传一下”。",
        },
    ],
    "R16": [
        {
            "strategy_id": "role_match",
            "strategy_name": "角色落位",
            "question": "你团队里谁具体能做这件最难的事？名字可以不说，但角色必须明确。",
            "resolve_hint": "团队能力开始与技术路线匹配。",
        },
    ],
    "R17": [
        {
            "strategy_id": "milestone_90d",
            "strategy_name": "90天里程碑",
            "question": "未来90天你们只做三件事，会是哪三件？如果只能先解一个瓶颈，最先解哪一个？",
            "resolve_hint": "出现可执行里程碑，不再是大词。",
        },
    ],
    "R20": [
        {
            "strategy_id": "value_translation",
            "strategy_name": "社会价值转商业价值",
            "question": "你的社会价值很好，但它怎么转成真正愿意买单的商业价值？如果受益者不付钱，那谁会付钱？",
            "resolve_hint": "社会价值与商业价值之间出现转译路径。",
        },
    ],
}


def select_project_followup_questions(alerts: List[Dict[str, str]], source_text: str = '', max_questions: int = 3) -> List[Dict[str, str]]:
    text = (source_text or '').lower()
    selected: List[Dict[str, str]] = []
    seen_rule_ids = set()

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_alerts = sorted(alerts, key=lambda item: severity_rank.get(item.get("severity", "medium"), 9))

    for alert in sorted_alerts:
        rule_id = alert.get("rule")
        if not rule_id or rule_id in seen_rule_ids:
            continue
        strategies = PROJECT_RULE_STRATEGIES.get(rule_id, [])
        if not strategies:
            continue
        chosen = strategies[0]
        if rule_id == "R8":
            if any(keyword in text for keyword in ["没有对手", "没对手", "第一家", "独创", "首创"]):
                chosen = strategies[0]
            elif any(keyword in text for keyword in ["腾讯", "字节", "阿里", "华为", "巨头"]):
                chosen = strategies[1] if len(strategies) > 1 else strategies[0]
            else:
                chosen = strategies[min(2, len(strategies) - 1)]
        selected.append(
            {
                "rule_id": rule_id,
                "rule_name": alert.get("name", rule_id),
                "severity": alert.get("severity", "medium"),
                "strategy_id": chosen["strategy_id"],
                "strategy_name": chosen["strategy_name"],
                "question": chosen["question"],
                "resolve_hint": chosen["resolve_hint"],
            }
        )
        seen_rule_ids.add(rule_id)
        if len(selected) >= max_questions:
            break
    return selected
