import hypernetx as hnx
from typing import List, Dict, Any

from app.hypergraph.stage_config import (
    PROJECT_TYPE_COMMERCIAL,
    PROJECT_TYPE_PUBLIC_WELFARE,
    detect_project_type,
)


class HypergraphEngine:
    def __init__(self):
        self.hg = None
        self.source_text = ""
        self.project_type = PROJECT_TYPE_COMMERCIAL

        self.commercial_expected_hyperedges = {
            "Core_Business_Loop": ["Target_Customer", "Value_Proposition", "Marketing_Channel", "Revenue_Model", "Cost_Structure"],
            "Customer_Value_Misalignment": ["Target_Customer", "Value_Proposition"],
            "Channel_Physical_Access": ["Target_Customer", "Marketing_Channel"],
            "Willingness_To_Pay": ["Core_Pain_Point", "Disposable_Income", "Price"],
            "Market_Reachability": ["TAM", "SAM", "SOM", "Marketing_Budget"],
            "Frequency_Mismatch": ["Usage_Frequency", "Revenue_Model", "Unit_Price"],
            "Unit_Economics": ["LTV", "CAC"],
            "Pricing_Space": ["Price", "Fixed_Cost", "Variable_Cost"],
            "Cash_Flow_Health": ["Customer_Type", "Account_Period", "Startup_Capital", "Burn_Rate"],
            "Financial_Reasonableness": ["Financial_Model", "Key_Assumption", "Sensitivity_Analysis"],
            "Supply_Chain_Sync": ["Product_Form", "Delivery_Method", "Fulfill_Cost", "Supplier_Network"],
            "Cold_Start_Engine": ["Platform_Model", "Seed_Users", "Cold_Start_Strategy"],
            "R&D_Team_Match": ["TRL", "Team_Background"],
            "Resource_Feasibility": ["Tech_Route", "Resource_List", "Milestone_Plan"],
            "Tech_Barrier": ["Core_Advantage", "Competitor_Status", "Switching_Cost", "IP"],
            "Real_Competition": ["Current_Pain", "Alternative_Solution", "Competitor_Pool"],
            "Narrative_Causality": ["Core_Pain_Point", "Solution", "Revenue_Model"],
            "Innovation_Verification": ["Differentiation", "Verifiable_Metric", "Control_Experiment"],
            "Compliance_Ethics": ["Data_Source", "Industry", "Policy_Constraints"],
            "Social_Value_Translation": ["Scenario_Research", "Pilot_Cooperation", "Translation_Roadmap"],
        }

        self.public_welfare_expected_hyperedges = {
            "Public_Welfare_Targeting": ["Beneficiary_Group", "Urgency_Pain", "Service_Scenario", "Accessibility_Constraint"],
            "Public_Welfare_Demand_Evidence": ["Research_Sample", "Field_Observation", "Needs_Quote", "Problem_Severity"],
            "Public_Welfare_Value_Design": ["Intervention_Solution", "Expected_Outcome", "Core_Service", "Trust_Mechanism"],
            "Stakeholder_Collaboration": ["Government_Link", "NGO_Partner", "Community_Leader", "Volunteer_Source"],
            "Public_Welfare_Ethics_Safeguard": ["Vulnerable_Group", "Ethical_Risk", "Privacy_Protection", "Consent_Process"],
            "Fundraising_Model": ["Funding_Source", "Donation_Product", "Grant_Channel", "Revenue_Supplement"],
            "Benefit_Cost_Efficiency": ["Single_Service_Cost", "Management_Cost", "Fund_Use_Ratio", "Budget_Ceiling"],
            "Impact_Measurement": ["Impact_Goal", "Indicator_System", "Baseline_Data", "Evaluation_Method"],
            "Beneficiary_Conversion_Path": ["Reach_Channel", "Participation_Motivation", "Retention_Mechanism", "Referral_Path"],
            "Public_Trust_Transparency": ["Disclosure_Frequency", "Financial_Disclosure", "Story_Evidence", "Third_Party_Endorsement"],
            "Pilot_Replication": ["Pilot_Site", "Pilot_Result", "Replication_Condition", "Expansion_Path"],
            "Volunteer_Operations": ["Volunteer_Role", "Training_Process", "Scheduling_Mechanism", "Incentive_NonCash"],
            "Resource_Sustainability": ["Key_Resource", "Resource_Gap", "Replacement_Plan", "Risk_Buffer"],
            "Policy_Compliance_Public": ["Policy_Basis", "Qualification_Requirement", "Safety_Redline", "Public_Opinion_Risk"],
            "Social_Value_CoCreation": ["Enterprise_Partner", "School_Hospital_Community", "CoCreation_Mode", "Longterm_Mechanism"],
        }

    @property
    def expected_hyperedges(self) -> Dict[str, List[str]]:
        if self.project_type == PROJECT_TYPE_PUBLIC_WELFARE:
            return self.public_welfare_expected_hyperedges
        return self.commercial_expected_hyperedges

    def build_hypergraph(self, extracted_hyperedges: Dict[str, List[str]], source_text: str = ""):
        self.source_text = source_text or ""
        self.project_type = detect_project_type(self.source_text, extracted_hyperedges)

        edge_dict = {}
        for edge_type, nodes in (extracted_hyperedges or {}).items():
            valid_nodes = [str(n).strip() for n in nodes if str(n).strip()]
            if len(valid_nodes) > 0:
                edge_dict[edge_type] = valid_nodes

        self.hg = hnx.Hypergraph(edge_dict)
        return self.hg

    def run_topology_diagnostics(self) -> List[Dict[str, Any]]:
        if not self.hg or len(self.hg.edges) == 0:
            return [{
                "rule": "System",
                "name": "图谱元素过少",
                "issue": "当前文本信息过少或大模型未提取到有效超边，无法进行拓扑网络检测。",
                "severity": "high",
            }]

        try:
            active_edges = set(list(self.hg.edges))
        except Exception:
            active_edges = set()

        def get_edge_nodes(edge_name: str) -> set:
            if edge_name in active_edges:
                try:
                    return set(self.hg.incidence_dict[edge_name])
                except Exception:
                    try:
                        return set(self.hg.edges[edge_name])
                    except Exception:
                        return set()
            return set()

        def has_field(edge_name: str, field_key: str) -> bool:
            for node in get_edge_nodes(edge_name):
                token = str(node).split(":", 1)[0].split("：", 1)[0].strip()
                if token == field_key:
                    return True
            return False

        if self.project_type == PROJECT_TYPE_PUBLIC_WELFARE:
            return self._run_public_welfare_diagnostics(active_edges, get_edge_nodes, has_field)
        return self._run_commercial_diagnostics(active_edges, get_edge_nodes)

    def _run_commercial_diagnostics(self, active_edges, get_edge_nodes) -> List[Dict[str, Any]]:
        alerts = []
        if "Core_Business_Loop" not in active_edges:
            alerts.append({"rule": "R1", "name": "全局逻辑散架", "issue": "未检测到核心商业闭环(Core_Business_Loop)，项目当前是散装概念，无法构成商业体。", "severity": "critical"})

        core_nodes = get_edge_nodes("Core_Business_Loop")
        tech_nodes = get_edge_nodes("Tech_Barrier")
        if core_nodes and tech_nodes and not core_nodes.intersection(tech_nodes):
            alerts.append({"rule": "R2", "name": "技术与商业双轨孤岛", "issue": "技术壁垒超边与商业闭环超边没有任何共享节点，你的技术没有融合进商业模式中。", "severity": "critical"})

        narrative_nodes = get_edge_nodes("Narrative_Causality")
        if "Narrative_Causality" in active_edges and not narrative_nodes:
            alerts.append({"rule": "R3", "name": "叙事因果断裂", "issue": "叙事超边内缺乏连接节点，痛点与方案之间缺乏逻辑连接。", "severity": "high"})

        comp_nodes = get_edge_nodes("Compliance_Ethics")
        if comp_nodes and not comp_nodes.intersection(core_nodes):
            alerts.append({"rule": "R4", "name": "合规逻辑游离", "issue": "分析了合规限制，但这些限制没有作用于你的核心商业闭环，属于无效分析。", "severity": "medium"})

        if core_nodes and len(core_nodes) < len(self.commercial_expected_hyperedges["Core_Business_Loop"]) * 0.4:
            alerts.append({"rule": "R5", "name": "闭环要素严重缺失", "issue": f"商业闭环超边萎缩，当前仅包含 {core_nodes}，缺失过多关键定义。", "severity": "high"})

        channel_nodes = get_edge_nodes("Channel_Physical_Access")
        if channel_nodes and core_nodes and not channel_nodes.intersection(core_nodes):
            alerts.append({"rule": "R6", "name": "渠道与客群脱节", "issue": "提取到的渠道触达超边与核心商业闭环没有任何节点交集，渠道无法触达你的目标客群。", "severity": "critical"})

        wtp_nodes = get_edge_nodes("Willingness_To_Pay")
        if wtp_nodes and len(wtp_nodes) < 2:
            alerts.append({"rule": "R7", "name": "支付意愿支撑不足", "issue": "痛点与定价之间缺乏 '可支配收入' 节点的连接，无法证明用户买得起。", "severity": "high"})

        if "Real_Competition" not in active_edges:
            alerts.append({"rule": "R8", "name": "无竞争对手幻觉", "issue": "竞争超边完全缺失，项目陷入了市场完全空白的幻觉中。", "severity": "critical"})

        market_nodes = get_edge_nodes("Market_Reachability")
        if market_nodes and len(market_nodes) < 2:
            alerts.append({"rule": "R9", "name": "市场漏斗断层", "issue": "TAM/SAM/SOM 超边未能形成漏斗，规模推算存在断层。", "severity": "medium"})

        innov_nodes = get_edge_nodes("Innovation_Verification")
        comp_pool_nodes = get_edge_nodes("Real_Competition")
        if innov_nodes and comp_pool_nodes and not innov_nodes.intersection(comp_pool_nodes):
            alerts.append({"rule": "R10", "name": "创新缺乏竞争对标", "issue": "你的创新验证超边与竞争格局超边没有交点，优势没有在竞品中得到验证。", "severity": "high"})

        ue_nodes = get_edge_nodes("Unit_Economics")
        if "Unit_Economics" in active_edges and not ue_nodes:
            alerts.append({"rule": "R11", "name": "单位经济模型崩塌", "issue": "UE超边内 LTV 或 CAC 节点缺失，无法证明单客盈利能力。", "severity": "critical"})

        pricing_nodes = get_edge_nodes("Pricing_Space")
        if "Pricing_Space" in active_edges and not pricing_nodes:
            alerts.append({"rule": "R12", "name": "利润空间黑盒", "issue": "定价超边中缺失可变成本或固定成本节点，无法推导利润空间。", "severity": "high"})

        cash_nodes = get_edge_nodes("Cash_Flow_Health")
        if cash_nodes and "Account_Period" in str(cash_nodes) and len(cash_nodes) < 2:
            alerts.append({"rule": "R13", "name": "现金流断裂高危", "issue": "存在账期节点，但缺乏足够的启动资金节点与之形成闭环缓冲。", "severity": "critical"})

        supply_nodes = get_edge_nodes("Supply_Chain_Sync")
        if supply_nodes and core_nodes and not supply_nodes.intersection(core_nodes):
            alerts.append({"rule": "R14", "name": "供应链脱离业务", "issue": "供应链超边存在，但与商业闭环毫无交集，产品的交付链路断裂。", "severity": "high"})

        cold_nodes = get_edge_nodes("Cold_Start_Engine")
        if cold_nodes and not cold_nodes.intersection(core_nodes):
            alerts.append({"rule": "R15", "name": "冷启动策略空转", "issue": "设计的冷启动策略节点没有作用于核心目标客群节点。", "severity": "medium"})

        team_tech_nodes = get_edge_nodes("R&D_Team_Match")
        if "R&D_Team_Match" in active_edges and not team_tech_nodes:
            alerts.append({"rule": "R16", "name": "技术壁垒无团队支撑", "issue": "技术路径节点游离，未能与团队背景节点连接。", "severity": "high"})

        feasibility_nodes = get_edge_nodes("Resource_Feasibility")
        if "Resource_Feasibility" in active_edges and not feasibility_nodes:
            alerts.append({"rule": "R17", "name": "执行方案空壳", "issue": "资源可行性超边缺失具体的里程碑或风险控制节点。", "severity": "medium"})

        fin_reason_nodes = get_edge_nodes("Financial_Reasonableness")
        if fin_reason_nodes and not fin_reason_nodes.intersection(core_nodes):
            alerts.append({"rule": "R18", "name": "财务预测漂浮", "issue": "财务假设超边没有建立在核心商业要素（客单价/客群）之上。", "severity": "high"})

        freq_nodes = get_edge_nodes("Frequency_Mismatch")
        if freq_nodes and len(freq_nodes) >= 3:
            alerts.append({"rule": "R19", "name": "频次与收入模型错配", "issue": "检测到使用频次节点与现行收入模型节点存在强烈的互斥逻辑。", "severity": "high"})

        social_nodes = get_edge_nodes("Social_Value_Translation")
        if social_nodes and not social_nodes.intersection(core_nodes):
            alerts.append({"rule": "R20", "name": "公益属性过重", "issue": "社会价值超边完全独立于商业闭环，项目偏向纯公益，缺乏商业造血转化机制。", "severity": "medium"})
        return alerts

    def _run_public_welfare_diagnostics(self, active_edges, get_edge_nodes, has_field) -> List[Dict[str, Any]]:
        alerts = []

        def node_count(edge_name: str) -> int:
            return len(get_edge_nodes(edge_name))

        def has_any_field(edge_name: str, fields: List[str]) -> bool:
            return any(has_field(edge_name, field) for field in fields)

        def overlap_ratio(a: str, b: str) -> float:
            a_nodes = get_edge_nodes(a)
            b_nodes = get_edge_nodes(b)
            if not a_nodes or not b_nodes:
                return 0.0
            inter = a_nodes.intersection(b_nodes)
            base = min(len(a_nodes), len(b_nodes)) or 1
            return len(inter) / base

        def edge_strength(edge_name: str, key_fields: List[str] | None = None) -> int:
            score = 0
            cnt = node_count(edge_name)
            if cnt >= 1:
                score += 1
            if cnt >= 2:
                score += 1
            if cnt >= 3:
                score += 1
            if key_fields and has_any_field(edge_name, key_fields):
                score += 1
            return score

        # ===== 第一阶段：对象 / 需求 / 方案 =====

        targeting_strength = edge_strength(
            "Public_Welfare_Targeting",
            ["Beneficiary_Group", "Service_Scenario", "Urgency_Pain"]
        )
        demand_strength = edge_strength(
            "Public_Welfare_Demand_Evidence",
            ["Research_Sample", "Field_Observation", "Needs_Quote", "Problem_Severity"]
        )
        value_strength = edge_strength(
            "Public_Welfare_Value_Design",
            ["Intervention_Solution", "Core_Service", "Expected_Outcome"]
        )
        stakeholder_strength = edge_strength(
            "Stakeholder_Collaboration",
            ["Government_Link", "NGO_Partner", "Community_Leader", "Volunteer_Source"]
        )
        ethics_strength = edge_strength(
            "Public_Welfare_Ethics_Safeguard",
            ["Vulnerable_Group", "Ethical_Risk", "Privacy_Protection", "Consent_Process"]
        )

        if "Public_Welfare_Targeting" not in active_edges:
            alerts.append({
                "rule": "PR1",
                "name": "受益对象界定偏弱",
                "issue": "暂未明确抽取到公益服务对象定义超边，建议至少补清受益群体、服务场景和问题紧迫性中的两项。",
                "severity": "high"
            })
        elif targeting_strength <= 1:
            alerts.append({
                "rule": "PR1",
                "name": "受益对象界定偏弱",
                "issue": "公益对象超边已出现，但信息还偏少；只要再补充受益群体、服务场景或紧迫痛点中的任意一项，结构就会更稳定。",
                "severity": "medium"
            })

        if "Public_Welfare_Demand_Evidence" not in active_edges:
            if targeting_strength <= 1 and value_strength <= 1:
                alerts.append({
                    "rule": "PR2",
                    "name": "公益需求证据偏弱",
                    "issue": "目前真实需求证据不足，建议至少补一类调研依据：样本、走访观察、原话引述或问题严重度。",
                    "severity": "high"
                })
        elif demand_strength <= 1:
            alerts.append({
                "rule": "PR2",
                "name": "公益需求证据偏弱",
                "issue": "需求证据超边已有雏形，但样本、观察、引述、严重度这几类证据还不够完整，建议补 1 到 2 类即可。",
                "severity": "medium"
            })

        if "Public_Welfare_Value_Design" not in active_edges:
            alerts.append({
                "rule": "PR3",
                "name": "服务设计表达不充分",
                "issue": "暂未明确抽取到公益服务设计超边，建议补清干预方式、核心服务和预期改变，不必一次写得很满。",
                "severity": "high"
            })
        elif value_strength <= 1:
            alerts.append({
                "rule": "PR3",
                "name": "服务设计表达不充分",
                "issue": "服务设计已经出现，但干预动作、服务内容和预期成效还没有形成更完整的链条。",
                "severity": "medium"
            })
        elif "Public_Welfare_Demand_Evidence" in active_edges and demand_strength >= 2:
            # 放宽：只有双方都较完整且完全无交集，才提醒
            if overlap_ratio("Public_Welfare_Value_Design", "Public_Welfare_Demand_Evidence") == 0 and value_strength >= 3 and demand_strength >= 3:
                alerts.append({
                    "rule": "PR3",
                    "name": "服务设计与需求证据连接偏弱",
                    "issue": "方案与需求证据都写出来了，但当前结构上还没明显连起来，建议补一处“某个需求证据如何对应某个服务动作”。",
                    "severity": "medium"
                })

        if "Stakeholder_Collaboration" not in active_edges:
            alerts.append({
                "rule": "PR4",
                "name": "协同方配置偏弱",
                "issue": "当前还没稳定抽取到政府/社区/公益组织/志愿者等协同关系，建议补 1 到 2 个关键合作方即可。",
                "severity": "medium"
            })
        elif stakeholder_strength <= 1:
            alerts.append({
                "rule": "PR4",
                "name": "协同方配置偏弱",
                "issue": "协同方已有，但合作角色、来源或链接机制还不够清楚。",
                "severity": "low"
            })

        if "Public_Welfare_Ethics_Safeguard" not in active_edges:
            # 放宽：不直接 critical
            alerts.append({
                "rule": "PR5",
                "name": "伦理保护表述不足",
                "issue": "尚未明显抽取到隐私、同意或弱势群体保护内容。若项目涉及未成年人、老人、残障等群体，建议补一句保护机制。",
                "severity": "medium"
            })
        elif ethics_strength <= 1:
            alerts.append({
                "rule": "PR5",
                "name": "伦理保护表述不足",
                "issue": "伦理保护内容已经出现，但保护动作还比较薄，建议补充隐私、知情同意或风险控制中的任意一项。",
                "severity": "low"
            })

        # ===== 第二阶段：筹资 / 效率 / 影响 =====

        funding_strength = edge_strength(
            "Fundraising_Model",
            ["Funding_Source", "Grant_Channel", "Donation_Product", "Revenue_Supplement"]
        )
        efficiency_strength = edge_strength(
            "Benefit_Cost_Efficiency",
            ["Single_Service_Cost", "Fund_Use_Ratio", "Management_Cost"]
        )
        impact_strength = edge_strength(
            "Impact_Measurement",
            ["Impact_Goal", "Indicator_System", "Baseline_Data", "Evaluation_Method"]
        )
        conversion_strength = edge_strength(
            "Beneficiary_Conversion_Path",
            ["Reach_Channel", "Participation_Motivation", "Retention_Mechanism", "Referral_Path"]
        )
        trust_strength = edge_strength(
            "Public_Trust_Transparency",
            ["Financial_Disclosure", "Third_Party_Endorsement", "Disclosure_Frequency", "Story_Evidence"]
        )

        if "Fundraising_Model" not in active_edges:
            alerts.append({
                "rule": "PR6",
                "name": "筹资路径偏弱",
                "issue": "当前还没有明显形成筹资模型，建议先补一个主要资金来源或申请渠道，不要求一次写成完整融资方案。",
                "severity": "high"
            })
        elif funding_strength <= 1:
            alerts.append({
                "rule": "PR6",
                "name": "筹资路径偏弱",
                "issue": "筹资逻辑已有，但来源或渠道还不够清楚，补充一类稳定资金来源即可明显改善。",
                "severity": "medium"
            })

        if "Benefit_Cost_Efficiency" not in active_edges:
            alerts.append({
                "rule": "PR7",
                "name": "公益成本效率说明不足",
                "issue": "目前成本效率结构不明显，建议至少补一个“单次服务成本”或“资金使用比例”类信息。",
                "severity": "medium"
            })
        elif efficiency_strength <= 1:
            alerts.append({
                "rule": "PR7",
                "name": "公益成本效率说明不足",
                "issue": "成本效率已有雏形，但仍缺少更清晰的成本口径或资金使用说明。",
                "severity": "low"
            })

        if "Impact_Measurement" not in active_edges:
            alerts.append({
                "rule": "PR8",
                "name": "影响评估可验证性偏弱",
                "issue": "当前缺少影响评估结构，建议补一个目标、一个指标或一种前后对比方式即可。",
                "severity": "high"
            })
        elif impact_strength <= 1:
            alerts.append({
                "rule": "PR8",
                "name": "影响评估可验证性偏弱",
                "issue": "评估逻辑已出现，但指标、基线或方法还不够清楚。",
                "severity": "medium"
            })
        elif "Public_Welfare_Value_Design" in active_edges and value_strength >= 2:
            if overlap_ratio("Impact_Measurement", "Public_Welfare_Value_Design") == 0 and impact_strength >= 3 and value_strength >= 3:
                alerts.append({
                    "rule": "PR8",
                    "name": "影响评估与服务方案连接偏弱",
                    "issue": "评估与服务都写到了，但两者还没在结构上明显对应，建议补一句“哪个服务动作对应哪个成效指标”。",
                    "severity": "low"
                })

        if "Beneficiary_Conversion_Path" not in active_edges:
            alerts.append({
                "rule": "PR9",
                "name": "受益者触达路径偏弱",
                "issue": "目前还没形成清晰的触达与参与路径，建议补充“怎么找到人、怎么让人参与”中的任意一环。",
                "severity": "medium"
            })
        elif conversion_strength <= 1:
            alerts.append({
                "rule": "PR9",
                "name": "受益者触达路径偏弱",
                "issue": "触达路径已有，但参与激励、留存或转介逻辑还不够清楚。",
                "severity": "low"
            })

        if "Public_Trust_Transparency" not in active_edges:
            alerts.append({
                "rule": "PR10",
                "name": "公信力与透明度偏弱",
                "issue": "当前缺少公示、披露或第三方背书结构，建议补一个透明机制即可。",
                "severity": "medium"
            })
        elif trust_strength <= 1:
            alerts.append({
                "rule": "PR10",
                "name": "公信力与透明度偏弱",
                "issue": "透明机制已有雏形，但披露频率、财务公开或背书材料还不够清晰。",
                "severity": "low"
            })

        # ===== 第三阶段：复制 / 治理 / 长期协同 =====

        pilot_strength = edge_strength(
            "Pilot_Replication",
            ["Pilot_Site", "Pilot_Result", "Replication_Condition", "Expansion_Path"]
        )
        volunteer_strength = edge_strength(
            "Volunteer_Operations",
            ["Volunteer_Role", "Training_Process", "Scheduling_Mechanism", "Incentive_NonCash"]
        )
        resource_strength = edge_strength(
            "Resource_Sustainability",
            ["Key_Resource", "Resource_Gap", "Replacement_Plan", "Risk_Buffer"]
        )
        policy_strength = edge_strength(
            "Policy_Compliance_Public",
            ["Policy_Basis", "Qualification_Requirement", "Safety_Redline", "Public_Opinion_Risk"]
        )
        cocreation_strength = edge_strength(
            "Social_Value_CoCreation",
            ["Enterprise_Partner", "School_Hospital_Community", "CoCreation_Mode", "Longterm_Mechanism"]
        )

        if "Pilot_Replication" not in active_edges:
            alerts.append({
                "rule": "PR11",
                "name": "试点复制路径偏弱",
                "issue": "当前还没明显形成试点复制结构，建议补“试点结果”或“扩散路径”中的任意一项。",
                "severity": "high"
            })
        elif pilot_strength <= 1:
            alerts.append({
                "rule": "PR11",
                "name": "试点复制路径偏弱",
                "issue": "试点结构已经出现，但复制条件或扩散路径仍不够清晰。",
                "severity": "medium"
            })

        if "Volunteer_Operations" not in active_edges:
            alerts.append({
                "rule": "PR12",
                "name": "志愿者运营机制偏弱",
                "issue": "若项目依赖志愿者，建议补充角色、培训或排班中的任意一项；若不依赖志愿者，这条可弱化处理。",
                "severity": "low"
            })
        elif volunteer_strength <= 1:
            alerts.append({
                "rule": "PR12",
                "name": "志愿者运营机制偏弱",
                "issue": "志愿者运营已有雏形，但训练、调度或激励机制还偏弱。",
                "severity": "low"
            })

        if "Resource_Sustainability" not in active_edges:
            alerts.append({
                "rule": "PR13",
                "name": "关键资源续航说明不足",
                "issue": "目前缺少资源续航结构，建议补一个核心资源及其替代/缓冲方案。",
                "severity": "high"
            })
        elif resource_strength <= 1:
            alerts.append({
                "rule": "PR13",
                "name": "关键资源续航说明不足",
                "issue": "资源续航结构已有，但替代方案或风险缓冲还不够明确。",
                "severity": "medium"
            })

        if "Policy_Compliance_Public" not in active_edges:
            alerts.append({
                "rule": "PR14",
                "name": "政策合规表述偏弱",
                "issue": "当前缺少政策/资质/安全红线结构，建议至少补一条合规依据或执行边界。",
                "severity": "high"
            })
        elif policy_strength <= 1:
            alerts.append({
                "rule": "PR14",
                "name": "政策合规表述偏弱",
                "issue": "合规结构已出现，但资质、安全或舆情风险还没有写得足够明确。",
                "severity": "medium"
            })

        if "Social_Value_CoCreation" not in active_edges:
            alerts.append({
                "rule": "PR15",
                "name": "社会共创机制偏弱",
                "issue": "当前多方共创结构还不明显，建议补一个学校/社区/医院/企业等长期合作方。",
                "severity": "low"
            })
        elif cocreation_strength <= 1:
            alerts.append({
                "rule": "PR15",
                "name": "社会共创机制偏弱",
                "issue": "共创机制已有，但合作方式或长期机制描述还比较薄。",
                "severity": "low"
            })

        return alerts


