import hypernetx as hnx
from typing import List, Dict, Any

class HypergraphEngine:
    def __init__(self):
        self.hg = None
        
        # ==========================================
        # 1. 20 条复杂商业逻辑超边（理想拓扑结构模板）
        # ==========================================
        self.expected_hyperedges = {
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
            "Social_Value_Translation": ["Scenario_Research", "Pilot_Cooperation", "Translation_Roadmap"]
        }

    def build_hypergraph(self, extracted_hyperedges: Dict[str, List[str]]):
        """
        基于大模型提取的实体构建真实超图
        extracted_hyperedges 格式示例: {"Core_Business_Loop": ["下沉市场", "手环", "社区推广"]}
        """
        edge_dict = {}
        for edge_type, nodes in extracted_hyperedges.items():
            valid_nodes = [n.strip() for n in nodes if n.strip()]
            if len(valid_nodes) > 0:
                edge_dict[edge_type] = valid_nodes
                
        # 使用 HyperNetX 实例化超图
        self.hg = hnx.Hypergraph(edge_dict)
        return self.hg

    def run_topology_diagnostics(self) -> List[Dict[str, Any]]:
        """
        ========================================================
        2. 20 条基于拓扑结构的超图一致性诊断规则 (Rule Checkers)
        ========================================================
        利用图论属性（交集、子集、度数、连通性）判断商业逻辑的断层
        """
        if not self.hg:
            return [{"rule": "System", "issue": "超图未初始化或提取为空，项目缺乏基础业务实体。", "severity": "high"}]

        alerts = []
        
        # 【修复点 1】：兼容 HyperNetX 新版 API，安全获取所有超边的名称集合
        try:
            active_edges = set(list(self.hg.edges))
        except Exception:
            active_edges = set()

        # 【修复点 2】：安全获取某条超边内的节点集合，使用 incidence_dict 最稳定
        def get_edge_nodes(edge_name: str) -> set:
            if edge_name in active_edges:
                try:
                    # 优先使用关联矩阵字典提取节点
                    return set(self.hg.incidence_dict[edge_name])
                except AttributeError:
                    # 备用提取方式
                    return set(self.hg.edges[edge_name])
            return set()

        # --- 规则 1-5：全局与连通性诊断 (孤岛与碎片化) ---
        
        # R1: 核心缺位诊断 
        if "Core_Business_Loop" not in active_edges:
            alerts.append({"rule": "R1", "name": "全局逻辑散架", "issue": "未检测到核心商业闭环(Core_Business_Loop)，项目当前是散装概念，无法构成商业体。", "severity": "critical"})
            
        # R2: 超图全局割裂检测 
        core_nodes = get_edge_nodes("Core_Business_Loop")
        tech_nodes = get_edge_nodes("Tech_Barrier")
        if core_nodes and tech_nodes and not core_nodes.intersection(tech_nodes):
            alerts.append({"rule": "R2", "name": "技术与商业双轨孤岛", "issue": "技术壁垒超边与商业闭环超边没有任何共享节点，你的技术没有融合进商业模式中。", "severity": "critical"})

        # R3: 痛点悬空检测 
        narrative_nodes = get_edge_nodes("Narrative_Causality")
        if narrative_nodes and len(narrative_nodes) < 2:
             alerts.append({"rule": "R3", "name": "叙事因果断裂", "issue": f"叙事超边内节点过少({narrative_nodes})，痛点与方案之间缺乏逻辑连接节点。", "severity": "high"})

        # R4: 节点利用率过低 
        comp_nodes = get_edge_nodes("Compliance_Ethics")
        if comp_nodes and not comp_nodes.intersection(core_nodes):
            alerts.append({"rule": "R4", "name": "合规逻辑游离", "issue": "分析了合规限制，但这些限制没有作用于你的核心商业闭环，属于无效分析。", "severity": "medium"})

        # R5: 核心要素缺失比率 
        if core_nodes and len(core_nodes) < len(self.expected_hyperedges["Core_Business_Loop"]) * 0.6:
            alerts.append({"rule": "R5", "name": "闭环要素严重缺失", "issue": f"商业闭环超边萎缩，当前仅包含 {core_nodes}，缺失超过 40% 的关键定义。", "severity": "high"})


        # --- 规则 6-10：市场与竞争拓扑诊断 (交集错位) ---
        
        # R6: 渠道物理不可达 
        channel_nodes = get_edge_nodes("Channel_Physical_Access")
        if channel_nodes and core_nodes and not channel_nodes.intersection(core_nodes):
            alerts.append({"rule": "R6", "name": "渠道与客群脱节", "issue": "提取到的渠道触达超边与核心商业闭环没有任何节点交集，渠道无法触达你的目标客群。", "severity": "critical"})

        # R7: 支付意愿悖论 
        wtp_nodes = get_edge_nodes("Willingness_To_Pay")
        if wtp_nodes and len(wtp_nodes) < 3:
             alerts.append({"rule": "R7", "name": "支付意愿支撑不足", "issue": "痛点与定价之间缺乏 '可支配收入' 节点的连接，无法证明用户买得起。", "severity": "high"})

        # R8: 竞争真空幻觉 
        if "Real_Competition" not in active_edges:
            alerts.append({"rule": "R8", "name": "无竞争对手幻觉", "issue": "竞争超边完全缺失，项目陷入了市场完全空白的幻觉中。", "severity": "critical"})

        # R9: 市场规模口径断层 
        market_nodes = get_edge_nodes("Market_Reachability")
        if market_nodes and len(market_nodes) < 3:
            alerts.append({"rule": "R9", "name": "市场漏斗断层", "issue": "TAM/SAM/SOM 超边未能形成完整的漏斗集合，规模推算存在断层。", "severity": "medium"})

        # R10: 创新自嗨 
        innov_nodes = get_edge_nodes("Innovation_Verification")
        comp_pool_nodes = get_edge_nodes("Real_Competition")
        if innov_nodes and comp_pool_nodes and not innov_nodes.intersection(comp_pool_nodes):
            alerts.append({"rule": "R10", "name": "创新缺乏竞争对标", "issue": "你的创新验证超边与竞争格局超边没有交点，优势没有在竞品中得到验证。", "severity": "high"})


        # --- 规则 11-15：财务与执行诊断 (节点缺失与断路) ---

        # R11: 单位经济模型不闭环
        ue_nodes = get_edge_nodes("Unit_Economics")
        if "Unit_Economics" in active_edges and len(ue_nodes) < 2:
            alerts.append({"rule": "R11", "name": "单位经济模型崩塌", "issue": "UE超边内 LTV 或 CAC 节点缺失，无法证明单客盈利能力。", "severity": "critical"})

        # R12: 定价与利润空间挤压
        pricing_nodes = get_edge_nodes("Pricing_Space")
        if pricing_nodes and len(pricing_nodes) < 2:
             alerts.append({"rule": "R12", "name": "利润空间黑盒", "issue": "定价超边中缺失可变成本或固定成本节点，无法推导利润空间。", "severity": "high"})

        # R13: 现金流断裂风险 
        cash_nodes = get_edge_nodes("Cash_Flow_Health")
        if cash_nodes and "Account_Period" in str(cash_nodes) and len(cash_nodes) < 3:
             alerts.append({"rule": "R13", "name": "现金流断裂高危", "issue": "存在账期节点，但缺乏足够的启动资金节点与之形成闭环缓冲。", "severity": "critical"})

        # R14: 履约交付断层
        supply_nodes = get_edge_nodes("Supply_Chain_Sync")
        if supply_nodes and core_nodes and not supply_nodes.intersection(core_nodes):
             alerts.append({"rule": "R14", "name": "供应链脱离业务", "issue": "供应链超边存在，但与商业闭环毫无交集，产品的交付链路断裂。", "severity": "high"})

        # R15: 冷启动策略空转
        cold_nodes = get_edge_nodes("Cold_Start_Engine")
        if cold_nodes and not cold_nodes.intersection(core_nodes):
             alerts.append({"rule": "R15", "name": "冷启动策略空转", "issue": "设计的冷启动策略节点没有作用于核心目标客群节点。", "severity": "medium"})


        # --- 规则 16-20：资源、科研与价值延伸诊断 ---

        # R16: 团队与技术断层
        team_tech_nodes = get_edge_nodes("R&D_Team_Match")
        if "R&D_Team_Match" in active_edges and len(team_tech_nodes) < 2:
             alerts.append({"rule": "R16", "name": "技术壁垒无团队支撑", "issue": "技术路径节点游离，未能与团队背景节点连接在同一超边内。", "severity": "high"})

        # R17: 执行方案空壳
        feasibility_nodes = get_edge_nodes("Resource_Feasibility")
        if feasibility_nodes and len(feasibility_nodes) < 2:
             alerts.append({"rule": "R17", "name": "执行方案空壳", "issue": "资源可行性超边缺失具体的里程碑或风险控制节点。", "severity": "medium"})

        # R18: 财务预测缺乏基石
        fin_reason_nodes = get_edge_nodes("Financial_Reasonableness")
        if fin_reason_nodes and not fin_reason_nodes.intersection(core_nodes):
             alerts.append({"rule": "R18", "name": "财务预测漂浮", "issue": "财务假设超边没有建立在核心商业要素（客单价/客群）之上。", "severity": "high"})

        # R19: 高频场景错配
        freq_nodes = get_edge_nodes("Frequency_Mismatch")
        if freq_nodes and len(freq_nodes) >= 2: 
             alerts.append({"rule": "R19", "name": "频次与收入模型错配", "issue": "检测到使用频次节点与现行收入模型节点存在强烈的互斥逻辑。", "severity": "high"})

        # R20: 社会价值未转化
        social_nodes = get_edge_nodes("Social_Value_Translation")
        if social_nodes and not social_nodes.intersection(core_nodes):
             alerts.append({"rule": "R20", "name": "公益属性过重", "issue": "社会价值超边完全独立于商业闭环，项目偏向纯公益，缺乏商业造血转化机制。", "severity": "medium"})

        return alerts