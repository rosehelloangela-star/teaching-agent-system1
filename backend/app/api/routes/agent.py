import asyncio
import json
import queue
import uuid
from contextlib import suppress
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.graph_workflow import agent_workflow, build_initial_state
from app.core.file_utils import extract_file_payload
from app.core.json_utils import _safe_json_loads
from app.core.stream_logger import emit_done, emit_error, emit_final, emit_log, register_stream, unregister_stream
from app.db.database import get_db
from app.db.models import Conversation
from app.schemas.agent import AgentRunResponse
from app.kg.graph_store import kg_store

router = APIRouter(prefix="/agent", tags=["agent"])

def _payload_to_prompt_text(payload: dict) -> str:
    return f"\n\n--- 附件：{payload['filename']} 开始 ---\n{payload['text']}\n--- 附件：{payload['filename']} 结束 ---\n"

def _merge_analysis_snapshot(conversation: Conversation, payload: dict, current_mode: str) -> dict:
    snapshot = _safe_json_loads(conversation.analysis_snapshot, {})
    if current_mode not in snapshot:
        snapshot[current_mode] = {}
    snapshot[current_mode].update(payload)
    return snapshot

def _build_agent_response(
    final_state: dict,
    current_mode: str,
    thread_id: str,
    conversation: Conversation | None = None,
) -> dict:
    analysis_snapshot = {}
    conversation_id = None
    document_status = "none"
    bound_file_name = None
    bound_file_uploaded_at = None
    if conversation is not None:
        conversation_id = conversation.id
        document_status = conversation.document_status or "none"
        bound_file_name = conversation.bound_file_name
        bound_file_uploaded_at = (
            conversation.bound_file_uploaded_at.isoformat()
            if conversation.bound_file_uploaded_at
            else None
        )
        analysis_snapshot = _safe_json_loads(conversation.analysis_snapshot, {})
    return {
        "current_mode": final_state.get("current_mode", current_mode),
        "selected_role": final_state.get("selected_role", ""),
        "critic_diagnosis": final_state.get("critic_diagnosis", {}),
        "planned_tasks": final_state.get("planned_tasks", []),
        "generated_content": final_state.get("generated_content", {}),
        "validation_status": final_state.get("validation_status", False),
        "validation_errors": final_state.get("validation_errors", ""),
        "attempt_count": final_state.get("attempt_count", 0),
        "thread_id": thread_id,
        "conversation_id": conversation_id,
        "document_status": document_status,
        "bound_file_name": bound_file_name,
        "bound_file_uploaded_at": bound_file_uploaded_at,
        "analysis_snapshot": analysis_snapshot,
        "hypergraph_data": final_state.get("hypergraph_data", {}), # 【新增】加入超图数据
        "stage_flow": final_state.get("stage_flow", {}),
        "kg_context": final_state.get("kg_context", {}),
    }

async def _load_file_payloads(files: List[UploadFile]) -> List[dict]:
    payloads = []
    for file in files:
        if file.filename:
            payloads.append(await extract_file_payload(file))
    return payloads

def _persist_bound_document(conversation: Conversation, payloads: List[dict], db: Session) -> Conversation:
    usable_payloads = [p for p in payloads if p.get("supported") and (p.get("text") or "").strip()]
    if not usable_payloads:
        return conversation
    merged_text = "\n\n".join(
        f"【附件：{p['filename']}】\n{p['text']}"
        for p in usable_payloads
    )
    conversation.bound_file_name = usable_payloads[0]["filename"]
    conversation.bound_document_text = merged_text
    conversation.bound_file_uploaded_at = datetime.utcnow()
    conversation.document_status = "bound"
    db.commit()
    db.refresh(conversation)
    return conversation

@router.get("/health")
def agent_health() -> dict:
    return {"status": "ok", "message": "agent route is running"}

