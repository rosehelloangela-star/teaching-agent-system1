# from __future__ import annotations

# from copy import deepcopy
# from typing import Any, Dict, List

# COMMON_DIMENSIONS: Dict[str, Dict[str, Any]] = {
#     "problem_definition": {
#         "dimension_name": "背景与问题定义",
#         "required_evidence": [
#             "明确的问题场景、用户对象或研究对象界定",
#             "痛点/问题严重性的事实依据或调研依据",
#             "为什么现在必须解决这个问题的背景说明",
#         ],
#         "common_mistakes": [
#             "把宏大口号当问题定义",
#             "目标人群范围过大，缺乏边界",
#             "没有用场景、数据或案例证明问题真实存在",
#         ],
#     },
#     "innovation_originality": {
#         "dimension_name": "创新突破与原创性",
#         "required_evidence": [
#             "相较现有方案的创新点拆解",
#             "创新来源或原创设计逻辑说明",
#             "与竞品/已有研究/已有解法的差异证明",
#         ],
#         "common_mistakes": [
#             "把功能堆砌误当创新",
#             "只讲概念新，不讲为什么难以复制",
#             "没有与现有方案进行横向对比",
#         ],
#     },
#     "core_solution": {
#         "dimension_name": "核心方案与科学论证",
#         "required_evidence": [
#             "核心技术路线或解决方案闭环图",
#             "关键机制、原理、流程或实验设计说明",
#             "支撑方案有效性的论证、测试或专家判断",
#         ],
#         "common_mistakes": [
#             "只有愿景，没有可执行方案",
#             "技术路径或业务路径描述模糊",
#             "结论先行，但没有论证过程",
#         ],
#     },
#     "data_visualization": {
#         "dimension_name": "数据与可视化支撑",
#         "required_evidence": [
#             "核心数据来源、样本口径或测算口径说明",
#             "关键图表、指标看板或结果可视化",
#             "数据与结论之间的对应关系说明",
#         ],
#         "common_mistakes": [
#             "只给结论，不给数据来源",
#             "图表好看但不支撑关键论点",
#             "把 TAM 或宏观市场数字直接当项目可得市场",
#         ],
#     },
#     "feasibility_execution": {
#         "dimension_name": "落地可行性与执行逻辑",
#         "required_evidence": [
#             "阶段计划、资源配置与里程碑",
#             "团队能力与任务匹配关系",
#             "交付路径、合作资源或关键前置条件",
#         ],
#         "common_mistakes": [
#             "计划与资源脱节",
#             "把长期目标写成短期里程碑",
#             "团队能力无法支撑关键执行环节",
#         ],
#     },
#     "benefit_prospect": {
#         "dimension_name": "综合效益与应用前景",
#         "required_evidence": [
#             "社会、经济、产业或用户价值说明",
#             "应用场景、推广路径或落地前景",
#             "预期收益或影响范围的合理估计",
#         ],
#         "common_mistakes": [
#             "价值陈述空泛，缺少量化指标",
#             "应用前景与当前阶段脱节",
#             "只讲愿景，不讲可实现的近期成果",
#         ],
#     },
#     "risk_robustness": {
#         "dimension_name": "风险评估与鲁棒性检验",
#         "required_evidence": [
#             "关键风险列表及应对策略",
#             "敏感性分析、备选方案或容错设计",
#             "合规、伦理、供应链或技术失败风险说明",
#         ],
#         "common_mistakes": [
#             "只写一句“风险可控”",
#             "没有识别最致命失败点",
#             "没有给出具体缓释措施",
#         ],
#     },
#     "logic_expression": {
#         "dimension_name": "规范与逻辑表达",
#         "required_evidence": [
#             "结构清晰的 BP/路演叙事",
#             "概念使用准确、逻辑顺序明确",
#             "图文配合、表达规范且结论一致",
#         ],
#         "common_mistakes": [
#             "叙事跳跃，前后矛盾",
#             "概念混用，术语不准确",
#             "页面精美但逻辑不成链",
#         ],
#     },
# }

