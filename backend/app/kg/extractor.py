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

def extract_kg_triplets(text: str) -> List[Dict[str, Any]]:
    """基于纯 Prompt 约束的知识抽取，拒绝代码兜底"""
    if not text or not text.strip(): 
        return []
        
    llm = get_llm(temperature=0.1, max_tokens=2000)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        你是顶级的创新创业投资人与商业逻辑建模专家。请阅读商业计划书(BP)片段，提取核心的【商业逻辑图谱】。
        
        === 本体库约束（必须严格遵守） ===
        【节点类型 (head_type / tail_type) 仅限 5 种】：
        Concept (概念), Mistake (常见错误), PositiveCase (成功案例), NegativeCase (失败案例), Task (验证任务)

        【边关系 (relation) 仅限 4 种】：
        PREREQ, COMMON_MISTAKE, HAS_POSITIVE_CASE, HAS_NEGATIVE_CASE
        
        === ⚠️ 致命的输出格式红线（系统级约束） ===
        你的输出将被直接送入代码解析，如果格式错误将导致系统崩溃！
        1. 你必须、且只能输出一个合法的 JSON **对象 (Object)**。
        2. 绝对不能在最外层输出 JSON 数组 (Array) 或列表 (List)。
        3. 该 JSON 对象必须包含且仅包含一个名为 "triplets" 的键，其值是一个数组。
        
        【✅ 正确的输出示例（请严格模仿）】：
        {{
            "triplets": [
                {{"head": "总潜在市场(TAM)", "head_type": "Concept", "relation": "HAS_NEGATIVE_CASE", "tail": "某校园外卖盲目夸大TAM", "tail_type": "NegativeCase"}},
                {{"head": "核心痛点", "head_type": "Concept", "relation": "COMMON_MISTAKE", "tail": "伪需求", "tail_type": "Mistake"}}
            ]
        }}
        
        【❌ 错误的输出示例（绝对禁止以下行为）】：
        [
            {{"head": "TAM", "relation": "PREREQ", "tail": "SAM"}}
        ]
        """),
        ("user", "提取以下文本中的商业知识网络：\n{text}")
    ])
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = (prompt | llm).invoke({"text": text})
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

# import os
# import json
# import argparse
# import PyPDF2
# from typing import Dict, List, Any
# import time

# from langchain_core.prompts import ChatPromptTemplate
# from app.agents.mechanism.llm_config import get_llm
# from app.core.json_utils import message_content_to_text, extract_first_json_value
# from app.core.text_cleaner import clean_pdf_text

# def extract_project_logic_network(text: str) -> Dict[str, Any]:
#     """
#     【专为前端可视化设计】
#     只提取学生项目文本中的商业要素，并用干净的 "LINK" 连线串联，不带任何学术关系词。
#     """
#     if not text or not text.strip(): 
#         return {"triplets": []}
        
#     llm = get_llm(temperature=0.1, max_tokens=2000)
    
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """
#         你是顶级的商业逻辑分析师。请仔细阅读学生提交的项目文本，提取出项目的【底层逻辑推演图】。
        
#         === 任务：提取商业逻辑网络 (Triplets) ===
#         请忽略任何学术教案用语，直接提取项目中实实在在的商业要素作为节点，并梳理它们之间的逻辑推导连线。
#         - 节点(head/tail)必须是极其具体的词：例如“大学生群体”、“拿快递难”、“防丢手环”、“99元买断”、“小红书投放”。
#         - 关系(relation)请固定填写 "LINK" 即可，不需要做复杂的分类。
        
#         请遵循商业常识的因果指向：
#         1. 目标客群 -> 核心痛点
#         2. 核心痛点 -> 解决方案(产品)
#         3. 解决方案 -> 盈利模式(收入)
#         4. 解决方案 -> 营销渠道
        
#         【输出格式要求（⚠️致命红线：严格的 JSON 格式）】
#         1. 只能输出一个合法的 JSON 对象，不要附加任何 Markdown 标记。
#         2. 字符串内双引号必须转义（\\"），禁止出现物理换行符（用 \\n 代替）。
        
#         示例：
#         {{
#             "triplets": [
#                 {{"head": "独居青年", "relation": "LINK", "tail": "陪伴需求"}},
#                 {{"head": "陪伴需求", "relation": "LINK", "tail": "AI虚拟宠物"}},
#                 {{"head": "AI虚拟宠物", "relation": "LINK", "tail": "按月订阅收费"}},
#                 {{"head": "AI虚拟宠物", "relation": "LINK", "tail": "B站UP主推广"}}
#             ]
#         }}
#         """),
#         ("user", "提取以下项目文本中的商业逻辑网络：\n{text}")
#     ])
    