# import hypernetx as hnx
# from typing import List, Dict, Any

# class HypergraphEngine:
#     def __init__(self):
#         self.hg = None
        
#         # ==========================================
#         # 1. 20 条复杂商业逻辑超边（理想拓扑结构模板）
#         # ==========================================
#         self.expected_hyperedges = {
#             "Core_Business_Loop": ["Target_Customer", "Value_Proposition", "Marketing_Channel", "Revenue_Model", "Cost_Structure"],
#             "Customer_Value_Misalignment": ["Target_Customer", "Value_Proposition"],
#             "Channel_Physical_Access": ["Target_Customer", "Marketing_Channel"],
#             "Willingness_To_Pay": ["Core_Pain_Point", "Disposable_Income", "Price"],
#             "Market_Reachability": ["TAM", "SAM", "SOM", "Marketing_Budget"],
#             "Frequency_Mismatch": ["Usage_Frequency", "Revenue_Model", "Unit_Price"],
#             "Unit_Economics": ["LTV", "CAC"],
#             "Pricing_Space": ["Price", "Fixed_Cost", "Variable_Cost"],
#             "Cash_Flow_Health": ["Customer_Type", "Account_Period", "Startup_Capital", "Burn_Rate"],
#             "Financial_Reasonableness": ["Financial_Model", "Key_Assumption", "Sensitivity_Analysis"],
#             "Supply_Chain_Sync": ["Product_Form", "Delivery_Method", "Fulfill_Cost", "Supplier_Network"],
#             "Cold_Start_Engine": ["Platform_Model", "Seed_Users", "Cold_Start_Strategy"],
#             "R&D_Team_Match": ["TRL", "Team_Background"],
#             "Resource_Feasibility": ["Tech_Route", "Resource_List", "Milestone_Plan"],
#             "Tech_Barrier": ["Core_Advantage", "Competitor_Status", "Switching_Cost", "IP"],
#             "Real_Competition": ["Current_Pain", "Alternative_Solution", "Competitor_Pool"],
#             "Narrative_Causality": ["Core_Pain_Point", "Solution", "Revenue_Model"],
#             "Innovation_Verification": ["Differentiation", "Verifiable_Metric", "Control_Experiment"],
#             "Compliance_Ethics": ["Data_Source", "Industry", "Policy_Constraints"],
#             "Social_Value_Translation": ["Scenario_Research", "Pilot_Cooperation", "Translation_Roadmap"]
#         }

