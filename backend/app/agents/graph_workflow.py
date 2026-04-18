# from typing import Any, Dict, List, TypedDict, Annotated

# from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.graph import END, StateGraph
# from langgraph.graph.message import add_messages

# from app.agents.mechanism.critic import critic_node
# from app.agents.mechanism.generator import generator_node
# from app.agents.mechanism.planner import planner_node
# from app.agents.mechanism.router import router_node
# from app.agents.mechanism.validator import validator_node
# from app.core.config import get_settings
# from app.core.stream_logger import log_and_emit


# class AgentState(TypedDict, total=False):
#     messages: Annotated[list[BaseMessage], add_messages]
#     user_input: str
#     current_mode: str
#     selected_role: str
#     role_config: Dict[str, Any]
#     critic_diagnosis: Dict[str, Any]
#     planned_tasks: List[Dict[str, Any]]
#     generated_content: Dict[str, Any]
#     validation_status: bool
#     validation_errors: str
#     attempt_count: int
#     max_retry: int
#     llm_unavailable: bool
#     thread_id: str
#     conversation_id: str
#     bound_document_text: str
#     bound_file_name: str
#     bound_file_uploaded_at: str
#     document_status: str
#     analysis_snapshot: Dict[str, Any]
#     hypergraph_data: Dict[str, Any]
#     competition_context: Dict[str, Any]
#     stage_flow: Dict[str, Any]


# def build_initial_state(
#     user_input: str,
#     current_mode: str = "learning",
#     max_retry: int | None = None,
#     thread_id: str = "",
#     conversation_id: str = "",
#     bound_document_text: str = "",
#     bound_file_name: str = "",
#     bound_file_uploaded_at: str = "",
#     document_status: str = "none",
#     analysis_snapshot: Dict[str, Any] | None = None,
# ) -> AgentState:
#     settings = get_settings()
#     snapshot = analysis_snapshot or {}
#     existing_stage_flow = ((snapshot.get('project') or {}).get('stage_flow') or {}) if current_mode == 'project' else {}

#     # === 核心改动：组装 Messages，拦截并注入教师干预 ===
#     messages = []
    
#     # 从前端传来的快照中提取教师干预列表
#     interventions = snapshot.get("teacher_interventions", [])
#     active_interventions = [item.get("content") for item in interventions if item.get("active") and item.get("content")]
    
#     # 如果存在有效的教师干预，作为最高优先级的 SystemMessage 注入
#     if active_interventions:
#         intervention_text = "\n".join(f"- {text}" for text in active_interventions)
#         system_prompt = (
#             "【最高优先级指令 - 教师强制教学干预】\n"
#             "人类教师对当前学生下达了强制的教学干预指令。你在本次回复中，必须严格执行以下策略，甚至可以打断当前的常规进度：\n"
#             f"{intervention_text}\n\n"
#             "【执行指南】\n"
#             "1. 若干预是【干预规则】：直接遵循该规则调整你的提问或评估。\n"
#             "2. 若干预包含【结构化案例注入】：说明老师给学生发了一个商业案例卡片。你必须在回复中引导学生阅读该案例，并提取案例中的痛点或方案反问学生（例如：『参考老师发的案例，你的项目在这个环节是怎么设计的？），切勿单纯复述案例。\n"
#             "（注：请将上述干预自然地融入你的回复中，不要机械宣告，而是以助教的口吻引导学生。）"
#         )
#         messages.append(SystemMessage(content=system_prompt))
#     # ====================================================

#     return {
#         "messages": messages, # 使用组装好的 messages 数组
#         "user_input": user_input,
#         "current_mode": current_mode,
#         "selected_role": "",
#         "role_config": {},
#         "critic_diagnosis": {},
#         "planned_tasks": [],
#         "generated_content": {},
#         "validation_status": False,
#         "validation_errors": "",
#         "attempt_count": 0,
#         "max_retry": max_retry if max_retry is not None else settings.max_retry_count,
#         "llm_unavailable": False,
#         "thread_id": thread_id,
#         "conversation_id": conversation_id,
#         "bound_document_text": bound_document_text,
#         "bound_file_name": bound_file_name,
#         "bound_file_uploaded_at": bound_file_uploaded_at,
#         "document_status": document_status,
#         "analysis_snapshot": snapshot,
#         "hypergraph_data": {},
#         "competition_context": {},
#         "stage_flow": existing_stage_flow,
#     }


# def should_continue_after_validation(state: AgentState) -> str:
#     if state.get("validation_status"):
#         log_and_emit(state, "validator", "结构校验通过，工作流结束。")
#         return "end"

#     attempt_count = state.get("attempt_count", 0)
#     max_retry = state.get("max_retry", 2)
#     if attempt_count >= max_retry + 1:
#         log_and_emit(
#             state,
#             "validator",
#             f"结构校验仍未通过，已达到最大重试次数 {max_retry}，结束本次流程。",
#             level="warning",
#         )
#         return "end"

#     log_and_emit(
#         state,
#         "validator",
#         f"结构校验未通过，准备进行第 {attempt_count + 1} 次生成重试。",
#         level="warning",
#     )
#     return "generator"


# workflow = StateGraph(AgentState)
# workflow.add_node("router", router_node)
# workflow.add_node("critic", critic_node)
# workflow.add_node("planner", planner_node)
# workflow.add_node("generator", generator_node)
# workflow.add_node("validator", validator_node)

