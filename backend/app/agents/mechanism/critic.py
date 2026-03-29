# import time
# from langchain_core.prompts import ChatPromptTemplate
# from app.agents.mechanism.llm_config import get_llm
# from app.core.json_utils import message_content_to_text
# from app.agents.roles import ROLE_CONFIG_REGISTRY
# from app.core.stream_logger import log_and_emit

# from app.kg.entity_matcher import detect_concepts
# from app.kg.graph_store import kg_store

# from app.hypergraph.hyper_engine import HypergraphEngine
# from app.hypergraph.extractor import extract_hyperedges_from_text
# from app.hypergraph.entity_matcher import detect_hyper_nodes


# def critic_node(state: dict) -> dict:
#     user_input = (state.get("user_input") or "").strip()

#     role_id = state.get("selected_role", "student_tutor")
#     role_config = ROLE_CONFIG_REGISTRY.get(role_id, {})

#     role_goal = role_config.get("goal", "提供教学分析")
#     focus = role_config.get("focus", "结构化诊断")
#     current_mode = state.get("current_mode", "learning")

#     messages = state.get("messages", [])
#     chat_history = "无历史对话（首次提交）。"
#     if len(messages) > 1:
#         history_lines = []
#         for m in messages[:-1]:
#             role = "【学生】" if m.type == "human" else "【导师】"
#             content = m.content[:500] + "..." if len(m.content) > 500 else m.content
#             history_lines.append(f"{role}:\n{content}")
#         chat_history = "\n".join(history_lines)

#     if not user_input:
#         log_and_emit(state, "critic", "用户输入为空，返回兜底诊断。", level="warning")
#         return {
#             "critic_diagnosis": {
#                 "raw_analysis": "主要问题：用户输入为空\n证据缺口：无可分析文本\n最大风险：无法判断\n推进阻碍：请先提交内容",
#             },
#             "llm_unavailable": False,
#         }

#     engine_context = ""

#     if current_mode == "learning" and user_input:
#         log_and_emit(state, "critic", f"进入知识图谱诊断分支。current_mode={current_mode}")
#         try:
#             all_db_nodes = kg_store.get_all_entity_names()
#             detected_concepts = detect_concepts(user_input, all_db_nodes, fuzzy_threshold=72, debug=True)
#             missing_prereqs = kg_store.diagnose_missing_prereqs(detected_concepts)

#             if missing_prereqs or detected_concepts:
#                 engine_context = "【Neo4j 图谱前置诊断客观信息】（请在评估时严格参考）：\n"
#                 if detected_concepts:
#                     engine_context += f"- 识别到项目已包含实体概念：{', '.join(detected_concepts)}\n"
#                     log_and_emit(state, "critic", f"知识图谱命中实体：{', '.join(detected_concepts)}")
#                 if missing_prereqs:
#                     engine_context += f"- ⚠️ 逻辑断层预警，缺失前置核心概念(PREREQ)：{', '.join(missing_prereqs)}\n"
#                     log_and_emit(state, "critic", f"检测到缺失前置概念：{', '.join(missing_prereqs)}", level="warning")

#                 for concept in detected_concepts:
#                     mistakes = kg_store.get_common_mistakes(concept)
#                     if mistakes:
#                         engine_context += f"- ⚠️ 针对'{concept}'，历史挑战杯高发错误模式：{', '.join(mistakes)}\n"
#                 log_and_emit(state, "critic", "知识图谱上下文组装完成。")
#             else:
#                 log_and_emit(state, "critic", "未命中任何图谱实体，本轮不注入图谱上下文。")
#         except Exception as e:
#             log_and_emit(state, "critic", f"访问 Neo4j 图谱失败，已降级处理：{e}", level="warning")

#     elif current_mode == "project" and user_input:
#         log_and_emit(state, "critic", f"进入超图诊断分支。current_mode={current_mode}")
#         try:
#             extracted_h_edges = extract_hyperedges_from_text(user_input)
#             fuzzy_hg_nodes = detect_hyper_nodes(user_input, fuzzy_threshold=72, debug=True)