# EXCLUSIVE_DIMENSIONS: Dict[str, Dict[str, Dict[str, Any]]] = {
#     "internet_plus": {
#         "business_finance": {
#             "dimension_name": "商业模式与财务回报",
#             "required_evidence": [
#                 "收入模式、成本结构与单位经济说明",
#                 "营收、利润或现金流测算依据",
#                 "价格、付费意愿与回本路径证明",
#             ],
#             "common_mistakes": [
#                 "收入模型与用户行为不匹配",
#                 "单位经济不成立却宣称可以盈利",
#                 "财务预测脱离获客与履约成本",
#             ],
#         },
#         "market_barrier_strategy": {
#             "dimension_name": "市场壁垒与营销策略",
#             "required_evidence": [
#                 "获客渠道与目标用户触达逻辑",
#                 "竞争壁垒、渠道优势或资源护城河",
#                 "营销转化路径与投放假设",
#             ],
#             "common_mistakes": [
#                 "客户与渠道错位",
#                 "把流量想象当成渠道能力",
#                 "没有真实替代方案与竞争者分析",
#             ],
#         },
#     },
#     "innovation_entrepreneurship": {
#         "practice_participation": {
#             "dimension_name": "实践过程与学生参与度",
#             "required_evidence": [
#                 "学生真实参与过程与分工记录",
#                 "调研、验证、访谈、制作等实践证据",
#                 "从想法到实践的迭代痕迹",
#             ],
#             "common_mistakes": [
#                 "只展示结果，不展示实践过程",
#                 "学生角色模糊，参与度不清晰",
#                 "把设想写成已完成实践",
#             ],
#         },
#         "stage_resource_integration": {
#             "dimension_name": "阶段性成果与资源整合",
#             "required_evidence": [
#                 "阶段性样机、合作、试点或奖项证据",
#                 "外部资源、导师、校内外支持说明",
#                 "后续资源整合与推进路径",
#             ],
#             "common_mistakes": [
#                 "阶段成果描述空泛",
#                 "资源整合只停留在口头设想",
#                 "缺乏可验证的中期成果",
#             ],
#         },
#     },
#     "math_modeling": {
#         "model_assumption_symbol": {
#             "dimension_name": "模型假设与符号系统",
#             "required_evidence": [
#                 "清晰的模型假设与变量定义",
#                 "符号系统、约束条件与边界说明",
#                 "建模对象与现实问题映射关系",
#             ],
#             "common_mistakes": [
#                 "假设不完整或相互冲突",
#                 "符号系统混乱",
#                 "模型与现实问题脱节",
#             ],
#         },
#         "algorithm_complexity_efficiency": {
#             "dimension_name": "算法复杂度与算力效能",
#             "required_evidence": [
#                 "算法流程与复杂度分析",
#                 "运行效率、资源消耗或求解可行性说明",
#                 "与替代算法或基线方法的效率比较",
#             ],
#             "common_mistakes": [
#                 "只写算法名，不分析复杂度",
#                 "忽视计算成本与可扩展性",
#                 "没有基线比较",
#             ],
#         },
#     },
#     "challenge_cup": {
#         "academic_value": {
#             "dimension_name": "学术价值与理论贡献",
#             "required_evidence": [
#                 "研究问题的学术意义说明",
#                 "理论、文献、已有研究的承接关系",
#                 "论文、报告或理论框架支撑材料",
#             ],
#             "common_mistakes": [
#                 "只有应用价值，没有学术问题意识",
#                 "缺乏文献基础或理论定位",
#                 "把常识性改进包装成理论贡献",
#             ],
#         },
#         "trl_maturity": {
#             "dimension_name": "技术成熟度（TRL）",
#             "required_evidence": [
#                 "技术原型、验证结果或成熟度阶段说明",
#                 "从实验室到应用的成熟路径",
#                 "关键技术依赖与落地条件说明",
#             ],
#             "common_mistakes": [
#                 "概念验证与工程化成熟度混淆",
#                 "没有原型却声称可快速落地",
#                 "缺少阶段验证与性能指标",
#             ],
#         },
#     },
# }