@router.post("/run", response_model=AgentRunResponse)
async def run_agent(
    user_input: str = Form(default=""),
    current_mode: str = Form(default="learning"),
    thread_id: str = Form(default=""),
    conversation_id: str = Form(default=""),
    max_retry: int = Form(default=2),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
) -> AgentRunResponse:
    try:
        if not thread_id:
            thread_id = str(uuid.uuid4())
        conversation = None
        if conversation_id:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="会话不存在")
        file_payloads = await _load_file_payloads(files)

        if conversation is not None and file_payloads:
            conversation = _persist_bound_document(conversation, file_payloads, db)

        if conversation is not None and current_mode in {"project", "competition"}:
            if conversation.document_status != "bound":
                raise HTTPException(
                    status_code=400,
                    detail="当前会话尚未绑定商业计划书，请先上传并绑定 BP 文档后再使用项目模式或竞赛模式。",
                )

        file_texts = ""
        if conversation is None and file_payloads:
            file_texts = "".join(_payload_to_prompt_text(p) for p in file_payloads)
        combined_input = user_input
        if file_texts:
            combined_input = f"{user_input}{file_texts}".strip()
        if not combined_input:
            raise HTTPException(status_code=400, detail="输入文本与附件不能同时为空")

        initial_state = build_initial_state(
            user_input=combined_input,
            current_mode=current_mode,
            max_retry=max_retry,
            thread_id=thread_id,
            conversation_id=conversation.id if conversation else "",
            bound_document_text=conversation.bound_document_text if conversation else "",
            bound_file_name=conversation.bound_file_name if conversation else "",
            bound_file_uploaded_at=conversation.bound_file_uploaded_at.isoformat() if conversation and conversation.bound_file_uploaded_at else "",
            document_status=conversation.document_status if conversation else "none",
            analysis_snapshot=_safe_json_loads(conversation.analysis_snapshot, {}) if conversation else {},
        )
        config = {"configurable": {"thread_id": thread_id}}
        final_state = agent_workflow.invoke(initial_state, config=config)

        if conversation is not None:
            payload_before_snapshot = _build_agent_response(final_state, current_mode, thread_id, conversation)
            snapshot = _merge_analysis_snapshot(conversation, payload_before_snapshot, current_mode)
            
            # 【核心修改】确保提取到的 hypergraph_data / stage_flow 被持久化到数据库分析快照中
            if current_mode not in snapshot:
                snapshot[current_mode] = {}
            if "hypergraph_data" in final_state and final_state["hypergraph_data"]:
                snapshot[current_mode]["hypergraph_data"] = final_state["hypergraph_data"]
            if current_mode == "project" and "stage_flow" in final_state and final_state["stage_flow"]:
                snapshot[current_mode]["stage_flow"] = final_state["stage_flow"]
            # ====== 新增：learning 模式保存 kg_context ======
            if current_mode == "learning" and "kg_context" in final_state and final_state["kg_context"]:
                snapshot[current_mode]["kg_context"] = final_state["kg_context"]

            conversation.analysis_snapshot = json.dumps(snapshot, ensure_ascii=False)
            conversation.last_mode = current_mode
            db.commit()
            db.refresh(conversation)

        return AgentRunResponse(**_build_agent_response(final_state, current_mode, thread_id, conversation))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent workflow 执行失败：{str(e)}")

