from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

COMMON_DIMENSIONS: Dict[str, Dict[str, Any]] = {
    "problem_definition": {
        "dimension_name": "背景与问题定义",
        "required_evidence": [
            "明确的问题场景、用户对象或研究对象界定",
            "痛点/问题严重性的事实依据或调研依据",
            "为什么现在必须解决这个问题的背景说明",
        ],
        "common_mistakes": [
            "把宏大口号当问题定义",
            "目标人群范围过大，缺乏边界",
            "没有用场景、数据或案例证明问题真实存在",
        ],
    },
    "innovation_originality": {
        "dimension_name": "创新突破与原创性",
        "required_evidence": [
            "相较现有方案的创新点拆解",
            "创新来源或原创设计逻辑说明",
            "与竞品/已有研究/已有解法的差异证明",
        ],
        "common_mistakes": [
            "把功能堆砌误当创新",
            "只讲概念新，不讲为什么难以复制",
            "没有与现有方案进行横向对比",
        ],
    },
    "core_solution": {
        "dimension_name": "核心方案与科学论证",
        "required_evidence": [
            "核心技术路线或解决方案闭环图",
            "关键机制、原理、流程或实验设计说明",
            "支撑方案有效性的论证、测试或专家判断",
        ],
        "common_mistakes": [
            "只有愿景，没有可执行方案",
            "技术路径或业务路径描述模糊",
            "结论先行，但没有论证过程",
        ],
    },
    "data_visualization": {
        "dimension_name": "数据与可视化支撑",
        "required_evidence": [
            "核心数据来源、样本口径或测算口径说明",
            "关键图表、指标看板或结果可视化",
            "数据与结论之间的对应关系说明",
        ],
        "common_mistakes": [
            "只给结论，不给数据来源",
            "图表好看但不支撑关键论点",
            "把 TAM 或宏观市场数字直接当项目可得市场",
        ],
    },
    "feasibility_execution": {
        "dimension_name": "落地可行性与执行逻辑",
        "required_evidence": [
            "阶段计划、资源配置与里程碑",
            "团队能力与任务匹配关系",
            "交付路径、合作资源或关键前置条件",
        ],
        "common_mistakes": [
            "计划与资源脱节",
            "把长期目标写成短期里程碑",
            "团队能力无法支撑关键执行环节",
        ],
    },
    "benefit_prospect": {
        "dimension_name": "综合效益与应用前景",
        "required_evidence": [
            "社会、经济、产业或用户价值说明",
            "应用场景、推广路径或落地前景",
            "预期收益或影响范围的合理估计",
        ],
        "common_mistakes": [
            "价值陈述空泛，缺少量化指标",
            "应用前景与当前阶段脱节",
            "只讲愿景，不讲可实现的近期成果",
        ],
    },
    "risk_robustness": {
        "dimension_name": "风险评估与鲁棒性检验",
        "required_evidence": [
            "关键风险列表及应对策略",
            "敏感性分析、备选方案或容错设计",
            "合规、伦理、供应链或技术失败风险说明",
        ],
        "common_mistakes": [
            "只写一句“风险可控”",
            "没有识别最致命失败点",
            "没有给出具体缓释措施",
        ],
    },
    "logic_expression": {
        "dimension_name": "规范与逻辑表达",
        "required_evidence": [
            "结构清晰的 BP/路演叙事",
            "概念使用准确、逻辑顺序明确",
            "图文配合、表达规范且结论一致",
        ],
        "common_mistakes": [
            "叙事跳跃，前后矛盾",
            "概念混用，术语不准确",
            "页面精美但逻辑不成链",
        ],
    },
}