# TEMPLATE_REGISTRY: Dict[str, Dict[str, Any]] = {
#     "internet_plus": {
#         "template_name": "中国国际大学生创新大赛（原互联网+）",
#         "short_name": "互联网+",
#         "aliases": ["互联网+", "中国国际大学生创新大赛", "原互联网+", "创新大赛", "主赛道", "初创组"],
#         "weights": {
#             "problem_definition": 5,
#             "innovation_originality": 10,
#             "core_solution": 10,
#             "data_visualization": 10,
#             "feasibility_execution": 10,
#             "benefit_prospect": 10,
#             "risk_robustness": 5,
#             "logic_expression": 5,
#             "business_finance": 20,
#             "market_barrier_strategy": 15,
#         },
#         "exclusive_order": ["business_finance", "market_barrier_strategy"],
#         "focus_hint": "优先强调商业模式闭环、财务回报真实性、就业带动、渠道与市场壁垒。",
#         "expected_shift": "会显著提高对商业模式、单位经济、渠道策略和财务真实性的要求。",
#     },
#     "innovation_entrepreneurship": {
#         "template_name": "创新创业（大创）",
#         "short_name": "创新创业/大创",
#         "aliases": ["大创", "创新创业", "大学生创新创业", "创新创业训练计划", "创业训练", "创业项目"],
#         "weights": {
#             "problem_definition": 10,
#             "innovation_originality": 15,
#             "core_solution": 10,
#             "data_visualization": 10,
#             "feasibility_execution": 15,
#             "benefit_prospect": 10,
#             "risk_robustness": 5,
#             "logic_expression": 5,
#             "practice_participation": 10,
#             "stage_resource_integration": 10,
#         },
#         "exclusive_order": ["practice_participation", "stage_resource_integration"],
#         "focus_hint": "优先强调学生真实实践过程、阶段成果、资源整合与创新创业训练价值。",
#         "expected_shift": "会显著提高对实践过程证据、学生参与度和阶段性成果的要求。",
#     },
#     "math_modeling": {
#         "template_name": "数学建模竞赛",
#         "short_name": "数学建模",
#         "aliases": ["数学建模", "建模", "modeling", "数模"],
#         "weights": {
#             "problem_definition": 10,
#             "innovation_originality": 5,
#             "core_solution": 20,
#             "data_visualization": 15,
#             "feasibility_execution": 5,
#             "benefit_prospect": 5,
#             "risk_robustness": 10,
#             "logic_expression": 15,
#             "model_assumption_symbol": 10,
#             "algorithm_complexity_efficiency": 5,
#         },
#         "exclusive_order": ["model_assumption_symbol", "algorithm_complexity_efficiency"],
#         "focus_hint": "优先强调模型假设、符号系统、科学论证、算法复杂度与结果表达。",
#         "expected_shift": "会显著提高对模型规范性、数学严谨性和计算效率的要求。",
#     },
#     "challenge_cup": {
#         "template_name": "挑战杯全国大学生课外学术科技作品竞赛",
#         "short_name": "挑战杯",
#         "aliases": ["挑战杯", "课外学术科技作品竞赛", "学术科技作品", "挑战杯全国大学生"],
#         "weights": {
#             "problem_definition": 5,
#             "innovation_originality": 20,
#             "core_solution": 20,
#             "data_visualization": 10,
#             "feasibility_execution": 5,
#             "benefit_prospect": 10,
#             "risk_robustness": 5,
#             "logic_expression": 5,
#             "academic_value": 10,
#             "trl_maturity": 10,
#         },
#         "exclusive_order": ["academic_value", "trl_maturity"],
#         "focus_hint": "优先强调学术深度、技术创新壁垒、社会调查严谨性与技术成熟度。",
#         "expected_shift": "会显著提高对理论贡献、文献/专利支撑和技术成熟路径的要求。",
#     },
# }

# DEFAULT_TEMPLATE_ID = "innovation_entrepreneurship"


# def _build_rubric_items(template_id: str) -> List[Dict[str, Any]]:
#     template = TEMPLATE_REGISTRY[template_id]
#     items: List[Dict[str, Any]] = []

#     for dim_id, base in COMMON_DIMENSIONS.items():
#         items.append(
#             {
#                 "dimension_id": dim_id,
#                 "dimension_name": base["dimension_name"],
#                 "category": "common",
#                 "weight": template["weights"][dim_id],
#                 "required_evidence": deepcopy(base["required_evidence"]),
#                 "common_mistakes": deepcopy(base["common_mistakes"]),
#             }
#         )

#     for dim_id in template["exclusive_order"]:
#         base = EXCLUSIVE_DIMENSIONS[template_id][dim_id]
#         items.append(
#             {
#                 "dimension_id": dim_id,
#                 "dimension_name": base["dimension_name"],
#                 "category": "exclusive",
#                 "weight": template["weights"][dim_id],
#                 "required_evidence": deepcopy(base["required_evidence"]),
#                 "common_mistakes": deepcopy(base["common_mistakes"]),
#             }
#         )

#     return items


# def resolve_competition_template(text: str) -> Dict[str, Any]:
#     full_text = (text or "").lower()