#     def build_hypergraph(self, extracted_hyperedges: Dict[str, List[str]]):
#         """
#         基于大模型提取的实体构建真实超图
#         extracted_hyperedges 格式示例: {"Core_Business_Loop": ["下沉市场", "手环", "社区推广"]}
#         """
#         edge_dict = {}
#         for edge_type, nodes in extracted_hyperedges.items():
#             valid_nodes = [n.strip() for n in nodes if n.strip()]
#             if len(valid_nodes) > 0:
#                 edge_dict[edge_type] = valid_nodes
                
#         # 使用 HyperNetX 实例化超图
#         self.hg = hnx.Hypergraph(edge_dict)
#         return self.hg

#     def run_topology_diagnostics(self) -> List[Dict[str, Any]]:
#         """
#         ========================================================
#         2. 20 条基于拓扑结构的超图一致性诊断规则 (Rule Checkers)
#         ========================================================
#         利用图论属性（交集、子集、度数、连通性）判断商业逻辑的断层
#         """
#         # 【修复点】：增加 len 判断，且补充缺失的 "name" 键
#         if not self.hg or len(self.hg.edges) == 0:
#             return [{
#                 "rule": "System", 
#                 "name": "图谱元素过少", 
#                 "issue": "当前文本信息过少或大模型未提取到有效超边，无法进行拓扑网络检测。", 
#                 "severity": "high"
#             }]

