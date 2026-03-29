from app.agents.roles import MODE_TO_ROLE_ID, ROLE_CONFIG_REGISTRY
from app.core.stream_logger import log_and_emit


def router_node(state: dict) -> dict:
    mode = (state.get("current_mode") or "learning").strip().lower()
    log_and_emit(state, "router", f"识别当前模式：{mode}")

    role_id = MODE_TO_ROLE_ID.get(mode, "student_tutor")
    selected_config = ROLE_CONFIG_REGISTRY[role_id]
    log_and_emit(state, "router", f"已分配角色：{selected_config['role_id']}")

    return {
        "current_mode": mode,
        "selected_role": selected_config["role_id"],
    }