#     best_template_id = DEFAULT_TEMPLATE_ID
#     best_alias = ""
#     best_score = -1

#     for template_id, template in TEMPLATE_REGISTRY.items():
#         score = 0
#         matched_alias = ""
#         for alias in template["aliases"]:
#             alias_lower = alias.lower()
#             if alias_lower in full_text:
#                 score += 2 if len(alias_lower) >= 4 else 1
#                 if len(alias_lower) > len(matched_alias):
#                     matched_alias = alias
#         if score > best_score:
#             best_score = score
#             best_template_id = template_id
#             best_alias = matched_alias

#     template = TEMPLATE_REGISTRY[best_template_id]
#     rubric_items = _build_rubric_items(best_template_id)
#     sorted_focus = sorted(rubric_items, key=lambda item: item["weight"], reverse=True)

#     return {
#         "template_id": best_template_id,
#         "template_name": template["template_name"],
#         "short_name": template["short_name"],
#         "matched_alias": best_alias or "未显式命中，按默认模板判定",
#         "recognition_basis": (
#             f"根据用户指令中的赛事关键词匹配到“{best_alias}”。"
#             if best_alias
#             else f"未命中明确赛事关键词，系统默认采用“{template['template_name']}”模板。"
#         ),
#         "focus_hint": template["focus_hint"],
#         "expected_shift": template["expected_shift"],
#         "total_weight": sum(item["weight"] for item in rubric_items),
#         "rubric_items": rubric_items,
#         "top_focus_dimensions": [
#             {
#                 "dimension_id": item["dimension_id"],
#                 "dimension_name": item["dimension_name"],
#                 "weight": item["weight"],
#             }
#             for item in sorted_focus[:4]
#         ],
#         "exclusive_dimensions": [
#             {
#                 "dimension_id": item["dimension_id"],
#                 "dimension_name": item["dimension_name"],
#                 "weight": item["weight"],
#             }
#             for item in rubric_items
#             if item["category"] == "exclusive"
#         ],
#     }


# def build_competition_context_text(template_ctx: Dict[str, Any]) -> str:
#     lines = [
#         f"- 当前赛事模板：{template_ctx['template_name']}（{template_ctx['template_id']}）",
#         f"- 识别依据：{template_ctx['recognition_basis']}",
#         f"- 评价口径提醒：{template_ctx['focus_hint']}",
#         f"- 权重偏移说明：{template_ctx['expected_shift']}",
#         "- 本轮必须使用以下 Rubric 维度与权重：",
#     ]

#     for item in template_ctx.get("rubric_items", []):
#         lines.append(
#             f"  * {item['dimension_id']} | {item['dimension_name']} | 类别={item['category']} | 权重={item['weight']} | "
#             f"required_evidence={'; '.join(item['required_evidence'])} | common_mistakes={'; '.join(item['common_mistakes'])}"
#         )
#     return "\n".join(lines)





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

