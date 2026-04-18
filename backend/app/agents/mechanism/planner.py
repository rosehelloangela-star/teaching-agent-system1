# from typing import List

# from langchain_core.prompts import ChatPromptTemplate
# from pydantic import BaseModel, Field

# from app.agents.mechanism.llm_config import get_llm
# from app.core.json_utils import extract_first_json_value, message_content_to_text
# from app.core.stream_logger import log_and_emit


# class PlannedTask(BaseModel):
#     task_desc: str = Field(description="任务描述")
#     priority: int = Field(description="优先级，1最高，3最低", ge=1, le=3)
#     expected_output: str = Field(description="完成后应得到的结果或产物")


# class PlannerOutput(BaseModel):
#     tasks: List[PlannedTask] = Field(description="任务列表")


# def planner_node(state: dict) -> dict:
#     diagnosis = state.get("critic_diagnosis", {}).get("raw_analysis", "")
#     current_mode = state.get("current_mode", "learning")
#     competition_context = state.get("competition_context", {})

#     messages = state.get("messages", [])
#     past_tasks_context = "无"
#     if len(messages) > 1:
#         past_tasks_context = messages[-2].content if len(messages) >= 2 else "无"

#     task_limit_map = {
#         "competition": 3,
#         "instructor": 3,
#         "teacher": 3,
#         "assessment": 2,
#         "grading": 2,
#         "learning": 1,
#         "project": 1,
#     }
#     task_limit = task_limit_map.get(current_mode, 1)

#     extra_context = ""
#     if current_mode == "competition" and competition_context:
#         focus_dims = ", ".join(
#             f"{item['dimension_name']}({item['weight']}%)"
#             for item in competition_context.get("top_focus_dimensions", [])
#         )
#         extra_context = (
#             f"\n【当前赛事模板】{competition_context.get('template_name')}\n"
#             f"【高权重优先维度】{focus_dims or '无'}\n"
#             "请优先输出能在24h/72h内提升高权重维度的任务。"
#         )

