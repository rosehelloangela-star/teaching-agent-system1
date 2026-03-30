import json
import re
from typing import Any, Type, TypeVar

from pydantic import BaseModel

# 【新增】安全解析 JSON 的辅助函数
def _safe_json_loads(text: str, default: Any = None) -> Any:
    """安全解析 JSON 字符串，解析失败时返回默认值"""
    try:
        if not text or not isinstance(text, str):
            return default if default is not None else {}
        return json.loads(text)
    except Exception:
        return default if default is not None else {}

T = TypeVar("T", bound=BaseModel)


def message_content_to_text(message: Any) -> str:
    """
    兼容 LangChain / OpenAI 风格返回，尽量把 content 统一转成纯文本。
    """
    content = getattr(message, "content", message)

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(str(item))
            else:
                parts.append(str(item))
        return "\n".join(part for part in parts if part).strip()

    return str(content).strip()


def strip_think_blocks(text: str) -> str:
    """
    去掉部分推理模型可能返回的 <think>...</think> 内容。
    """
    return re.sub(r"<think>.*?</think>", "", text, flags=re.IGNORECASE | re.DOTALL).strip()


def _try_json_loads(text: str) -> Any:
    return json.loads(text)


def _extract_balanced_json(text: str, start_idx: int) -> str | None:
    """
    从 text[start_idx] 开始，尝试提取一个平衡的 JSON 对象或数组。
    """
    if start_idx >= len(text) or text[start_idx] not in "{[":
        return None

    stack: list[str] = []
    opening = text[start_idx]
    stack.append("}" if opening == "{" else "]")

    in_string = False
    escape = False

    for i in range(start_idx + 1, len(text)):
        ch = text[i]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            stack.append("}")
        elif ch == "[":
            stack.append("]")
        elif ch in "}]":
            if not stack or ch != stack[-1]:
                return None
            stack.pop()
            if not stack:
                return text[start_idx : i + 1]

    return None


def extract_first_json_value(text: str) -> Any:
    """
    从模型返回文本里尽量提取第一个可解析 JSON。
    支持：
    1. 整段就是 JSON
    2. ```json ... ``` 代码块
    3. 文本中夹杂的第一个 JSON 对象/数组
    """
    cleaned = strip_think_blocks(text)

    # 情况1：整段就是 JSON
    try:
        return _try_json_loads(cleaned)
    except Exception:
        pass

    # 情况2：json 代码块
    fence_matches = re.findall(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.IGNORECASE | re.DOTALL)
    for candidate in fence_matches:
        candidate = candidate.strip()
        try:
            return _try_json_loads(candidate)
        except Exception:
            continue

    # 情况3：全文扫描第一个平衡 JSON
    for i, ch in enumerate(cleaned):
        if ch in "{[":
            candidate = _extract_balanced_json(cleaned, i)
            if candidate is None:
                continue
            try:
                return _try_json_loads(candidate)
            except Exception:
                continue

    raise ValueError(
        "未能从模型输出中提取有效 JSON。原始输出前500字符如下：\n"
        f"{cleaned[:500]}"
    )


def parse_pydantic_from_text(text: str, model_cls: Type[T]) -> T:
    data = extract_first_json_value(text)
    return model_cls.model_validate(data)