JUDGE_EXPERT_LIBRARY: Dict[str, Dict[str, str]] = {
    "user_research": {
        "expert_id": "user_research",
        "expert_role": "用户研究与问题定义评委",
        "expert_domain": "用户/问题",
        "style_tag": "场景逼问",
        "signature": "我不接受口号，只接受真实场景。",
    },
    "innovation_review": {
        "expert_id": "innovation_review",
        "expert_role": "创新性与对标评委",
        "expert_domain": "创新/竞品",
        "style_tag": "差异逼问",
        "signature": "我不想听新概念，我只关心你和旧方案到底差在哪。",
    },
    "solution_science": {
        "expert_id": "solution_science",
        "expert_role": "技术方案与科学论证评委",
        "expert_domain": "技术/方案",
        "style_tag": "原理逼问",
        "signature": "原理讲不清，再漂亮的愿景都不算数。",
    },
    "data_validation": {
        "expert_id": "data_validation",
        "expert_role": "数据与验证评委",
        "expert_domain": "数据/验证",
        "style_tag": "证据逼问",
        "signature": "没有证据链，你的结论就只是感受。",
    },
    "execution_landing": {
        "expert_id": "execution_landing",
        "expert_role": "落地执行评委",
        "expert_domain": "执行/落地",
        "style_tag": "落地逼问",
        "signature": "我默认所有计划都会跳票，除非你证明不会。",
    },
    "value_impact": {
        "expert_id": "value_impact",
        "expert_role": "价值与应用前景评委",
        "expert_domain": "价值/应用",
        "style_tag": "价值逼问",
        "signature": "只讲愿景不讲近期成果，在我这里不会得高分。",
    },
    "risk_governance": {
        "expert_id": "risk_governance",
        "expert_role": "风险与合规评委",
        "expert_domain": "风险/合规",
        "style_tag": "极限逼问",
        "signature": "真正的风险不是你写出来的，而是你没意识到的。",
    },
    "expression_logic": {
        "expert_id": "expression_logic",
        "expert_role": "叙事与逻辑表达评委",
        "expert_domain": "表达/结构",
        "style_tag": "逻辑逼问",
        "signature": "我会默认你的漂亮页面在掩盖逻辑断裂。",
    },
    "business_finance": {
        "expert_id": "business_finance",
        "expert_role": "商业模式与财务评委",
        "expert_domain": "商业/财务",
        "style_tag": "盈利逼问",
        "signature": "谁付钱、为什么现在付、你凭什么不是越卖越亏？",
    },
    "market_growth": {
        "expert_id": "market_growth",
        "expert_role": "市场与增长评委",
        "expert_domain": "市场/增长",
        "style_tag": "增长逼问",
        "signature": "没有真实渠道与竞争认知，市场故事再大也站不住。",
    },
    "practice_process": {
        "expert_id": "practice_process",
        "expert_role": "实践过程评委",
        "expert_domain": "实践/参与",
        "style_tag": "真实性逼问",
        "signature": "我会追着问：这些事到底是不是学生真的做过。",
    },
    "resource_integration": {
        "expert_id": "resource_integration",
        "expert_role": "资源整合与阶段成果评委",
        "expert_domain": "资源/阶段成果",
        "style_tag": "成果逼问",
        "signature": "没有可验证的阶段成果，资源整合就还是 PPT 语言。",
    },
    "model_method": {
        "expert_id": "model_method",
        "expert_role": "建模方法评委",
        "expert_domain": "建模/假设",
        "style_tag": "建模逼问",
        "signature": "假设不成立，后面所有推导都没有意义。",
    },
    "algorithm_efficiency": {
        "expert_id": "algorithm_efficiency",
        "expert_role": "算法与复杂度评委",
        "expert_domain": "算法/效率",
        "style_tag": "复杂度逼问",
        "signature": "算法不是写了名字就结束，我要看代价和可扩展性。",
    },
    "academic_research": {
        "expert_id": "academic_research",
        "expert_role": "学术价值与文献评委",
        "expert_domain": "学术/文献",
        "style_tag": "理论逼问",
        "signature": "没有理论坐标，你的贡献很容易沦为常识性改进。",
    },
    "trl_engineering": {
        "expert_id": "trl_engineering",
        "expert_role": "技术成熟度评委",
        "expert_domain": "工程化/TRL",
        "style_tag": "成熟度逼问",
        "signature": "概念验证和可落地不是一回事。",
    },
}