EXCLUSIVE_DIMENSIONS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "internet_plus": {
        "business_finance": {
            "dimension_name": "商业模式与财务回报",
            "required_evidence": [
                "收入模式、成本结构与单位经济说明",
                "营收、利润或现金流测算依据",
                "价格、付费意愿与回本路径证明",
            ],
            "common_mistakes": [
                "收入模型与用户行为不匹配",
                "单位经济不成立却宣称可以盈利",
                "财务预测脱离获客与履约成本",
            ],
        },
        "market_barrier_strategy": {
            "dimension_name": "市场壁垒与营销策略",
            "required_evidence": [
                "获客渠道与目标用户触达逻辑",
                "竞争壁垒、渠道优势或资源护城河",
                "营销转化路径与投放假设",
            ],
            "common_mistakes": [
                "客户与渠道错位",
                "把流量想象当成渠道能力",
                "没有真实替代方案与竞争者分析",
            ],
        },
    },
    "innovation_entrepreneurship": {
        "practice_participation": {
            "dimension_name": "实践过程与学生参与度",
            "required_evidence": [
                "学生真实参与过程与分工记录",
                "调研、验证、访谈、制作等实践证据",
                "从想法到实践的迭代痕迹",
            ],
            "common_mistakes": [
                "只展示结果，不展示实践过程",
                "学生角色模糊，参与度不清晰",
                "把设想写成已完成实践",
            ],
        },
        "stage_resource_integration": {
            "dimension_name": "阶段性成果与资源整合",
            "required_evidence": [
                "阶段性样机、合作、试点或奖项证据",
                "外部资源、导师、校内外支持说明",
                "后续资源整合与推进路径",
            ],
            "common_mistakes": [
                "阶段成果描述空泛",
                "资源整合只停留在口头设想",
                "缺乏可验证的中期成果",
            ],
        },
    },
    "math_modeling": {
        "model_assumption_symbol": {
            "dimension_name": "模型假设与符号系统",
            "required_evidence": [
                "清晰的模型假设与变量定义",
                "符号系统、约束条件与边界说明",
                "建模对象与现实问题映射关系",
            ],
            "common_mistakes": [
                "假设不完整或相互冲突",
                "符号系统混乱",
                "模型与现实问题脱节",
            ],
        },
        "algorithm_complexity_efficiency": {
            "dimension_name": "算法复杂度与算力效能",
            "required_evidence": [
                "算法流程与复杂度分析",
                "运行效率、资源消耗或求解可行性说明",
                "与替代算法或基线方法的效率比较",
            ],
            "common_mistakes": [
                "只写算法名，不分析复杂度",
                "忽视计算成本与可扩展性",
                "没有基线比较",
            ],
        },
    },
    "challenge_cup": {
        "academic_value": {
            "dimension_name": "学术价值与理论贡献",
            "required_evidence": [
                "研究问题的学术意义说明",
                "理论、文献、已有研究的承接关系",
                "论文、报告或理论框架支撑材料",
            ],
            "common_mistakes": [
                "只有应用价值，没有学术问题意识",
                "缺乏文献基础或理论定位",
                "把常识性改进包装成理论贡献",
            ],
        },
        "trl_maturity": {
            "dimension_name": "技术成熟度（TRL）",
            "required_evidence": [
                "技术原型、验证结果或成熟度阶段说明",
                "从实验室到应用的成熟路径",
                "关键技术依赖与落地条件说明",
            ],
            "common_mistakes": [
                "概念验证与工程化成熟度混淆",
                "没有原型却声称可快速落地",
                "缺少阶段验证与性能指标",
            ],
        },
    },
}

TEMPLATE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "internet_plus": {
        "template_name": "中国国际大学生创新大赛（原互联网+）",
        "short_name": "互联网+",
        "aliases": ["互联网+", "中国国际大学生创新大赛", "原互联网+", "创新大赛", "主赛道", "初创组"],
        "weights": {
            "problem_definition": 5,
            "innovation_originality": 10,
            "core_solution": 10,
            "data_visualization": 10,
            "feasibility_execution": 10,
            "benefit_prospect": 10,
            "risk_robustness": 5,
            "logic_expression": 5,
            "business_finance": 20,
            "market_barrier_strategy": 15,
        },
        "exclusive_order": ["business_finance", "market_barrier_strategy"],
        "focus_hint": "优先强调商业模式闭环、财务回报真实性、就业带动、渠道与市场壁垒。",
        "expected_shift": "会显著提高对商业模式、单位经济、渠道策略和财务真实性的要求。",
    },
    "innovation_entrepreneurship": {
        "template_name": "创新创业（大创）",
        "short_name": "创新创业/大创",
        "aliases": ["大创", "创新创业", "大学生创新创业", "创新创业训练计划", "创业训练", "创业项目"],
        "weights": {
            "problem_definition": 10,
            "innovation_originality": 15,
            "core_solution": 10,
            "data_visualization": 10,
            "feasibility_execution": 15,
            "benefit_prospect": 10,
            "risk_robustness": 5,
            "logic_expression": 5,
            "practice_participation": 10,
            "stage_resource_integration": 10,
        },
        "exclusive_order": ["practice_participation", "stage_resource_integration"],
        "focus_hint": "优先强调学生真实实践过程、阶段成果、资源整合与创新创业训练价值。",
        "expected_shift": "会显著提高对实践过程证据、学生参与度和阶段性成果的要求。",
    },
    "math_modeling": {
        "template_name": "数学建模竞赛",
        "short_name": "数学建模",
        "aliases": ["数学建模", "建模", "modeling", "数模"],
        "weights": {
            "problem_definition": 10,
            "innovation_originality": 5,
            "core_solution": 20,
            "data_visualization": 15,
            "feasibility_execution": 5,
            "benefit_prospect": 5,
            "risk_robustness": 10,
            "logic_expression": 15,
            "model_assumption_symbol": 10,
            "algorithm_complexity_efficiency": 5,
        },
        "exclusive_order": ["model_assumption_symbol", "algorithm_complexity_efficiency"],
        "focus_hint": "优先强调模型假设、符号系统、科学论证、算法复杂度与结果表达。",
        "expected_shift": "会显著提高对模型规范性、数学严谨性和计算效率的要求。",
    },
    "challenge_cup": {
        "template_name": "挑战杯全国大学生课外学术科技作品竞赛",
        "short_name": "挑战杯",
        "aliases": ["挑战杯", "课外学术科技作品竞赛", "学术科技作品", "挑战杯全国大学生"],
        "weights": {
            "problem_definition": 5,
            "innovation_originality": 20,
            "core_solution": 20,
            "data_visualization": 10,
            "feasibility_execution": 5,
            "benefit_prospect": 10,
            "risk_robustness": 5,
            "logic_expression": 5,
            "academic_value": 10,
            "trl_maturity": 10,
        },
        "exclusive_order": ["academic_value", "trl_maturity"],
        "focus_hint": "优先强调学术深度、技术创新壁垒、社会调查严谨性与技术成熟度。",
        "expected_shift": "会显著提高对理论贡献、文献/专利支撑和技术成熟路径的要求。",
    },
}

