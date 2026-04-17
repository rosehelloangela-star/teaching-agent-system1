import os
import json
import pypdf
from typing import Dict, List, Any
import time

from langchain_core.prompts import ChatPromptTemplate
from app.agents.mechanism.llm_config import get_llm
from app.core.json_utils import message_content_to_text, extract_first_json_value
from app.core.text_cleaner import clean_pdf_text
from app.kg.graph_store import kg_store


def _get_core_concepts() -> str:
    """动态从数据库拉取你预设的基础 Concept 理论节点，传给大模型"""
    try:
        if kg_store.driver:
            with kg_store.driver.session() as session:
                # 只拉取核心理论节点，避免把以前抽取的脏数据拉出来
                records = session.run("MATCH (n:Entity:Concept) RETURN n.name AS name")
                concepts = [r["name"] for r in records]
                if concepts:
                    return ", ".join(concepts)
    except Exception as e:
        print(f"[Extractor_Logger] 无法拉取动态概念: {e}")
        
    # 如果数据库还没连上，给一个默认的兜底核心盘
    return "总潜在市场(TAM), 可服务市场(SAM), 可获得市场(SOM), 用户画像(Persona), 核心痛点, 价值主张(Value Proposition), 最小可行性产品(MVP), 产品市场契合度(PMF), 核心壁垒(Moat), 商业模式(Business Model), 获客成本(CAC), 单均经济模型(Unit Economics), 核心团队(Core Team)"