DIMENSION_QUESTION_STRATEGIES: Dict[str, Dict[str, Any]] = {
    "problem_definition": {
        "expert_id": "user_research",
        "pressure_level": "高压追问",
        "attack_point": "质疑你是否真的抓住了明确而刚性的真实问题",
        "evidence_hint": "场景边界、用户访谈、痛点证据",
        "question_templates": [
            "你一直在讲{dimension_name}，但我只听到口号，没有听到具体对象。请你用一句话回答：到底是谁，在什么场景下，因为哪个痛点愿意立刻换方案？",
            "如果我要求你删掉所有宏大叙事，只保留一个最小且最痛的问题场景，你还能把这个项目为什么现在必须存在说清楚吗？",
        ],
    },
    "innovation_originality": {
        "expert_id": "innovation_review",
        "pressure_level": "差异追问",
        "attack_point": "质疑你的创新是否只是功能堆砌或换皮表达",
        "evidence_hint": "竞品对比、原创机制、不可替代性证明",
        "question_templates": [
            "你说自己有创新，但如果我把行业里前三种已有方案摆在台上，你到底比它们多解决了什么、少付出了什么，还是只是换了个说法？",
            "请你别再说“我们更智能/更高效”这种空话。你能指出一个别人目前做不到、而你能稳定做到的关键差异吗？",
        ],
    },
    "core_solution": {
        "expert_id": "solution_science",
        "pressure_level": "原理追问",
        "attack_point": "质疑你的核心方案是否有完整原理链和可执行闭环",
        "evidence_hint": "技术路线、关键机制、实验或验证过程",
        "question_templates": [
            "我现在最担心的是：你的方案听起来很完整，但真正关键的一步到底怎么发生？如果没有那一步，你的方案是不是立刻失效？",
            "请你别再重复愿景。你就回答一件事：你的核心机制是什么，它为什么有效，你拿什么证明它不是拍脑袋？",
        ],
    },
    "data_visualization": {
        "expert_id": "data_validation",
        "pressure_level": "证据追问",
        "attack_point": "质疑你的图表和数据是否真的支撑关键结论",
        "evidence_hint": "数据来源、样本口径、图表与结论对应关系",
        "question_templates": [
            "你这页图表看起来很多，但我没看到口径。请你告诉我：数据从哪来、样本是什么、这张图到底支撑了哪个关键判断？",
            "如果我现在问你“这组数字为什么可信”，你是拿调研口径、实验记录，还是只是拿网络公开资料来凑数？",
        ],
    },
    "feasibility_execution": {
        "expert_id": "execution_landing",
        "pressure_level": "落地追问",
        "attack_point": "质疑你的执行计划是否能真正落地而不是里程碑拼贴",
        "evidence_hint": "里程碑、资源配置、团队分工、合作资源",
        "question_templates": [
            "你的计划写得很满，但我只想知道：下一阶段真正负责的人是谁、关键资源在哪里、如果其中一项不到位，你的项目会卡死在哪一步？",
            "你现在展示的是计划，不是落地。请你告诉我，未来三个月最先能交付的硬结果是什么，谁来做，凭什么做得出来？",
        ],
    },
    "benefit_prospect": {
        "expert_id": "value_impact",
        "pressure_level": "价值追问",
        "attack_point": "质疑你的价值陈述是否停留在愿景层面",
        "evidence_hint": "应用场景、短期成果、量化收益或影响指标",
        "question_templates": [
            "你一直在讲前景很好，但评委不会给愿景打高分。请你告诉我：这个项目在最近一段时间能交付什么可验证价值，而不是三年后的想象？",
            "如果我要你只保留一个最能说服评委的价值指标，你会留下什么？为什么它不是一句空泛的“社会意义重大”？",
        ],
    },
    "risk_robustness": {
        "expert_id": "risk_governance",
        "pressure_level": "极限追问",
        "attack_point": "质疑你是否识别到真正致命的失败点",
        "evidence_hint": "关键风险、备选方案、敏感性分析、合规说明",
        "question_templates": [
            "你写“风险可控”这四个字，在我这里几乎等于没写。请你直接说：这个项目最可能死在哪个环节，你准备怎么救？",
            "如果最核心假设失败、关键合作方退出，或者合规条件突然变化，你的项目是有备选路径，还是当场停摆？",
        ],
    },
    "logic_expression": {
        "expert_id": "expression_logic",
        "pressure_level": "逻辑追问",
        "attack_point": "质疑你的叙事是否结构清楚且前后自洽",
        "evidence_hint": "章节结构、术语一致性、结论与材料对应关系",
        "question_templates": [
            "你的页面做得不差，但我担心你在用视觉掩盖逻辑断裂。请你不用 PPT，只用三句话把“问题—方案—价值”讲成一条闭环。",
            "如果我现在把你路演稿顺序打乱，你的论证还成立吗？还是说一换顺序，逻辑就露馅了？",
        ],
    },
    "business_finance": {
        "expert_id": "business_finance",
        "pressure_level": "盈利追问",
        "attack_point": "质疑你的商业模式、付费逻辑与单位经济是否成立",
        "evidence_hint": "谁付费、定价依据、成本结构、回本路径",
        "question_templates": [
            "你一直在讲市场空间，但我只关心一件事：到底谁付钱、为什么现在付、你靠什么证明自己不是越卖越亏？",
            "如果我要求你现在当场拆一次单笔交易的收入、成本和毛利，你能不能说清楚，还是你的盈利只是写在表格里的愿望？",
        ],
    },
    "market_barrier_strategy": {
        "expert_id": "market_growth",
        "pressure_level": "增长追问",
        "attack_point": "质疑你的渠道、竞争认知和壁垒是否真实",
        "evidence_hint": "获客渠道、竞争对手、转化路径、壁垒依据",
        "question_templates": [
            "你说自己有市场壁垒，但我没看到真正的对手分析。请你告诉我：如果一个更有钱、更有渠道的对手明天照着做，你凭什么不被瞬间替代？",
            "你的增长逻辑到底是渠道验证过了，还是只是默认“用户会自己来”？如果让我追问首批用户从哪来、怎么转化，你准备拿什么回答？",
        ],
    },
    "practice_participation": {
        "expert_id": "practice_process",
        "pressure_level": "真实性追问",
        "attack_point": "质疑所谓实践过程是否真实发生且由学生主导",
        "evidence_hint": "实践记录、学生分工、访谈/制作/测试痕迹",
        "question_templates": [
            "你现在讲的是“我们做过很多实践”，但我没看到过程证据。请你告诉我：哪些环节是学生自己真正做的，有什么痕迹能证明？",
            "如果我现在随机追问一个成员：他到底访谈了谁、做了什么验证、迭代了什么内容，你的团队能对得上吗？",
        ],
    },
    "stage_resource_integration": {
        "expert_id": "resource_integration",
        "pressure_level": "成果追问",
        "attack_point": "质疑你的阶段成果和资源整合是否停留在口头层面",
        "evidence_hint": "试点/样机/合作/奖项证据、资源支撑路径",
        "question_templates": [
            "你说已经有阶段成果，那请你别泛讲。现在就告诉我：最像“硬结果”的那一项是什么，它能不能被评委当场验证？",
            "你提到很多导师、合作和资源，但这些到底是已经落实的支撑，还是你希望未来会发生的关系？",
        ],
    },
    "model_assumption_symbol": {
        "expert_id": "model_method",
        "pressure_level": "建模追问",
        "attack_point": "质疑你的模型假设、变量定义和现实映射是否严谨",
        "evidence_hint": "模型假设、变量定义、边界条件、现实映射",
        "question_templates": [
            "你的模型一旦假设错了，后面所有推导都不成立。请你告诉我：最关键的那个假设是什么，它为什么合理？",
            "如果我现在要求你解释一个核心变量的现实含义和边界条件，你能解释清楚，还是只是把符号写上去了？",
        ],
    },
    "algorithm_complexity_efficiency": {
        "expert_id": "algorithm_efficiency",
        "pressure_level": "复杂度追问",
        "attack_point": "质疑你的算法是否有复杂度与效率支撑",
        "evidence_hint": "算法流程、复杂度分析、资源消耗、基线对比",
        "question_templates": [
            "你提了算法，但没有代价。请你回答：时间复杂度、资源消耗和可扩展性分别是什么，你为什么觉得它能跑得动？",
            "如果我拿一个更简单的基线方法来和你比，你是在哪个指标上真的更优，而不是只是模型名字更高级？",
        ],
    },
    "academic_value": {
        "expert_id": "academic_research",
        "pressure_level": "理论追问",
        "attack_point": "质疑你的研究是否具有清晰的学术问题意识与理论贡献",
        "evidence_hint": "研究意义、文献承接、理论框架、学术空白",
        "question_templates": [
            "你说有学术价值，但我没看到理论坐标。请你直接回答：你的工作补的是哪一块空白，而不是单纯把已有方法换个场景？",
            "如果我问“已有研究为什么还不够，你的贡献到底新增了什么”，你是能给出文献层面的回答，还是只能继续讲应用价值？",
        ],
    },
    "trl_maturity": {
        "expert_id": "trl_engineering",
        "pressure_level": "成熟度追问",
        "attack_point": "质疑你的技术成熟度与工程化路径是否被夸大",
        "evidence_hint": "原型、测试结果、成熟度阶段、工程化条件",
        "question_templates": [
            "你现在展示的是概念验证、实验结果，还是已经接近可用原型？请不要混着讲，因为这三件事在评审里不是一个层级。",
            "如果评委要求你说明“从实验室样机走到真实应用还差哪几步”，你能不能说清楚每一步的技术和资源门槛？",
        ],
    },
}