#             if fuzzy_hg_nodes and extracted_h_edges:
#                 log_and_emit(state, "critic", f"模糊识别到标准超图节点：{', '.join(fuzzy_hg_nodes)}")
#                 for edge_key in extracted_h_edges:
#                     extracted_h_edges[edge_key].extend(fuzzy_hg_nodes)

#             # --- 修改核心逻辑区 ---
#             if extracted_h_edges:
#                 hg_engine = HypergraphEngine()
#                 hg_engine.build_hypergraph(extracted_h_edges)
#                 alerts = hg_engine.run_topology_diagnostics()

#                 if alerts or fuzzy_hg_nodes:
#                     engine_context = "【基于 HyperNetX 的超图逻辑拓扑审查报告】（最高优先级，请严厉指出逻辑断层）：\n"
#                     if fuzzy_hg_nodes:
#                         engine_context += f"- 🔍 模糊识别到的底层标准要素：{', '.join(fuzzy_hg_nodes)}\n"
#                     for alert in alerts:
#                         engine_context += f"- ⚠️ [{alert['rule']} {alert['name']}] (严重度:{alert.get('severity', 'high')})：{alert['issue']}\n"
#                     log_and_emit(state, "critic", f"成功触发 {len(alerts)} 条超图预警。", level="warning" if alerts else "info")
#                 else:
#                     log_and_emit(state, "critic", "超图引擎完成分析，但未触发预警。")
            
#             elif fuzzy_hg_nodes:
#                 # 新增逻辑：提取到了节点，但没有边（闭环断裂）
#                 engine_context = f"【超图拓扑诊断】⚠️ 识别到了离散的商业要素（{', '.join(fuzzy_hg_nodes)}），但未能提取出任何有效的商业闭环逻辑（超图边）。项目当前要素割裂，未能形成系统级关联。\n"
#                 log_and_emit(state, "critic", "有要素无闭环，判定为要素割裂。", level="warning")
            
#             else:
#                 # 既没有节点也没有边（彻底空壳）
#                 engine_context = "【超图拓扑诊断】⚠️ 未能从当前文本中提取出任何有效商业闭环元素及节点，项目处于空壳状态。\n"
#                 log_and_emit(state, "critic", "未提取到任何要素和闭环，判定为项目彻底空壳。", level="warning")
#             # --- 修改核心逻辑区结束 ---

#         except Exception as e:
#             log_and_emit(state, "critic", f"超图引擎分析失败，已降级处理：{e}", level="warning")

#     else:
#         log_and_emit(state, "critic", f"当前模式未命中特定图谱分支。current_mode={current_mode}")

