from pydantic import ValidationError
from app.agents.roles import ROLE_CONFIG_REGISTRY
from app.core.stream_logger import log_and_emit


def validator_node(state: dict) -> dict:
    generated = state.get("generated_content", {})
    role_id = state.get("selected_role", "student_tutor")
    schema = ROLE_CONFIG_REGISTRY.get(role_id, {}).get("output_schema")

    log_and_emit(state, "validator", "开始执行结构校验。")

    if isinstance(generated, dict) and generated.get("_parser_error"):
        log_and_emit(
            state,
            "validator",
            "生成器没有返回合法 JSON，已触发重试。",
            level="warning",
        )
        return {
            "validation_status": False,
            "validation_errors": (
                "生成器没有返回合法 JSON，已触发重试。\n"
                f"解析错误：{generated.get('_parser_error')}"
            ),
        }

    try:
        schema.model_validate(generated)
        log_and_emit(state, "validator", "输出结构符合 Schema 要求。")
        return {
            "validation_status": True,
            "validation_errors": "",
        }
    except ValidationError as e:
        log_and_emit(state, "validator", "结构校验失败，准备反馈给生成器重试。", level="warning")
        return {
            "validation_status": False,
            "validation_errors": f"结构校验失败，请按 Schema 修正：\n{str(e)}",
        }
    except Exception as e:
        log_and_emit(state, "validator", f"发生未知校验错误：{e}", level="error")
        return {
            "validation_status": False,
            "validation_errors": f"未知校验错误：{str(e)}",
        }