TEMPLATE_JUDGE_PANEL: Dict[str, List[str]] = {
    "internet_plus": ["business_finance", "market_growth", "user_research", "solution_science", "execution_landing"],
    "innovation_entrepreneurship": ["practice_process", "resource_integration", "user_research", "solution_science", "execution_landing"],
    "math_modeling": ["model_method", "algorithm_efficiency", "data_validation", "expression_logic", "risk_governance"],
    "challenge_cup": ["academic_research", "trl_engineering", "solution_science", "innovation_review", "data_validation"],
}


def build_dimension_question_blueprint(template_id: str, dimension_id: str) -> Dict[str, Any]:
    strategy = deepcopy(DIMENSION_QUESTION_STRATEGIES.get(dimension_id, {}))
    expert = deepcopy(JUDGE_EXPERT_LIBRARY.get(strategy.get("expert_id", "expression_logic"), JUDGE_EXPERT_LIBRARY["expression_logic"]))
    return {
        "expert_id": expert.get("expert_id"),
        "expert_role": expert.get("expert_role"),
        "expert_domain": expert.get("expert_domain"),
        "style_tag": expert.get("style_tag"),
        "signature": expert.get("signature"),
        "pressure_level": strategy.get("pressure_level", "高压追问"),
        "attack_point": strategy.get("attack_point", "质疑该维度的核心论证是否成立"),
        "evidence_hint": strategy.get("evidence_hint", "补齐该维度的关键证据"),
        "question_templates": deepcopy(strategy.get("question_templates", [])),
        "template_id": template_id,
    }



