import json
from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate
from app.agents.mechanism.llm_config import get_llm
from app.core.json_utils import message_content_to_text, extract_first_json_value


def extract_hyperedges_from_text(text: str) -> Dict[str, List[str]]:
    if not text or not text.strip():
        return {}

    llm = get_llm(temperature=0.2, max_tokens=3200)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个精通创新创业项目结构化拆解的专家。请阅读输入文本，并提取成 JSON 格式的“超图（Hypergraph）实体”。

【抽取原则】
1. 先自行判断项目更偏“商业性项目”还是“公益项目”，但不要单独输出判断结论字段；直接按对应逻辑抽取相关超边。
2. 如果文本同时包含商业与公益信息，可以同时输出两类超边，但必须优先抽取信息最充分的那一类。
3. JSON 的 Value 必须是字符串数组，且每个字符串严格写成 "标准Key: 具体内容"。
4. 只要找到一点点相关信息，就必须输出；禁止因为信息不完整而整条超边留空。
5. 相同概念在多个超边中复用时，措辞尽量保持一致，方便后续拓扑连通判断。

【商业项目可用超边名称】
Core_Business_Loop, Customer_Value_Misalignment, Channel_Physical_Access, Willingness_To_Pay, Market_Reachability, Frequency_Mismatch, Unit_Economics, Pricing_Space, Cash_Flow_Health, Financial_Reasonableness, Supply_Chain_Sync, Cold_Start_Engine, R&D_Team_Match, Resource_Feasibility, Tech_Barrier, Real_Competition, Narrative_Causality, Innovation_Verification, Compliance_Ethics, Social_Value_Translation

【公益项目可用超边名称】
Public_Welfare_Targeting, Public_Welfare_Demand_Evidence, Public_Welfare_Value_Design, Stakeholder_Collaboration, Public_Welfare_Ethics_Safeguard, Fundraising_Model, Benefit_Cost_Efficiency, Impact_Measurement, Beneficiary_Conversion_Path, Public_Trust_Transparency, Pilot_Replication, Volunteer_Operations, Resource_Sustainability, Policy_Compliance_Public, Social_Value_CoCreation

【公益项目标准 Key 示例】
Beneficiary_Group, Urgency_Pain, Service_Scenario, Accessibility_Constraint,
Research_Sample, Field_Observation, Needs_Quote, Problem_Severity,
Intervention_Solution, Expected_Outcome, Core_Service, Trust_Mechanism,
Government_Link, NGO_Partner, Community_Leader, Volunteer_Source,
Vulnerable_Group, Ethical_Risk, Privacy_Protection, Consent_Process,
Funding_Source, Donation_Product, Grant_Channel, Revenue_Supplement,
Single_Service_Cost, Management_Cost, Fund_Use_Ratio, Budget_Ceiling,
Impact_Goal, Indicator_System, Baseline_Data, Evaluation_Method,
Reach_Channel, Participation_Motivation, Retention_Mechanism, Referral_Path,
Disclosure_Frequency, Financial_Disclosure, Story_Evidence, Third_Party_Endorsement,
Pilot_Site, Pilot_Result, Replication_Condition, Expansion_Path,
Volunteer_Role, Training_Process, Scheduling_Mechanism, Incentive_NonCash,
Key_Resource, Resource_Gap, Replacement_Plan, Risk_Buffer,
Policy_Basis, Qualification_Requirement, Safety_Redline, Public_Opinion_Risk,
Enterprise_Partner, School_Hospital_Community, CoCreation_Mode, Longterm_Mechanism

【输出规范示例】
{{
    "Core_Business_Loop": [
        "Target_Customer: 城市白领群体",
        "Value_Proposition: 提供快速匹配健身教练",
        "Marketing_Channel: 微信朋友圈广告",
        "Revenue_Model: 抽取课程费20%作为佣金"
    ],
    "Fundraising_Model": [
        "Funding_Source: 企业CSR与基金会联合资助",
        "Grant_Channel: 地方公益创投项目申报",
        "Revenue_Supplement: 为学校提供教师培训服务获取补充收入"
    ],
    "Impact_Measurement": [
        "Impact_Goal: 提升留守儿童课后陪伴覆盖率",
        "Indicator_System: 服务次数、持续参与率、心理量表改善",
        "Evaluation_Method: 前后测与班主任访谈结合"
    ]
}}
"""),
        ("user", "提取以下文本中的项目超图要素，严格返回 JSON 对象：\n\n{text}")
    ])

    try:
        response = (prompt | llm).invoke({"text": text})
        raw_text = message_content_to_text(response).strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[-1]
        if raw_text.endswith("```"):
            raw_text = raw_text.rsplit("\n", 1)[0]

        data = extract_first_json_value(raw_text)
        if isinstance(data, dict):
            cleaned_data = {}
            for k, v in data.items():
                if isinstance(v, list) and len(v) > 0:
                    cleaned_data[str(k)] = [str(item) for item in v if str(item).strip()]

            print(f"[Extractor Debug] 成功提取超边: {list(cleaned_data.keys())}", flush=True)
            return cleaned_data

        print(f"[Extractor Debug] 提取失败，大模型返回非字典: {data}", flush=True)
        return {}
    except Exception as e:
        print(f"[Hypergraph Extractor] 实时超边抽取异常: {e}", flush=True)
        return {}
