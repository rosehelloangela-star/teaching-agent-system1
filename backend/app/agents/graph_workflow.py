# from typing import Any, Dict, List, TypedDict, Annotated
# from langgraph.graph import END, StateGraph
# from langgraph.graph.message import add_messages
# from langchain_core.messages import BaseMessage, HumanMessage
# from langgraph.checkpoint.memory import MemorySaver

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
#     critic_diagnosis: Dict[str, Any]
#     planned_tasks: List[Dict[str, Any]]
#     generated_content: Dict[str, Any]
#     validation_status: bool
#     validation_errors: str
#     attempt_count: int
#     max_retry: int
#     llm_unavailable: bool
#     thread_id: str


# def build_initial_state(
#     user_input: str,
#     current_mode: str = "learning",
#     max_retry: int | None = None,
#     thread_id: str = "",
# ) -> AgentState:
#     settings = get_settings()
#     return {
#         "messages": [HumanMessage(content=user_input)],
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
# app = workflow.compile(checkpointer=memory)



from typing import Any, Dict, List, TypedDict, Annotated

from langchain_core.messages import BaseMessage, HumanMessage
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

    # 新增：会话级上下文
    conversation_id: str
    bound_document_text: str
    bound_file_name: str
    bound_file_uploaded_at: str
    document_status: str
    analysis_snapshot: Dict[str, Any]


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

    return {
        "messages": [HumanMessage(content=user_input)],
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
        "analysis_snapshot": analysis_snapshot or {},
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
app = workflow.compile(checkpointer=memory)