#         alerts = []
        
#         # 【修复点 1】：兼容 HyperNetX 新版 API，安全获取所有超边的名称集合
#         try:
#             active_edges = set(list(self.hg.edges))
#         except Exception:
#             active_edges = set()

#         # 【修复点 2】：安全获取某条超边内的节点集合，使用 incidence_dict 最稳定
#         def get_edge_nodes(edge_name: str) -> set:
#             if edge_name in active_edges:
#                 try:
#                     # 优先使用关联矩阵字典提取节点
#                     return set(self.hg.incidence_dict[edge_name])
#                 except AttributeError:
#                     # 备用提取方式
#                     return set(self.hg.edges[edge_name])
#             return set()

#         # --- 规则 1-5：全局与连通性诊断 (孤岛与碎片化) ---
        
#         # R1: 核心缺位诊断 
#         if "Core_Business_Loop" not in active_edges:
#             alerts.append({"rule": "R1", "name": "全局逻辑散架", "issue": "未检测到核心商业闭环(Core_Business_Loop)，项目当前是散装概念，无法构成商业体。", "severity": "critical"})
            
#         # R2: 超图全局割裂检测 
#         core_nodes = get_edge_nodes("Core_Business_Loop")
#         tech_nodes = get_edge_nodes("Tech_Barrier")
#         if core_nodes and tech_nodes and not core_nodes.intersection(tech_nodes):
#             alerts.append({"rule": "R2", "name": "技术与商业双轨孤岛", "issue": "技术壁垒超边与商业闭环超边没有任何共享节点，你的技术没有融合进商业模式中。", "severity": "critical"})