#     try:
#         response = (prompt | llm).invoke({"text": text})
#         parsed_data = extract_first_json_value(message_content_to_text(response))
        
#         if isinstance(parsed_data, dict):
#             return {
#                 "triplets": parsed_data.get("triplets", [])
#             }
#         return {"triplets": []}
        
#     except Exception as e:
#         print(f"[Extractor - Logic Network] 逻辑网络抽取失败: {e}", flush=True)
#         return {"triplets": []}

# # 引入 Neo4j 存储实例
# from app.kg.graph_store import kg_store

# def extract_comprehensive_knowledge(text: str) -> Dict[str, Any]:
#     """
#     让大模型一次性同时提取【KG三元组】与【超图多节点簇】。
#     """
#     if not text or not text.strip(): 
#         return {"triplets": [], "hyperedges": {}}
        
#     llm = get_llm(temperature=0.1, max_tokens=3000)
    
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """
#         你是顶级的双创商业逻辑建模专家。请阅读文本，并同时提取【知识图谱三元组】与【多元超边关系】。
        
#         === 任务一：提取知识图谱三元组 (Triplets) ===
#         - 节点类型必须是：Concept, Method, Task, Artifact, Metric, RubricItem, Mistake
#         - 边关系必须是：PREREQ, CONTAIN, MEASURED_BY, GENERATE, EVALUATED_BY, COMMON_MISTAKE, FIX_STRATEGY
        
#         === 任务二：提取多元超边关系 (Hyperedges) ===
#         请严格且仅使用以下 20 个英文 Key 作为超边名称：
#         Core_Business_Loop, Customer_Value_Misalignment, Channel_Physical_Access, Willingness_To_Pay, 
#         Market_Reachability, Frequency_Mismatch, Unit_Economics, Pricing_Space, Cash_Flow_Health, 
#         Financial_Reasonableness, Supply_Chain_Sync, Cold_Start_Engine, R&D_Team_Match, Resource_Feasibility, 
#         Tech_Barrier, Real_Competition, Narrative_Causality, Innovation_Verification, Compliance_Ethics, 
#         Social_Value_Translation。
        
#         【输出格式要求】
#         只输出一个合法 JSON，必须包含 "triplets" 和 "hyperedges" 两个键：
#         {{
#             "triplets": [
#                 {{"head": "用户画像", "head_type": "Concept", "relation": "PREREQ", "tail": "核心痛点", "tail_type": "Concept"}}
#             ],
#             "hyperedges": {{
#                 "Core_Business_Loop": ["下沉市场老年群体", "防丢手环", "按次付费"],
#                 "Tech_Barrier": ["低功耗算法", "实用新型专利"]
#             }}
#         }}
#         """),
#         ("user", "提取以下文本中的知识网络：\n{text}")
#     ])
    
#     try:
#         response = (prompt | llm).invoke({"text": text})
#         parsed_data = extract_first_json_value(message_content_to_text(response))
        
#         if isinstance(parsed_data, dict):
#             # 过滤清洗数据
#             triplets = parsed_data.get("triplets", [])
#             hyperedges = {k: v for k, v in parsed_data.get("hyperedges", {}).items() if isinstance(v, list) and len(v) > 0}
#             return {"triplets": triplets, "hyperedges": hyperedges}
#         return {"triplets": [], "hyperedges": {}}
        
#     except Exception as e:
#         print(f"[Extractor] 综合抽取失败: {e}", flush=True)
#         return {"triplets": [], "hyperedges": {}}

# def process_unified_pipeline(folder_path: str, output_hypergraph_json: str, chunk_size: int = 3000):
#     """
#     遍历 PDF 文件夹，执行双轨抽取，并且做到 Chunk（块）级别的实时落盘保护。
#     """
#     print(f"\n🚀 启动【双轨知识抽取流(KG + Hypergraph)】")
#     if not os.path.exists(folder_path):
#         print(f"文件夹 {folder_path} 不存在，请放入 PDF。")
#         return

