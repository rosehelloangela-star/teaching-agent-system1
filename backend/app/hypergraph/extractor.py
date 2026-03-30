import json
from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate
from app.agents.mechanism.llm_config import get_llm
from app.core.json_utils import message_content_to_text, extract_first_json_value

def extract_hyperedges_from_text(text: str) -> Dict[str, List[str]]:
    if not text or not text.strip(): 
        return {}
        
    llm = get_llm(temperature=0.2, max_tokens=2500)
    
    # 【核心修复】：下面的 JSON 示例中使用了 {{ 和 }} 进行转义，防止 LangChain 报错
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个精通商业逻辑的结构化数据提取专家。请阅读输入的商业计划书文本，提取具体的业务内容，并将其打包成 JSON 格式的“超图（Hypergraph）实体”。

【可用超边名称（作为 JSON 的 Key）】
Core_Business_Loop, Customer_Value_Misalignment, Channel_Physical_Access, Willingness_To_Pay, Market_Reachability, Frequency_Mismatch, Unit_Economics, Pricing_Space, Cash_Flow_Health, Financial_Reasonableness, Supply_Chain_Sync, Cold_Start_Engine, R&D_Team_Match, Resource_Feasibility, Tech_Barrier, Real_Competition, Narrative_Causality, Innovation_Verification, Compliance_Ethics, Social_Value_Translation

【提取与组装规则（最高优先级）】
1. 格式强制：JSON 的 Value 必须是字符串数组，且每个字符串严格按照 "标准Key: 具体内容" 组装（例如 "Target_Customer: 农村留守群体"）。
2. 只要能找到一丁点相关信息，哪怕只有一个要素，也必须提取！严禁交白卷！如果完全找不到某分类信息，该 Key 可以不输出。
3. 确保交叉连通：如果同一个概念（比如“无人机”）在多个分类中用到，请保持其提取内容完全一致。

【输出规范示例】
{{
    "Core_Business_Loop": [
        "Target_Customer: 城市白领群体",
        "Value_Proposition: 提供快速匹配健身教练",
        "Marketing_Channel: 微信朋友圈广告",
        "Revenue_Model: 抽取课程费20%作为佣金"
    ],
    "Real_Competition": [
        "Alternative_Solution: 用户在小红书自己找教程",
        "Competitor_Pool: Keep等各大健身App"
    ],
    "Unit_Economics": [
        "CAC: 投放单客成本约50元",
        "LTV: 单客半年复购价值约300元"
    ],
    "R&D_Team_Match": [
        "Team_Background: 3名体育学院毕业生",
        "Tech_Route: 自研智能派单算法"
    ]
}}
"""),
        ("user", "提取以下文本中的商业要素，严格返回JSON对象：\n\n{text}")
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
                    cleaned_data[k] = [str(item) for item in v]
            
            print(f"[Extractor Debug] 成功提取超边: {list(cleaned_data.keys())}", flush=True)
            return cleaned_data
            
        print(f"[Extractor Debug] 提取失败，大模型返回非字典: {data}", flush=True)
        return {}
    except Exception as e:
        print(f"[Hypergraph Extractor] 实时超边抽取异常: {e}", flush=True)
        return {}