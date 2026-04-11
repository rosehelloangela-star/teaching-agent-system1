import queue
import threading
import time
from typing import Any, Dict, Optional

_stream_queues: dict[str, queue.Queue] = {}
_lock = threading.Lock()


def register_stream(thread_id: str) -> queue.Queue:
    q: queue.Queue = queue.Queue()
    with _lock:
        _stream_queues[thread_id] = q
    return q


def unregister_stream(thread_id: str) -> None:
    with _lock:
        _stream_queues.pop(thread_id, None)


def emit_event(thread_id: Optional[str], event: Dict[str, Any]) -> None:
    if not thread_id:
        return

    payload = {
        "timestamp": time.strftime("%H:%M:%S"),
        **event,
    }

    with _lock:
        q = _stream_queues.get(thread_id)

    if q is not None:
        q.put(payload)


# ====== 修改1：增加 meta ======
def emit_log(
    thread_id: Optional[str],
    node: str,
    message: str,
    level: str = "info",
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    emit_event(
        thread_id,
        {
            "type": "log",
            "node": node,
            "level": level,
            "message": message,
            "meta": meta or {},
        },
    )


def emit_final(thread_id: Optional[str], data: Dict[str, Any]) -> None:
    emit_event(thread_id, {"type": "final", "data": data})


def emit_error(thread_id: Optional[str], message: str) -> None:
    emit_event(thread_id, {"type": "error", "message": message})


def emit_done(thread_id: Optional[str]) -> None:
    emit_event(thread_id, {"type": "done"})


# ====== 修改2：log_and_emit 透传 meta ======
def log_and_emit(
    state: Optional[dict],
    node: str,
    message: str,
    level: str = "info",
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    prefix = f"[{node}][{level}] {message}"
    print(prefix, flush=True)

    thread_id = None
    if isinstance(state, dict):
        thread_id = state.get("thread_id")

    emit_log(thread_id, node=node, message=message, level=level, meta=meta)