def build_template_judge_panel(template_id: str) -> List[Dict[str, str]]:
    expert_ids = TEMPLATE_JUDGE_PANEL.get(template_id, TEMPLATE_JUDGE_PANEL.get(DEFAULT_TEMPLATE_ID, []))
    panel: List[Dict[str, str]] = []
    for expert_id in expert_ids:
        expert = deepcopy(JUDGE_EXPERT_LIBRARY.get(expert_id))
        if expert:
            panel.append(expert)
    return panel



def _build_rubric_items(template_id: str) -> List[Dict[str, Any]]:
    template = TEMPLATE_REGISTRY[template_id]
    items: List[Dict[str, Any]] = []

    for dim_id, base in COMMON_DIMENSIONS.items():
        blueprint = build_dimension_question_blueprint(template_id, dim_id)
        items.append(
            {
                "dimension_id": dim_id,
                "dimension_name": base["dimension_name"],
                "category": "common",
                "weight": template["weights"][dim_id],
                "required_evidence": deepcopy(base["required_evidence"]),
                "common_mistakes": deepcopy(base["common_mistakes"]),
                "primary_expert_id": blueprint["expert_id"],
                "primary_expert_role": blueprint["expert_role"],
                "primary_expert_domain": blueprint["expert_domain"],
                "question_focus": blueprint["attack_point"],
            }
        )

    for dim_id in template["exclusive_order"]:
        base = EXCLUSIVE_DIMENSIONS[template_id][dim_id]
        blueprint = build_dimension_question_blueprint(template_id, dim_id)
        items.append(
            {
                "dimension_id": dim_id,
                "dimension_name": base["dimension_name"],
                "category": "exclusive",
                "weight": template["weights"][dim_id],
                "required_evidence": deepcopy(base["required_evidence"]),
                "common_mistakes": deepcopy(base["common_mistakes"]),
                "primary_expert_id": blueprint["expert_id"],
                "primary_expert_role": blueprint["expert_role"],
                "primary_expert_domain": blueprint["expert_domain"],
                "question_focus": blueprint["attack_point"],
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
        "judge_panel": build_template_judge_panel(best_template_id),
        "top_focus_dimensions": [
            {
                "dimension_id": item["dimension_id"],
                "dimension_name": item["dimension_name"],
                "weight": item["weight"],
                "primary_expert_role": item.get("primary_expert_role"),
            }
            for item in sorted_focus[:4]
        ],
        "exclusive_dimensions": [
            {
                "dimension_id": item["dimension_id"],
                "dimension_name": item["dimension_name"],
                "weight": item["weight"],
                "primary_expert_role": item.get("primary_expert_role"),
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
        "- 本轮可模拟的评委席：",
    ]

    for expert in template_ctx.get("judge_panel", []):
        lines.append(
            f"  * {expert.get('expert_role')} | 领域={expert.get('expert_domain')} | 风格={expert.get('style_tag')} | 口头禅={expert.get('signature')}"
        )

    lines.append("- 本轮必须使用以下 Rubric 维度与权重：")
    for item in template_ctx.get("rubric_items", []):
        lines.append(
            f"  * {item['dimension_id']} | {item['dimension_name']} | 类别={item['category']} | 权重={item['weight']} | "
            f"主审={item.get('primary_expert_role')} | 追问重点={item.get('question_focus')} | "
            f"required_evidence={'; '.join(item['required_evidence'])} | common_mistakes={'; '.join(item['common_mistakes'])}"
        )
    return "\n".join(lines)
