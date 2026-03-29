# 文件路径：backend/app/hypergraph/extractor.py

from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate
from app.agents.mechanism.llm_config import get_llm
from app.core.json_utils import message_content_to_text, extract_first_json_value

def extract_hyperedges_from_text(text: str) -> Dict[str, List[str]]:
    """
    供 Agent (critic.py) 实时调用：
    使用大模型从学生提交的单段文本中提取符合 20 条定义的超边簇。
    """
    if not text or not text.strip(): 
        return {}
        
    llm = get_llm(temperature=0.1, max_tokens=2500)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        你是顶级的双创商业逻辑建模专家。请提取文本中的多元超边关系（Hyperedges）。
        
        【强制约束：只能使用以下 20 个英文 Key 作为 JSON 的键】
        Core_Business_Loop, Customer_Value_Misalignment, Channel_Physical_Access, Willingness_To_Pay, 
        Market_Reachability, Frequency_Mismatch, Unit_Economics, Pricing_Space, Cash_Flow_Health, 
        Financial_Reasonableness, Supply_Chain_Sync, Cold_Start_Engine, R&D_Team_Match, Resource_Feasibility, 
        Tech_Barrier, Real_Competition, Narrative_Causality, Innovation_Verification, Compliance_Ethics, 
        Social_Value_Translation。
        
        【抽取规则】
        只有当文本中确实包含了某类逻辑的实质性要素时，才提取该超边。提取的值必须是具体的短语实体。
        
        【输出格式】
        只输出合法 JSON 对象，键为超边名称，值为实体名称数组。示例：
        {{
            "Core_Business_Loop": ["下沉市场", "防丢手环", "按次付费"],
            "Tech_Barrier": ["低功耗算法", "暂无竞品", "实用新型专利"]
        }}
        """),
        ("user", "提取以下文本中的超边逻辑簇：\n{text}")
    ])
    
    try:
        response = (prompt | llm).invoke({"text": text})
        data = extract_first_json_value(message_content_to_text(response))
        if isinstance(data, dict):
            # 过滤掉空数组
            return {k: v for k, v in data.items() if isinstance(v, list) and len(v) > 0}
        return {}
    except Exception as e:
        print(f"[Hypergraph Extractor] 实时超边抽取失败: {e}", flush=True)
        return {}