#         # R3: 痛点悬空检测 
#         narrative_nodes = get_edge_nodes("Narrative_Causality")
#         if narrative_nodes and len(narrative_nodes) < 2:
#              alerts.append({"rule": "R3", "name": "叙事因果断裂", "issue": f"叙事超边内节点过少({narrative_nodes})，痛点与方案之间缺乏逻辑连接节点。", "severity": "high"})

#         # R4: 节点利用率过低 
#         comp_nodes = get_edge_nodes("Compliance_Ethics")
#         if comp_nodes and not comp_nodes.intersection(core_nodes):
#             alerts.append({"rule": "R4", "name": "合规逻辑游离", "issue": "分析了合规限制，但这些限制没有作用于你的核心商业闭环，属于无效分析。", "severity": "medium"})

#         # R5: 核心要素缺失比率 
#         if core_nodes and len(core_nodes) < len(self.expected_hyperedges["Core_Business_Loop"]) * 0.6:
#             alerts.append({"rule": "R5", "name": "闭环要素严重缺失", "issue": f"商业闭环超边萎缩，当前仅包含 {core_nodes}，缺失超过 40% 的关键定义。", "severity": "high"})


#         # --- 规则 6-10：市场与竞争拓扑诊断 (交集错位) ---
        
#         # R6: 渠道物理不可达 
#         channel_nodes = get_edge_nodes("Channel_Physical_Access")
#         if channel_nodes and core_nodes and not channel_nodes.intersection(core_nodes):
#             alerts.append({"rule": "R6", "name": "渠道与客群脱节", "issue": "提取到的渠道触达超边与核心商业闭环没有任何节点交集，渠道无法触达你的目标客群。", "severity": "critical"})