def extract_kg_triplets(text: str) -> List[Dict[str, Any]]:
    """支持多类型实体与动态本体映射的高级知识抽取"""
    if not text or not text.strip(): 
        return []
        
    llm = get_llm(temperature=0.1, max_tokens=2000)
    base_concepts_str = _get_core_concepts()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        你是顶级的创新创业投资人与商业逻辑建模专家。请阅读商业计划书(BP)片段，提取核心的【商业逻辑图谱】。
        
        === 🚨 核心本体库与强制映射原则（至关重要） ===
        商业计划书中通常描述的是具体的行业项目（如“医疗AI报告”、“校园单车”）。
        你的核心任务是：提取这些【具体业务细节】，并将其【强制锚定】到系统现有的【核心理论概念】上。
        
        【系统现有的核心理论概念池 (Concept) 白名单】：
        {base_concepts_str}

        === 🧱 允许的节点类型 (Node Types) ===
        请将你提取的内容严格分类为以下 8 种类型：
        1. Concept (理论概念)：只能从上面的【白名单】中挑选，不得生编硬造！
        2. Customer (目标客群)：具体的受众，如“三甲医院影像科医生”。
        3. PainPoint (痛点)：客户面临的具体难题，如“医生阅片工作量大且易漏诊”。
        4. Solution (解决方案)：项目提供的产品服务，如“AI秒级生成辅助诊断报告”。
        5. BusinessModel (商业模式)：具体变现方式，如“按SaaS账号年费订阅”。
        6. Case (具体案例)：包含数据或事实的优秀做法，如“试运行3个月，漏诊率下降40%”。
        7. Mistake (常见错误/不足)：项目的短板或雷区，如“研发成本过高导致资金链断裂”。
        8. Task (验证任务)：下一步需要做的事或行动建议。

        === 🔗 允许的关系类型 (Relations) ===
        - MAPPED_TO (理论锚定)：将业务节点挂载到理论概念上。例：(三甲医院医生[Customer]) -[MAPPED_TO]-> (用户画像(Persona)[Concept])
        - SOLVES (解决)：(Solution) -[SOLVES]-> (PainPoint)
        - TARGETS (针对)：(Solution) -[TARGETS]-> (Customer)
        - ADOPTS (采用)：(Solution) -[ADOPTS]-> (BusinessModel)
        - HAS_CASE (案例支撑)：(Concept/Solution) -[HAS_CASE]-> (Case)
        - COMMON_MISTAKE (常见雷区)：(Concept) -[COMMON_MISTAKE]-> (Mistake)
        
        === ⚠️ 质量红线（不遵守将导致系统崩溃） ===
        1. PainPoint, Solution, Case 这类节点的 `head` 或 `tail` (即内容本身) 绝对不能是短词！必须是一句包含具体上下文的完整描述（15-30字左右）。
           ❌ 错误："效率低"
           ✅ 正确："三甲医院影像科医生每天面临超负荷阅片工作极易漏诊"
        2. 必须且只能输出一个合法的 JSON 对象，包含唯一键 "triplets"，其值为数组。
        
        【✅ 正确的输出示例】：
        {{
            "triplets": [
                {{"head": "三甲医院影像科医生", "head_type": "Customer", "relation": "MAPPED_TO", "tail": "用户画像(Persona)", "tail_type": "Concept"}},
                {{"head": "基层医院缺乏资深医生导致漏诊", "head_type": "PainPoint", "relation": "MAPPED_TO", "tail": "核心痛点", "tail_type": "Concept"}},
                {{"head": "自研AI秒级生成辅助诊断报告", "head_type": "Solution", "relation": "SOLVES", "tail": "基层医院缺乏资深医生导致漏诊", "tail_type": "PainPoint"}},
                {{"head": "自研AI秒级生成辅助诊断报告", "head_type": "Solution", "relation": "MAPPED_TO", "tail": "最小可行性产品(MVP)", "tail_type": "Concept"}},
                {{"head": "总潜在市场(TAM)", "head_type": "Concept", "relation": "HAS_CASE", "tail": "全国医学影像设备及软件服务市场达500亿", "tail_type": "Case"}}
            ]
        }}
        """),
        ("user", "提取以下文本中的商业知识网络：\n{text}")
    ])
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 注入 base_concepts_str
            response = (prompt | llm).invoke({"text": text, "base_concepts_str": base_concepts_str})
            parsed_data = extract_first_json_value(message_content_to_text(response))
            
            if isinstance(parsed_data, dict):
                return parsed_data.get("triplets", [])
            else:
                print(f"[Extractor_Logger] ⚠️ 模型输出了非字典格式，已按空处理。", flush=True)
                return []
                
        except Exception as e:
            # 如果是超时错误，或者还没到最后一次尝试，就等待后重试
            if attempt < max_retries - 1:
                print(f"[Extractor_Logger] ⏳ 第 {attempt + 1} 次请求失败 ({e})，休息 3 秒后重试...", flush=True)
                time.sleep(3)
                continue
            else:
                print(f"[Extractor_Logger] ❌ 连续 {max_retries} 次抽取失败: {e}", flush=True)
                return []


def process_kg_pipeline(folder_path: str, chunk_size: int = 1000):
    """遍历 PDF 执行知识抽取（含断点续传记录）"""
    print(f"\n[Extractor_Logger] 🚀 启动【知识图谱抽取流 (强 Prompt 版)】", flush=True)
    if not os.path.exists(folder_path):
        print(f"[Extractor_Logger] 文件夹 {folder_path} 不存在。", flush=True)
        return

    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"[Extractor_Logger] 没有找到 PDF 文件。", flush=True)
        return

    # 读取已处理记录
    record_file = os.path.join(os.path.dirname(folder_path), "processed_pdfs.json")
    processed_history = []
    if os.path.exists(record_file):
        try:
            with open(record_file, "r", encoding="utf-8") as rf:
                processed_history = json.load(rf)
        except:
            pass

    for filename in pdf_files:
        if filename in processed_history:
            print(f"[Extractor_Logger] ⏭️ [{filename}] 已处理过，自动跳过。", flush=True)
            continue

        filepath = os.path.join(folder_path, filename)
        raw_content = ""
        try:
            with open(filepath, "rb") as f:
                for page in pypdf.PdfReader(f).pages:
                    raw_content += (page.extract_text() or "") + "\n"

            cleaned_content = clean_pdf_text(raw_content)
            print(f"[Extractor_Logger] 📄 正在处理 [{filename}]...", flush=True)

            if cleaned_content.strip():
                for i in range(0, len(cleaned_content), chunk_size):
                    chunk = cleaned_content[i:i + chunk_size]
                    triplets = extract_kg_triplets(chunk)
                    time.sleep(1) # 防并发限流
                    
                    if triplets:
                        kg_store.add_knowledge_from_triplets(triplets)
                        print(f"[Extractor_Logger] ✅ 成功写入 {len(triplets)} 条图谱三元组。", flush=True)

            # 写入记录
            processed_history.append(filename)
            with open(record_file, "w", encoding="utf-8") as wf:
                json.dump(processed_history, wf, ensure_ascii=False, indent=4)
            print(f"[Extractor_Logger] 💾 [{filename}] 已存入已处理名册。", flush=True)

        except Exception as e:
            print(f"[Extractor_Logger] ❌ [{filename}] 处理错误: {e}", flush=True)


if __name__ == "__main__":
    target_folder = os.path.join(os.path.dirname(__file__), "..", "data", "pdfs")
    os.makedirs(target_folder, exist_ok=True)
    process_kg_pipeline(target_folder)