#     pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
#     if not pdf_files:
#         print(f"{folder_path} 中没有找到 PDF 文件。")
#         return

#     # 读取已有的超图 JSON 库（实现增量跳过）
#     existing_hyper_data = {}
#     if os.path.exists(output_hypergraph_json):
#         try:
#             with open(output_hypergraph_json, 'r', encoding='utf-8') as f:
#                 existing_hyper_data = json.load(f)
#             print(f"📄 发现已有超图知识库，包含 {len(existing_hyper_data)} 个项目。")
#         except Exception as e:
#             print(f"读取已有 JSON 失败，将重新建立。错误: {e}")

#     for filename in pdf_files:
#         # 【文件级跳过】如果 JSON 里已经有了完整记录，跳过该文件
#         if filename in existing_hyper_data:
#             print(f"⏭️  [{filename}] 已存在于知识库中，跳过。")
#             continue

#         filepath = os.path.join(folder_path, filename)
#         raw_content = ""
#         try:
#             with open(filepath, "rb") as f:
#                 for page in PyPDF2.PdfReader(f).pages:
#                     raw_content += (page.extract_text() or "") + "\n"

#             cleaned_content = clean_pdf_text(raw_content)
#             print(f"\n📄 开始处理 [{filename}]，总长度: {len(cleaned_content)} 字符。")

#             project_hyperedges = {}
#             if cleaned_content.strip():
#                 total_chunks = (len(cleaned_content) + chunk_size - 1) // chunk_size
                
#                 # 开始分块处理
#                 for idx, i in enumerate(range(0, len(cleaned_content), chunk_size)):
#                     chunk = cleaned_content[i:i + chunk_size]
                    
#                     print(f"  -> ⏳ 正在请求大模型抽取第 {idx + 1}/{total_chunks} 块...", flush=True)
                    
#                     extracted_data = extract_comprehensive_knowledge(chunk)
#                     time.sleep(2) # 缓冲防断流
                    
#                     triplets = extracted_data["triplets"]
#                     hyperedges = extracted_data["hyperedges"]
                    
#                     # ==========================================
#                     # 【Chunk级实时落盘 1】：Neo4j 图谱数据
#                     # ==========================================
#                     if triplets:
#                         kg_store.add_knowledge_from_triplets(triplets)
#                         print(f"     ✅ [Neo4j] 已写入 {len(triplets)} 条二元关系。")
                    
#                     # ==========================================
#                     # 【Chunk级实时落盘 2】：JSON 超图数据
#                     # ==========================================
#                     if hyperedges:
#                         # 融合同一项目在不同 Chunk 中发现的超边
#                         for edge_key, nodes in hyperedges.items():
#                             if edge_key not in project_hyperedges:
#                                 project_hyperedges[edge_key] = set()
#                             project_hyperedges[edge_key].update(nodes)
                        
#                         # 实时更新全局的 JSON 数据字典
#                         existing_hyper_data[filename] = {k: list(v) for k, v in project_hyperedges.items()}
                        
#                         # 实时写入本地磁盘，断电都不怕！
#                         os.makedirs(os.path.dirname(output_hypergraph_json), exist_ok=True)
#                         with open(output_hypergraph_json, 'w', encoding='utf-8') as f:
#                             json.dump(existing_hyper_data, f, ensure_ascii=False, indent=4)
                            
#                         print(f"     ✅ [HyperNetX] 发现 {len(hyperedges)} 类超边，进度已实时保存至 JSON。")

#             print(f"🎉 [{filename}] 全部分块处理完毕！\n")

#         except Exception as e:
#             print(f"❌ [{filename}] 处理时发生严重错误... {e}")

# if __name__ == "__main__":
#     target_folder = os.path.join(os.path.dirname(__file__), "..", "data", "pdfs")
#     output_db = os.path.join(os.path.dirname(__file__), "..", "data", "winning_hypergraphs_db.json")
    
#     os.makedirs(target_folder, exist_ok=True)
    
#     process_unified_pipeline(target_folder, output_db)