#         # R7: 支付意愿悖论 
#         wtp_nodes = get_edge_nodes("Willingness_To_Pay")
#         if wtp_nodes and len(wtp_nodes) < 3:
#              alerts.append({"rule": "R7", "name": "支付意愿支撑不足", "issue": "痛点与定价之间缺乏 '可支配收入' 节点的连接，无法证明用户买得起。", "severity": "high"})

#         # R8: 竞争真空幻觉 
#         if "Real_Competition" not in active_edges:
#             alerts.append({"rule": "R8", "name": "无竞争对手幻觉", "issue": "竞争超边完全缺失，项目陷入了市场完全空白的幻觉中。", "severity": "critical"})

#         # R9: 市场规模口径断层 
#         market_nodes = get_edge_nodes("Market_Reachability")
#         if market_nodes and len(market_nodes) < 3:
#             alerts.append({"rule": "R9", "name": "市场漏斗断层", "issue": "TAM/SAM/SOM 超边未能形成完整的漏斗集合，规模推算存在断层。", "severity": "medium"})

#         # R10: 创新自嗨 
#         innov_nodes = get_edge_nodes("Innovation_Verification")
#         comp_pool_nodes = get_edge_nodes("Real_Competition")
#         if innov_nodes and comp_pool_nodes and not innov_nodes.intersection(comp_pool_nodes):
#             alerts.append({"rule": "R10", "name": "创新缺乏竞争对标", "issue": "你的创新验证超边与竞争格局超边没有交点，优势没有在竞品中得到验证。", "severity": "high"})