#     llm = get_llm(temperature=0.2, max_tokens=350)
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 (
#                     "你是任务规划器。\n"
#                     "请根据诊断结果，输出不超过 {task_limit} 条下一步任务。\n"
#                     "注意参考【历史辅导记录】，如果学生已经尝试解决过某个任务，请提出更深入的下一步行动，避免重复布置相同的任务！\n"
#                     "任务必须可执行、可交付、可验证。\n"
#                     "只返回合法 JSON，不要解释，不要 markdown。\n"
#                     "返回格式严格如下：\n"
#                     "{{\n"
#                     '  "tasks": [\n'
#                     "    {{\n"
#                     '      "task_desc": "任务描述",\n'
#                     '      "priority": 1,\n'
#                     '      "expected_output": "完成后应得到的结果或产物"\n'
#                     "    }}\n"
#                     "  ]\n"
#                     "}}"
#                 ),
#             ),
#             (
#                 "user",
#                 "【历史辅导记录】（供参考是否重复）：\n{past_context}\n\n【本次诊断结果】：\n{diagnosis}{extra_context}",
#             ),
#         ]
#     )

#     chain = prompt | llm
#     log_and_emit(state, "planner", "正在生成下一步规划...")

#     response = chain.invoke(
#         {
#             "task_limit": task_limit,
#             "past_context": str(past_tasks_context)[:500],
#             "diagnosis": diagnosis,
#             "extra_context": extra_context,
#         }
#     )
#     raw_text = message_content_to_text(response)
#     parsed = extract_first_json_value(raw_text)
    
#     # 【核心修复】：兼容大模型各种千奇百怪的 JSON 返回格式，坚决保留其真实生成内容
#     if isinstance(parsed, list):
#         # 应对大模型直接返回 [...] 列表的情况
#         parsed = {"tasks": parsed}
#     elif isinstance(parsed, dict) and "tasks" not in parsed:
#         # 应对大模型只返回单个任务对象 {...} 漏掉 tasks 键的情况
#         parsed = {"tasks": [parsed]}
        
#     result = PlannerOutput.model_validate(parsed)
#     tasks = [task.model_dump() for task in result.tasks[:task_limit]]

#     log_and_emit(state, "planner", f"任务规划成功，生成 {len(tasks)} 条任务。")
#     return {"planned_tasks": tasks}




from typing import List

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.agents.mechanism.llm_config import get_llm
from app.core.json_utils import extract_first_json_value, message_content_to_text
from app.core.stream_logger import log_and_emit


class PlannedTask(BaseModel):
    task_desc: str = Field(description="任务描述")
    priority: int = Field(description="优先级，1最高，3最低", ge=1, le=3)
    expected_output: str = Field(description="完成后应得到的结果或产物")


class PlannerOutput(BaseModel):
    tasks: List[PlannedTask] = Field(description="任务列表")


def planner_node(state: dict) -> dict:
    diagnosis = state.get("critic_diagnosis", {}).get("raw_analysis", "")
    current_mode = state.get("current_mode", "learning")
    competition_context = state.get("competition_context", {})

    messages = state.get("messages", [])
    past_tasks_context = "无"
    if len(messages) > 1:
        past_tasks_context = messages[-2].content if len(messages) >= 2 else "无"

    task_limit_map = {
        "competition": 3,
        "instructor": 3,
        "teacher": 3,
        "assessment": 2,
        "grading": 2,
        "learning": 1,
        "project": 1,
    }
    task_limit = task_limit_map.get(current_mode, 1)

    extra_context = ""
    if current_mode == "competition" and competition_context:
        focus_dims = ", ".join(
            f"{item['dimension_name']}({item['weight']}%)"
            for item in competition_context.get("top_focus_dimensions", [])
        )
        extra_context = (
            f"\n【当前赛事模板】{competition_context.get('template_name')}\n"
            f"【高权重优先维度】{focus_dims or '无'}\n"
            "请优先输出能在24h/72h内提升高权重维度的任务。"
        )

    llm = get_llm(temperature=0.2, max_tokens=350)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "你是任务规划器。\n"
                    "请根据诊断结果，输出不超过 {task_limit} 条下一步任务。\n"
                    "注意参考【历史辅导记录】，如果学生已经尝试解决过某个任务，请提出更深入的下一步行动，避免重复布置相同的任务！\n"
                    "任务必须可执行、可交付、可验证。\n"
                    "只返回合法 JSON，不要解释，不要 markdown。\n"
                    "返回格式严格如下：\n"
                    "{{\n"
                    '  "tasks": [\n'
                    "    {{\n"
                    '      "task_desc": "任务描述",\n'
                    '      "priority": 1,\n'
                    '      "expected_output": "完成后应得到的结果或产物"\n'
                    "    }}\n"
                    "  ]\n"
                    "}}"
                ),
            ),
            (
                "user",
                "【历史辅导记录】（供参考是否重复）：\n{past_context}\n\n【本次诊断结果】：\n{diagnosis}{extra_context}",
            ),
        ]
    )

    chain = prompt | llm
    log_and_emit(state, "planner", "正在生成下一步规划...")

    response = chain.invoke(
        {
            "task_limit": task_limit,
            "past_context": str(past_tasks_context)[:500],
            "diagnosis": diagnosis,
            "extra_context": extra_context,
        }
    )
    raw_text = message_content_to_text(response)
    parsed = extract_first_json_value(raw_text)
    
    # 【核心修复】：兼容大模型各种千奇百怪的 JSON 返回格式，坚决保留其真实生成内容
    if isinstance(parsed, list):
        # 应对大模型直接返回 [...] 列表的情况
        parsed = {"tasks": parsed}
    elif isinstance(parsed, dict) and "tasks" not in parsed:
        # 应对大模型只返回单个任务对象 {...} 漏掉 tasks 键的情况
        parsed = {"tasks": [parsed]}
        
    result = PlannerOutput.model_validate(parsed)
    tasks = [task.model_dump() for task in result.tasks[:task_limit]]

    log_and_emit(state, "planner", f"任务规划成功，生成 {len(tasks)} 条任务。")
    return {"planned_tasks": tasks}