DEFAULT_TEMPLATE_ID = "innovation_entrepreneurship"


def _build_rubric_items(template_id: str) -> List[Dict[str, Any]]:
    template = TEMPLATE_REGISTRY[template_id]
    items: List[Dict[str, Any]] = []

    for dim_id, base in COMMON_DIMENSIONS.items():
        items.append(
            {
                "dimension_id": dim_id,
                "dimension_name": base["dimension_name"],
                "category": "common",
                "weight": template["weights"][dim_id],
                "required_evidence": deepcopy(base["required_evidence"]),
                "common_mistakes": deepcopy(base["common_mistakes"]),
            }
        )

    for dim_id in template["exclusive_order"]:
        base = EXCLUSIVE_DIMENSIONS[template_id][dim_id]
        items.append(
            {
                "dimension_id": dim_id,
                "dimension_name": base["dimension_name"],
                "category": "exclusive",
                "weight": template["weights"][dim_id],
                "required_evidence": deepcopy(base["required_evidence"]),
                "common_mistakes": deepcopy(base["common_mistakes"]),
            }
        )

    return items


def resolve_competition_template(text: str) -> Dict[str, Any]:
    full_text = (text or "").lower()

    best_template_id = DEFAULT_TEMPLATE_ID
    best_alias = ""
    best_score = -1

    for template_id, template in TEMPLATE_REGISTRY.items():
        score = 0
        matched_alias = ""
        for alias in template["aliases"]:
            alias_lower = alias.lower()
            if alias_lower in full_text:
                score += 2 if len(alias_lower) >= 4 else 1
                if len(alias_lower) > len(matched_alias):
                    matched_alias = alias
        if score > best_score:
            best_score = score
            best_template_id = template_id
            best_alias = matched_alias

    template = TEMPLATE_REGISTRY[best_template_id]
    rubric_items = _build_rubric_items(best_template_id)
    sorted_focus = sorted(rubric_items, key=lambda item: item["weight"], reverse=True)

    return {
        "template_id": best_template_id,
        "template_name": template["template_name"],
        "short_name": template["short_name"],
        "matched_alias": best_alias or "未显式命中，按默认模板判定",
        "recognition_basis": (
            f"根据用户指令中的赛事关键词匹配到“{best_alias}”。"
            if best_alias
            else f"未命中明确赛事关键词，系统默认采用“{template['template_name']}”模板。"
        ),
        "focus_hint": template["focus_hint"],
        "expected_shift": template["expected_shift"],
        "total_weight": sum(item["weight"] for item in rubric_items),
        "rubric_items": rubric_items,
        "top_focus_dimensions": [
            {
                "dimension_id": item["dimension_id"],
                "dimension_name": item["dimension_name"],
                "weight": item["weight"],
            }
            for item in sorted_focus[:4]
        ],
        "exclusive_dimensions": [
            {
                "dimension_id": item["dimension_id"],
                "dimension_name": item["dimension_name"],
                "weight": item["weight"],
            }
            for item in rubric_items
            if item["category"] == "exclusive"
        ],
    }


def build_competition_context_text(template_ctx: Dict[str, Any]) -> str:
    lines = [
        f"- 当前赛事模板：{template_ctx['template_name']}（{template_ctx['template_id']}）",
        f"- 识别依据：{template_ctx['recognition_basis']}",
        f"- 评价口径提醒：{template_ctx['focus_hint']}",
        f"- 权重偏移说明：{template_ctx['expected_shift']}",
        "- 本轮必须使用以下 Rubric 维度与权重：",
    ]

    for item in template_ctx.get("rubric_items", []):
        lines.append(
            f"  * {item['dimension_id']} | {item['dimension_name']} | 类别={item['category']} | 权重={item['weight']} | "
            f"required_evidence={'; '.join(item['required_evidence'])} | common_mistakes={'; '.join(item['common_mistakes'])}"
        )
    return "\n".join(lines)