#     llm = get_llm(temperature=0.1, max_tokens=300)
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 (
#                     "你是极为严苛的创新创业教学诊断专家。\n"
#                     f"当前角色目标：{role_goal}\n"
#                     f"当前诊断重点：{focus}\n"
#                     "请结合【历史对话】、【系统客观诊断报告】和学生的【本次输入】进行严苛的结构化诊断。\n"
#                     "如果底层的图谱/超图引擎提示了逻辑断层、缺失要素或历史高发错误，你必须优先将其作为最大风险或主要问题指出，绝不能顺从学生的错误思路！\n"
#                     "如果学生是在修复之前的问题，请检查是否修复到位；如果是新项目，请全面诊断。\n"
#                     "请只输出 4 行，且严格使用以下格式：\n"
#                     "主要问题：...\n"
#                     "证据缺口：...\n"
#                     "最大风险：...\n"
#                     "推进阻碍：...\n"
#                     "要求：\n"
#                     "1. 只输出这 4 行，不要标题，不要解释，不要 markdown\n"
#                     "2. 每行尽量简洁，直击要害\n"
#                     "3. 必须使用中文"
#                 ),
#             ),
#             ("user", "【历史对话记录】：\n{chat_history}\n\n{engine_context}\n\n【本次输入】：\n{user_input}"),
#         ]
#     )

#     chain = prompt | llm
#     log_and_emit(state, "critic", f"正在结合 {current_mode} 模式上下文调用诊断模型...")
#     start = time.perf_counter()
#     try:
#         response = chain.invoke(
#             {
#                 "chat_history": chat_history,
#                 "engine_context": engine_context,
#                 "user_input": user_input,
#             }
#         )
#         text = message_content_to_text(response)
#         elapsed = time.perf_counter() - start

#         if not text.strip():
#             raise ValueError("模型返回为空")

#         log_and_emit(state, "critic", f"诊断模型返回成功，用时 {elapsed:.2f}s。")
#         return {
#             "critic_diagnosis": {"raw_analysis": text.strip()},
#             "llm_unavailable": False,
#         }
#     except Exception as e:
#         elapsed = time.perf_counter() - start
#         log_and_emit(state, "critic", f"诊断模型调用失败，用时 {elapsed:.2f}s。错误：{e}", level="error")
#         fallback_text = "主要问题：远程模型调用失败\n证据缺口：系统暂无响应\n最大风险：诊断服务暂时不可用\n推进阻碍：请检查网络或稍后重试"
#         return {
#             "critic_diagnosis": {"raw_analysis": fallback_text},
#             "llm_unavailable": True,
#         }


# # import time
# # from langchain_core.prompts import ChatPromptTemplate
# # from app.agents.mechanism.llm_config import get_llm
# # from app.core.json_utils import message_content_to_text
# # from app.agents.roles import ROLE_CONFIG_REGISTRY
# # from app.core.stream_logger import log_and_emit

# # from app.kg.entity_matcher import detect_concepts
# # from app.kg.graph_store import kg_store

# # from app.hypergraph.hyper_engine import HypergraphEngine
# # from app.hypergraph.extractor import extract_hyperedges_from_text
# # from app.hypergraph.entity_matcher import detect_hyper_nodes


# # def critic_node(state: dict) -> dict:
# #     user_input = (state.get("user_input") or "").strip()

# #     role_id = state.get("selected_role", "student_tutor")
# #     role_config = ROLE_CONFIG_REGISTRY.get(role_id, {})

# #     role_goal = role_config.get("goal", "提供教学分析")
# #     focus = role_config.get("focus", "结构化诊断")
# #     current_mode = state.get("current_mode", "learning")

# #     messages = state.get("messages", [])
# #     chat_history = "无历史对话（首次提交）。"
# #     if len(messages) > 1:
# #         history_lines = []
# #         for m in messages[:-1]:
# #             role = "【学生】" if m.type == "human" else "【导师】"
# #             content = m.content[:500] + "..." if len(m.content) > 500 else m.content
# #             history_lines.append(f"{role}:\n{content}")
# #         chat_history = "\n".join(history_lines)

# #     if not user_input:
# #         log_and_emit(state, "critic", "用户输入为空，返回兜底诊断。", level="warning")
# #         return {
# #             "critic_diagnosis": {
# #                 "raw_analysis": "主要问题：用户输入为空\n证据缺口：无可分析文本\n最大风险：无法判断\n推进阻碍：请先提交内容",
# #             },
# #             "llm_unavailable": False,
# #         }

# #     engine_context = ""

# #     if current_mode == "learning" and user_input:
# #         log_and_emit(state, "critic", f"进入知识图谱诊断分支。current_mode={current_mode}")
# #         try:
# #             all_db_nodes = kg_store.get_all_entity_names()
# #             detected_concepts = detect_concepts(user_input, all_db_nodes, fuzzy_threshold=72, debug=True)
# #             missing_prereqs = kg_store.diagnose_missing_prereqs(detected_concepts)

# #             if missing_prereqs or detected_concepts:
# #                 engine_context = "【Neo4j 图谱前置诊断客观信息】（请在评估时严格参考）：\n"
# #                 if detected_concepts:
# #                     engine_context += f"- 识别到项目已包含实体概念：{', '.join(detected_concepts)}\n"
# #                     log_and_emit(state, "critic", f"知识图谱命中实体：{', '.join(detected_concepts)}")
# #                 if missing_prereqs:
# #                     engine_context += f"- ⚠️ 逻辑断层预警，缺失前置核心概念(PREREQ)：{', '.join(missing_prereqs)}\n"
# #                     log_and_emit(state, "critic", f"检测到缺失前置概念：{', '.join(missing_prereqs)}", level="warning")

# #                 for concept in detected_concepts:
# #                     mistakes = kg_store.get_common_mistakes(concept)
# #                     if mistakes:
# #                         engine_context += f"- ⚠️ 针对'{concept}'，历史挑战杯高发错误模式：{', '.join(mistakes)}\n"
# #                 log_and_emit(state, "critic", "知识图谱上下文组装完成。")
# #             else:
# #                 log_and_emit(state, "critic", "未命中任何图谱实体，本轮不注入图谱上下文。")
# #         except Exception as e:
# #             log_and_emit(state, "critic", f"访问 Neo4j 图谱失败，已降级处理：{e}", level="warning")

# #     elif current_mode == "project" and user_input:
# #         log_and_emit(state, "critic", f"进入超图诊断分支。current_mode={current_mode}")
# #         try:
# #             extracted_h_edges = extract_hyperedges_from_text(user_input)
# #             fuzzy_hg_nodes = detect_hyper_nodes(user_input, fuzzy_threshold=72, debug=True)

# #             if fuzzy_hg_nodes and extracted_h_edges:
# #                 log_and_emit(state, "critic", f"模糊识别到标准超图节点：{', '.join(fuzzy_hg_nodes)}")
# #                 for edge_key in extracted_h_edges:
# #                     extracted_h_edges[edge_key].extend(fuzzy_hg_nodes)

# #             if extracted_h_edges:
# #                 hg_engine = HypergraphEngine()
# #                 hg_engine.build_hypergraph(extracted_h_edges)
# #                 alerts = hg_engine.run_topology_diagnostics()

# #                 if alerts or fuzzy_hg_nodes:
# #                     engine_context = "【基于 HyperNetX 的超图逻辑拓扑审查报告】（最高优先级，请严厉指出逻辑断层）：\n"
# #                     if fuzzy_hg_nodes:
# #                         engine_context += f"- 🔍 模糊识别到的底层标准要素：{', '.join(fuzzy_hg_nodes)}\n"
# #                     for alert in alerts:
# #                         engine_context += f"- ⚠️ [{alert['rule']} {alert['name']}] (严重度:{alert.get('severity', 'high')})：{alert['issue']}\n"
# #                     log_and_emit(state, "critic", f"成功触发 {len(alerts)} 条超图预警。", level="warning" if alerts else "info")
# #                 else:
# #                     log_and_emit(state, "critic", "超图引擎完成分析，但未触发预警。")
# #             else:
# #                 engine_context = "【超图拓扑诊断】⚠️ 未能从当前文本中提取出任何有效商业闭环元素，项目处于空壳状态。\n"
# #                 log_and_emit(state, "critic", "未提取到有效商业闭环元素，判定为项目空壳。", level="warning")
# #         except Exception as e:
# #             log_and_emit(state, "critic", f"超图引擎分析失败，已降级处理：{e}", level="warning")

# #     else:
# #         log_and_emit(state, "critic", f"当前模式未命中特定图谱分支。current_mode={current_mode}")

# #     llm = get_llm(temperature=0.1, max_tokens=300)
# #     prompt = ChatPromptTemplate.from_messages(
# #         [
# #             (
# #                 "system",
# #                 (
# #                     "你是极为严苛的创新创业教学诊断专家。\n"
# #                     f"当前角色目标：{role_goal}\n"
# #                     f"当前诊断重点：{focus}\n"
# #                     "请结合【历史对话】、【系统客观诊断报告】和学生的【本次输入】进行严苛的结构化诊断。\n"
# #                     "如果底层的图谱/超图引擎提示了逻辑断层、缺失要素或历史高发错误，你必须优先将其作为最大风险或主要问题指出，绝不能顺从学生的错误思路！\n"
# #                     "如果学生是在修复之前的问题，请检查是否修复到位；如果是新项目，请全面诊断。\n"
# #                     "请只输出 4 行，且严格使用以下格式：\n"
# #                     "主要问题：...\n"
# #                     "证据缺口：...\n"
# #                     "最大风险：...\n"
# #                     "推进阻碍：...\n"
# #                     "要求：\n"
# #                     "1. 只输出这 4 行，不要标题，不要解释，不要 markdown\n"
# #                     "2. 每行尽量简洁，直击要害\n"
# #                     "3. 必须使用中文"
# #                 ),
# #             ),
# #             ("user", "【历史对话记录】：\n{chat_history}\n\n{engine_context}\n\n【本次输入】：\n{user_input}"),
# #         ]
# #     )

# #     chain = prompt | llm
# #     log_and_emit(state, "critic", f"正在结合 {current_mode} 模式上下文调用诊断模型...")
# #     start = time.perf_counter()
# #     try:
# #         response = chain.invoke(
# #             {
# #                 "chat_history": chat_history,
# #                 "engine_context": engine_context,
# #                 "user_input": user_input,
# #             }
# #         )
# #         text = message_content_to_text(response)
# #         elapsed = time.perf_counter() - start

# #         if not text.strip():
# #             raise ValueError("模型返回为空")

# #         log_and_emit(state, "critic", f"诊断模型返回成功，用时 {elapsed:.2f}s。")
# #         return {
# #             "critic_diagnosis": {"raw_analysis": text.strip()},
# #             "llm_unavailable": False,
# #         }
# #     except Exception as e:
# #         elapsed = time.perf_counter() - start
# #         log_and_emit(state, "critic", f"诊断模型调用失败，用时 {elapsed:.2f}s。错误：{e}", level="error")
# #         fallback_text = "主要问题：远程模型调用失败\n证据缺口：系统暂无响应\n最大风险：诊断服务暂时不可用\n推进阻碍：请检查网络或稍后重试"
# #         return {
# #             "critic_diagnosis": {"raw_analysis": fallback_text},
# #             "llm_unavailable": True,
# #         }


import time

from langchain_core.prompts import ChatPromptTemplate

from app.agents.mechanism.llm_config import get_llm
from app.agents.roles import ROLE_CONFIG_REGISTRY
from app.core.json_utils import message_content_to_text
from app.core.stream_logger import log_and_emit
from app.hypergraph.entity_matcher import detect_hyper_nodes
from app.hypergraph.extractor import extract_hyperedges_from_text
from app.hypergraph.hyper_engine import HypergraphEngine
from app.kg.entity_matcher import detect_concepts
from app.kg.graph_store import kg_store


def _truncate_text(text: str, max_chars: int = 8000) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...(文档内容已截断)"


def critic_node(state: dict) -> dict:
    user_input = (state.get("user_input") or "").strip()

    role_id = state.get("selected_role", "student_tutor")
    role_config = ROLE_CONFIG_REGISTRY.get(role_id, {})

    role_goal = role_config.get("goal", "提供教学分析")
    focus = role_config.get("focus", "结构化诊断")
    current_mode = state.get("current_mode", "learning")

    bound_document_text = (state.get("bound_document_text") or "").strip()
    bound_file_name = (state.get("bound_file_name") or "").strip()
    document_status = (state.get("document_status") or "none").strip().lower()

    has_bound_doc = document_status == "bound" and bool(bound_document_text)

    messages = state.get("messages", [])
    chat_history = "无历史对话（首次提交）。"
    if len(messages) > 1:
        history_lines = []
        for m in messages[:-1]:
            role = "【学生】" if m.type == "human" else "【导师】"
            content = m.content[:500] + "..." if len(m.content) > 500 else m.content
            history_lines.append(f"{role}:\n{content}")
        chat_history = "\n".join(history_lines)

    if not user_input:
        log_and_emit(state, "critic", "用户输入为空，返回兜底诊断。", level="warning")
        return {
            "critic_diagnosis": {
                "raw_analysis": "主要问题：用户输入为空\n证据缺口：无可分析文本\n最大风险：无法判断\n推进阻碍：请先提交内容",
            },
            "llm_unavailable": False,
        }

    document_context = ""
    analysis_source_text = user_input

    if has_bound_doc:
        doc_excerpt = _truncate_text(bound_document_text, max_chars=8000)
        document_context = (
            "【当前会话已绑定商业计划书】（请优先把它视为事实依据）：\n"
            f"- 文件名：{bound_file_name or '未命名文件'}\n"
            f"- 文档内容节选：\n{doc_excerpt}\n"
        )
        log_and_emit(state, "critic", f"检测到会话已绑定文档：{bound_file_name or '未命名文件'}")

        if current_mode in {"project", "competition"}:
            analysis_source_text = (
                f"{_truncate_text(bound_document_text, max_chars=12000)}\n\n"
                f"【学生本轮补充说明】\n{user_input}"
            ).strip()

    engine_context = ""

    if current_mode == "learning":
        log_and_emit(state, "critic", f"进入知识图谱诊断分支。current_mode={current_mode}")
        try:
            all_db_nodes = kg_store.get_all_entity_names()
            detected_concepts = detect_concepts(user_input, all_db_nodes, fuzzy_threshold=72, debug=True)
            missing_prereqs = kg_store.diagnose_missing_prereqs(detected_concepts)

            if missing_prereqs or detected_concepts:
                engine_context = "【Neo4j 图谱前置诊断客观信息】（请在评估时严格参考）：\n"
                if detected_concepts:
                    engine_context += f"- 识别到项目已包含实体概念：{', '.join(detected_concepts)}\n"
                    log_and_emit(state, "critic", f"知识图谱命中实体：{', '.join(detected_concepts)}")
                if missing_prereqs:
                    engine_context += f"- ⚠️ 逻辑断层预警，缺失前置核心概念(PREREQ)：{', '.join(missing_prereqs)}\n"
                    log_and_emit(state, "critic", f"检测到缺失前置概念：{', '.join(missing_prereqs)}", level="warning")

                for concept in detected_concepts:
                    mistakes = kg_store.get_common_mistakes(concept)
                    if mistakes:
                        engine_context += f"- ⚠️ 针对'{concept}'，历史挑战杯高发错误模式：{', '.join(mistakes)}\n"

                log_and_emit(state, "critic", "知识图谱上下文组装完成。")
            else:
                log_and_emit(state, "critic", "未命中任何图谱实体，本轮不注入图谱上下文。")

        except Exception as e:
            log_and_emit(state, "critic", f"访问 Neo4j 图谱失败，已降级处理：{e}", level="warning")

    elif current_mode == "project":
        log_and_emit(state, "critic", f"进入超图诊断分支。current_mode={current_mode}")
        try:
            extracted_h_edges = extract_hyperedges_from_text(analysis_source_text)
            fuzzy_hg_nodes = detect_hyper_nodes(analysis_source_text, fuzzy_threshold=72, debug=True)

            if fuzzy_hg_nodes and extracted_h_edges:
                log_and_emit(state, "critic", f"模糊识别到标准超图节点：{', '.join(fuzzy_hg_nodes)}")
                for edge_key in extracted_h_edges:
                    extracted_h_edges[edge_key].extend(fuzzy_hg_nodes)

            if extracted_h_edges:
                hg_engine = HypergraphEngine()
                hg_engine.build_hypergraph(extracted_h_edges)
                alerts = hg_engine.run_topology_diagnostics()

                if alerts or fuzzy_hg_nodes:
                    engine_context = "【基于 HyperNetX 的超图逻辑拓扑审查报告】（最高优先级，请严厉指出逻辑断层）：\n"
                    if fuzzy_hg_nodes:
                        engine_context += f"- 🔍 模糊识别到的底层标准要素：{', '.join(fuzzy_hg_nodes)}\n"
                    for alert in alerts:
                        engine_context += f"- ⚠️ [{alert['rule']} {alert['name']}] (严重度:{alert.get('severity', 'high')})：{alert['issue']}\n"
                    log_and_emit(state, "critic", f"成功触发 {len(alerts)} 条超图预警。", level="warning" if alerts else "info")
                else:
                    log_and_emit(state, "critic", "超图引擎完成分析，但未触发预警。")

            elif fuzzy_hg_nodes:
                engine_context = (
                    f"【超图拓扑诊断】⚠️ 识别到了离散的商业要素（{', '.join(fuzzy_hg_nodes)}），"
                    "但未能提取出任何有效的商业闭环逻辑（超图边）。项目当前要素割裂，未能形成系统级关联。\n"
                )
                log_and_emit(state, "critic", "有要素无闭环，判定为要素割裂。", level="warning")

            else:
                engine_context = "【超图拓扑诊断】⚠️ 未能从当前文本中提取出任何有效商业闭环元素及节点，项目处于空壳状态。\n"
                log_and_emit(state, "critic", "未提取到任何要素和闭环，判定为项目彻底空壳。", level="warning")

        except Exception as e:
            log_and_emit(state, "critic", f"超图引擎分析失败，已降级处理：{e}", level="warning")

    elif current_mode == "competition":
        log_and_emit(state, "critic", f"进入竞赛诊断分支。current_mode={current_mode}")
        if has_bound_doc:
            engine_context = (
                "【竞赛评审上下文】当前分析对象为已绑定 BP 文档。"
                "请优先依据该文档内容完成 Rubric 对标、扣分证据识别与提分任务规划。\n"
            )
        else:
            engine_context = "【竞赛评审上下文】当前未绑定 BP 文档，请谨慎评估。\n"

    else:
        log_and_emit(state, "critic", f"当前模式未命中特定图谱分支。current_mode={current_mode}")

    llm = get_llm(temperature=0.1, max_tokens=320)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "你是极为严苛的创新创业教学诊断专家。\n"
                    f"当前角色目标：{role_goal}\n"
                    f"当前诊断重点：{focus}\n"
                    "请结合【历史对话】、【绑定文档信息】、【系统客观诊断报告】和学生的【本次输入】进行严苛的结构化诊断。\n"
                    "如果底层的图谱/超图引擎提示了逻辑断层、缺失要素或历史高发错误，你必须优先将其作为最大风险或主要问题指出，绝不能顺从学生的错误思路！\n"
                    "如果学生是在修复之前的问题，请检查是否修复到位；如果是新项目，请全面诊断。\n"
                    "请只输出 4 行，且严格使用以下格式：\n"
                    "主要问题：...\n"
                    "证据缺口：...\n"
                    "最大风险：...\n"
                    "推进阻碍：...\n"
                    "要求：\n"
                    "1. 只输出这 4 行，不要标题，不要解释，不要 markdown\n"
                    "2. 每行尽量简洁，直击要害\n"
                    "3. 必须使用中文"
                ),
            ),
            (
                "user",
                "【历史对话记录】：\n{chat_history}\n\n{document_context}\n{engine_context}\n\n【本次输入】：\n{user_input}",
            ),
        ]
    )

    chain = prompt | llm
    log_and_emit(state, "critic", f"正在结合 {current_mode} 模式上下文调用诊断模型...")

    start = time.perf_counter()
    try:
        response = chain.invoke(
            {
                "chat_history": chat_history,
                "document_context": document_context,
                "engine_context": engine_context,
                "user_input": analysis_source_text,
            }
        )
        text = message_content_to_text(response)
        elapsed = time.perf_counter() - start

        if not text.strip():
            raise ValueError("模型返回为空")

        log_and_emit(state, "critic", f"诊断模型返回成功，用时 {elapsed:.2f}s。")
        return {
            "critic_diagnosis": {"raw_analysis": text.strip()},
            "llm_unavailable": False,
        }

    except Exception as e:
        elapsed = time.perf_counter() - start
        log_and_emit(state, "critic", f"诊断模型调用失败，用时 {elapsed:.2f}s。错误：{e}", level="error")
        fallback_text = "主要问题：远程模型调用失败\n证据缺口：系统暂无响应\n最大风险：诊断服务暂时不可用\n推进阻碍：请检查网络或稍后重试"
        return {
            "critic_diagnosis": {"raw_analysis": fallback_text},
            "llm_unavailable": True,
        }