#         # --- 规则 11-15：财务与执行诊断 (节点缺失与断路) ---

#         # R11: 单位经济模型不闭环
#         ue_nodes = get_edge_nodes("Unit_Economics")
#         if "Unit_Economics" in active_edges and len(ue_nodes) < 2:
#             alerts.append({"rule": "R11", "name": "单位经济模型崩塌", "issue": "UE超边内 LTV 或 CAC 节点缺失，无法证明单客盈利能力。", "severity": "critical"})

#         # R12: 定价与利润空间挤压
#         pricing_nodes = get_edge_nodes("Pricing_Space")
#         if pricing_nodes and len(pricing_nodes) < 2:
#              alerts.append({"rule": "R12", "name": "利润空间黑盒", "issue": "定价超边中缺失可变成本或固定成本节点，无法推导利润空间。", "severity": "high"})

#         # R13: 现金流断裂风险 
#         cash_nodes = get_edge_nodes("Cash_Flow_Health")
#         if cash_nodes and "Account_Period" in str(cash_nodes) and len(cash_nodes) < 3:
#              alerts.append({"rule": "R13", "name": "现金流断裂高危", "issue": "存在账期节点，但缺乏足够的启动资金节点与之形成闭环缓冲。", "severity": "critical"})

#         # R14: 履约交付断层
#         supply_nodes = get_edge_nodes("Supply_Chain_Sync")
#         if supply_nodes and core_nodes and not supply_nodes.intersection(core_nodes):
#              alerts.append({"rule": "R14", "name": "供应链脱离业务", "issue": "供应链超边存在，但与商业闭环毫无交集，产品的交付链路断裂。", "severity": "high"})