# workflow.set_entry_point("router")
# workflow.add_edge("router", "critic")
# workflow.add_edge("critic", "planner")
# workflow.add_edge("planner", "generator")
# workflow.add_edge("generator", "validator")
# workflow.add_conditional_edges(
#     "validator",
#     should_continue_after_validation,
#     {
#         "end": END,
#         "generator": "generator",
#     },
# )

# memory = MemorySaver()
# agent_workflow = workflow.compile(checkpointer=memory)





from typing import Any, Dict, List, TypedDict, Annotated

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from app.agents.mechanism.critic import critic_node
from app.agents.mechanism.generator import generator_node
from app.agents.mechanism.planner import planner_node
from app.agents.mechanism.router import router_node
from app.agents.mechanism.validator import validator_node
from app.core.config import get_settings
from app.core.stream_logger import log_and_emit


class AgentState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    user_input: str
    current_mode: str
    selected_role: str
    role_config: Dict[str, Any]
    critic_diagnosis: Dict[str, Any]
    planned_tasks: List[Dict[str, Any]]
    generated_content: Dict[str, Any]
    validation_status: bool
    validation_errors: str
    attempt_count: int
    max_retry: int
    llm_unavailable: bool
    thread_id: str
    conversation_id: str
    bound_document_text: str
    bound_file_name: str
    bound_file_uploaded_at: str
    document_status: str
    analysis_snapshot: Dict[str, Any]
    hypergraph_data: Dict[str, Any]
    competition_context: Dict[str, Any]
    stage_flow: Dict[str, Any]


def build_initial_state(
    user_input: str,
    current_mode: str = "learning",
    max_retry: int | None = None,
    thread_id: str = "",
    conversation_id: str = "",
    bound_document_text: str = "",
    bound_file_name: str = "",
    bound_file_uploaded_at: str = "",
    document_status: str = "none",
    analysis_snapshot: Dict[str, Any] | None = None,
) -> AgentState:
    settings = get_settings()
    snapshot = analysis_snapshot or {}
    existing_stage_flow = ((snapshot.get('project') or {}).get('stage_flow') or {}) if current_mode == 'project' else {}

    # === 核心改动：组装 Messages，拦截并注入教师干预 ===
    messages = []
    
    # 从前端传来的快照中提取教师干预列表
    interventions = snapshot.get("teacher_interventions", [])
    active_interventions = [item.get("content") for item in interventions if item.get("active") and item.get("content")]
    
    # 如果存在有效的教师干预，作为最高优先级的 SystemMessage 注入
    if active_interventions:
        intervention_text = "\n".join(f"- {text}" for text in active_interventions)
        system_prompt = (
            "【最高优先级指令 - 教师强制教学干预】\n"
            "人类教师对当前学生下达了强制的教学干预指令。你在本次回复中，必须严格执行以下策略，甚至可以打断当前的常规进度：\n"
            f"{intervention_text}\n\n"
            "【执行指南】\n"
            "1. 若干预是【干预规则】：直接遵循该规则调整你的提问或评估。\n"
            "2. 若干预包含【结构化案例注入】：说明老师给学生发了一个商业案例卡片。你必须在回复中引导学生阅读该案例，并提取案例中的痛点或方案反问学生（例如：『参考老师发的案例，你的项目在这个环节是怎么设计的？），切勿单纯复述案例。\n"
            "（注：请将上述干预自然地融入你的回复中，不要机械宣告，而是以助教的口吻引导学生。）"
        )
        messages.append(SystemMessage(content=system_prompt))
    # ====================================================

    return {
        "messages": messages, # 使用组装好的 messages 数组
        "user_input": user_input,
        "current_mode": current_mode,
        "selected_role": "",
        "role_config": {},
        "critic_diagnosis": {},
        "planned_tasks": [],
        "generated_content": {},
        "validation_status": False,
        "validation_errors": "",
        "attempt_count": 0,
        "max_retry": max_retry if max_retry is not None else settings.max_retry_count,
        "llm_unavailable": False,
        "thread_id": thread_id,
        "conversation_id": conversation_id,
        "bound_document_text": bound_document_text,
        "bound_file_name": bound_file_name,
        "bound_file_uploaded_at": bound_file_uploaded_at,
        "document_status": document_status,
        "analysis_snapshot": snapshot,
        "hypergraph_data": {},
        "competition_context": {},
        "stage_flow": existing_stage_flow,
    }


def should_continue_after_validation(state: AgentState) -> str:
    if state.get("validation_status"):
        log_and_emit(state, "validator", "结构校验通过，工作流结束。")
        return "end"

    attempt_count = state.get("attempt_count", 0)
    max_retry = state.get("max_retry", 2)
    if attempt_count >= max_retry + 1:
        log_and_emit(
            state,
            "validator",
            f"结构校验仍未通过，已达到最大重试次数 {max_retry}，结束本次流程。",
            level="warning",
        )
        return "end"

    log_and_emit(
        state,
        "validator",
        f"结构校验未通过，准备进行第 {attempt_count + 1} 次生成重试。",
        level="warning",
    )
    return "generator"


workflow = StateGraph(AgentState)
workflow.add_node("router", router_node)
workflow.add_node("critic", critic_node)
workflow.add_node("planner", planner_node)
workflow.add_node("generator", generator_node)
workflow.add_node("validator", validator_node)

workflow.set_entry_point("router")
workflow.add_edge("router", "critic")
workflow.add_edge("critic", "planner")
workflow.add_edge("planner", "generator")
workflow.add_edge("generator", "validator")
workflow.add_conditional_edges(
    "validator",
    should_continue_after_validation,
    {
        "end": END,
        "generator": "generator",
    },
)

memory = MemorySaver()
agent_workflow = workflow.compile(checkpointer=memory)