@router.post("/run/stream")
async def run_agent_stream(
    user_input: str = Form(default=""),
    current_mode: str = Form(default="learning"),
    thread_id: str = Form(default=""),
    conversation_id: str = Form(default=""),
    max_retry: int = Form(default=2),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    if not thread_id:
        thread_id = str(uuid.uuid4())
    conversation = None
    if conversation_id:
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")
            
    file_payloads = await _load_file_payloads(files)
    if conversation is not None and file_payloads:
        conversation = _persist_bound_document(conversation, file_payloads, db)
        
    if conversation is not None and current_mode in {"project", "competition"}:
        if conversation.document_status != "bound":
            raise HTTPException(
                status_code=400,
                detail="当前会话尚未绑定商业计划书，请先上传并绑定 BP 文档后再使用项目模式或竞赛模式。",
            )
            
    file_texts = ""
    if conversation is None and file_payloads:
        file_texts = "".join(_payload_to_prompt_text(p) for p in file_payloads)
    combined_input = user_input
    if file_texts:
        combined_input = f"{user_input}{file_texts}".strip()
    if not combined_input:
        raise HTTPException(status_code=400, detail="输入文本与附件不能同时为空")

    initial_state = build_initial_state(
        user_input=combined_input,
        current_mode=current_mode,
        max_retry=max_retry,
        thread_id=thread_id,
        conversation_id=conversation.id if conversation else "",
        bound_document_text=conversation.bound_document_text if conversation else "",
        bound_file_name=conversation.bound_file_name if conversation else "",
        bound_file_uploaded_at=conversation.bound_file_uploaded_at.isoformat() if conversation and conversation.bound_file_uploaded_at else "",
        document_status=conversation.document_status if conversation else "none",
        analysis_snapshot=_safe_json_loads(conversation.analysis_snapshot, {}) if conversation else {},
    )
    
    config = {"configurable": {"thread_id": thread_id}}
    stream_queue = register_stream(thread_id)
    
    async def produce_workflow_events() -> None:
        try:
            emit_log(thread_id, "api", "请求已接收，开始创建工作流。")
            if conversation is not None and conversation.document_status == "bound":
                emit_log(
                    thread_id,
                    "api",
                    f"当前会话已绑定文档：{conversation.bound_file_name or '未命名文件'}，将自动纳入本轮分析。",
                )
            emit_log(thread_id, "api", "附件与输入已解析完成，准备启动多 Agent 协同流程。")
            
            final_state = await asyncio.to_thread(agent_workflow.invoke, initial_state, config=config)
            
            if conversation is not None:
                payload_before_snapshot = _build_agent_response(final_state, current_mode, thread_id, conversation)
                snapshot = _merge_analysis_snapshot(conversation, payload_before_snapshot, current_mode)
                
                # 【核心修改】为流式输出同样保存超图信息与阶段推进状态
                if current_mode not in snapshot:
                    snapshot[current_mode] = {}
                if "hypergraph_data" in final_state and final_state["hypergraph_data"]:
                    snapshot[current_mode]["hypergraph_data"] = final_state["hypergraph_data"]
                if current_mode == "project" and "stage_flow" in final_state and final_state["stage_flow"]:
                    snapshot[current_mode]["stage_flow"] = final_state["stage_flow"]
                # ====== 新增：learning 模式保存 kg_context ======
                if current_mode == "learning" and "kg_context" in final_state and final_state["kg_context"]:
                    snapshot[current_mode]["kg_context"] = final_state["kg_context"]
                    
                conversation.analysis_snapshot = json.dumps(snapshot, ensure_ascii=False)
                conversation.last_mode = current_mode
                db.commit()
                db.refresh(conversation)
                
            emit_log(thread_id, "api", "工作流执行完成，正在整理最终输出。")
            emit_final(thread_id, _build_agent_response(final_state, current_mode, thread_id, conversation))
        except Exception as e:
            emit_error(thread_id, f"Agent workflow 执行失败：{str(e)}")
        finally:
            emit_done(thread_id)

    producer_task = asyncio.create_task(produce_workflow_events())
    
    async def event_generator():
        try:
            while True:
                try:
                    event = await asyncio.to_thread(stream_queue.get, True, 0.25)
                    yield f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"
                    if event.get("type") == "done":
                        break
                except queue.Empty:
                    if producer_task.done():
                        await asyncio.sleep(0.05)
                    continue
        finally:
            with suppress(Exception):
                await producer_task
            unregister_stream(thread_id)
            
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/kg/graph")
def get_learning_kg_graph(
    view: str = "query",
    q: str = "",
) -> dict:
    """
    view=query  -> 当前查询子图
    view=global -> 全图
    q           -> learning 模式下的用户问题
    """
    try:
        if view == "global":
            return {
                "ok": True,
                "view": "global",
                "data": kg_store.get_global_graph_for_visualization(limit=800),
            }

        all_db_nodes = kg_store.get_all_entity_names()
        detected_concepts = detect_concepts(q or "", all_db_nodes, fuzzy_threshold=72, debug=False)

        return {
            "ok": True,
            "view": "query",
            "data": kg_store.get_query_graph_for_visualization(detected_concepts),
        }
    except Exception as e:
        return {
            "ok": False,
            "view": view,
            "data": {"nodes": [], "triples": [], "hit_nodes": []},
            "error": str(e),
        }