#         # R15: 冷启动策略空转
#         cold_nodes = get_edge_nodes("Cold_Start_Engine")
#         if cold_nodes and not cold_nodes.intersection(core_nodes):
#              alerts.append({"rule": "R15", "name": "冷启动策略空转", "issue": "设计的冷启动策略节点没有作用于核心目标客群节点。", "severity": "medium"})


#         # --- 规则 16-20：资源、科研与价值延伸诊断 ---

#         # R16: 团队与技术断层
#         team_tech_nodes = get_edge_nodes("R&D_Team_Match")
#         if "R&D_Team_Match" in active_edges and len(team_tech_nodes) < 2:
#              alerts.append({"rule": "R16", "name": "技术壁垒无团队支撑", "issue": "技术路径节点游离，未能与团队背景节点连接在同一超边内。", "severity": "high"})

#         # R17: 执行方案空壳
#         feasibility_nodes = get_edge_nodes("Resource_Feasibility")
#         if feasibility_nodes and len(feasibility_nodes) < 2:
#              alerts.append({"rule": "R17", "name": "执行方案空壳", "issue": "资源可行性超边缺失具体的里程碑或风险控制节点。", "severity": "medium"})

#         # R18: 财务预测缺乏基石
#         fin_reason_nodes = get_edge_nodes("Financial_Reasonableness")
#         if fin_reason_nodes and not fin_reason_nodes.intersection(core_nodes):
#              alerts.append({"rule": "R18", "name": "财务预测漂浮", "issue": "财务假设超边没有建立在核心商业要素（客单价/客群）之上。", "severity": "high"})

#         # R19: 高频场景错配
#         freq_nodes = get_edge_nodes("Frequency_Mismatch")
#         if freq_nodes and len(freq_nodes) >= 2: 
#              alerts.append({"rule": "R19", "name": "频次与收入模型错配", "issue": "检测到使用频次节点与现行收入模型节点存在强烈的互斥逻辑。", "severity": "high"})

#         # R20: 社会价值未转化
#         social_nodes = get_edge_nodes("Social_Value_Translation")
#         if social_nodes and not social_nodes.intersection(core_nodes):
#              alerts.append({"rule": "R20", "name": "公益属性过重", "issue": "社会价值超边完全独立于商业闭环，项目偏向纯公益，缺乏商业造血转化机制。", "severity": "medium"})

#         return alerts