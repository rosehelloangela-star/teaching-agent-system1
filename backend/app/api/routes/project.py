from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from sqlalchemy.orm import Session
from typing import List
import json
from collections import defaultdict

from app.db.database import get_db
from app.db.models import Project, User, Conversation
from app.schemas.project import ProjectResponse, ChatSyncRequest

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse)
async def create_project(
    name: str = Form(...),
    student_id: str = Form(...),
    content: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    file_name = file.filename if file else None
    new_project = Project(
        name=name,
        student_id=student_id,
        content=content,
        file_name=file_name,
        status="pending"
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.get("/", response_model=List[ProjectResponse])
def get_projects(student_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Project)
    if student_id:
        query = query.filter(Project.student_id == student_id)
    return query.order_by(Project.created_at.desc()).all()


@router.put("/{project_id}/chat", response_model=ProjectResponse)
def sync_chat_history(project_id: str, request: ChatSyncRequest, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目未找到")
    project.chat_history = request.chat_history
    db.commit()
    db.refresh(project)
    return project


# ---------- helpers for teacher insights ----------

def _safe_json_loads(raw, fallback):
    if not raw:
        return fallback
    try:
        return json.loads(raw)
    except Exception:
        return fallback


def _pct(count: int, total: int) -> float:
    return round((count / total) * 100, 1) if total else 0.0


def _fallback_interventions(top_mistakes: list[dict], coverage_summary: list[dict]) -> list[dict]:
    interventions = []
    weakest_dims = sorted(coverage_summary, key=lambda x: x.get("mastery_rate", 0))[:3]

    for item in top_mistakes[:3]:
        label = item.get("mistake") or item.get("rule_name") or item.get("dimension_name") or "未知问题"
        if "单位经济" in label or "财务" in label:
            interventions.append({
                "title": "财务与单位经济专项训练",
                "why": f"{label} 是当前高频问题之一",
                "plan": [
                    "理论课：讲解单位经济、CAC/LTV 与盈亏平衡点",
                    "实操课：要求每组提交一页单位经济测算表",
                ],
            })
        elif "渠道" in label or "客群" in label:
            interventions.append({
                "title": "用户—渠道匹配工作坊",
                "why": f"{label} 暴露出班级普遍存在用户触达错位",
                "plan": [
                    "理论课：讲解目标用户画像与渠道选择逻辑",
                    "实操课：要求每组完成一份用户触达路径图",
                ],
            })
        elif "技术" in label or "TRL" in label or "学术" in label:
            interventions.append({
                "title": "技术论证与证据表达训练",
                "why": f"{label} 反映出技术成熟度/学术支撑不足",
                "plan": [
                    "理论课：讲解技术验证、TRL 与论文/专利支撑写法",
                    "实操课：要求每组补充一页技术论证与验证计划",
                ],
            })

    if weakest_dims:
        weak_names = "、".join(d["dimension_name"] for d in weakest_dims)
        interventions.append({
            "title": "下周重点教学主题建议",
            "why": f"当前班级掌握率最低的维度集中在：{weak_names}",
            "plan": [
                f"理论课：优先讲解 {weak_names}",
                "实践课：围绕上述薄弱维度要求所有团队提交针对性补件",
            ],
        })

    return interventions[:4]


@router.get("/class-insights")
def get_class_insights(class_name: str, db: Session = Depends(get_db)):
    """教师端：班级真实学情洞察（聚合学生端 project / competition 快照）"""
    students = db.query(User).filter(User.role == "student", User.class_name == class_name).all()
    if not students:
        return {
            "class_name": class_name,
            "total_students": 0,
            "total_projects": 0,
            "average_rubric_score": 0,
            "average_competition_score_pct": 0,
            "rule_trigger_frequency": {},
            "hypergraph_alerts": [],
            "competitions": {},
            "high_risk_projects": [],
            "coverage_summary": [],
            "top_mistakes": [],
            "teaching_interventions": [],
        }

    student_map = {s.id: s.real_name for s in students}
    student_ids = list(student_map.keys())

    conversations = db.query(Conversation).filter(
        Conversation.student_id.in_(student_ids),
        Conversation.document_status == "bound"
    ).all()

    total_projects = len(conversations)
    total_students = len(students)

    alert_display_counter = defaultdict(int)
    rule_trigger_frequency = defaultdict(int)
    competition_data = defaultdict(list)
    high_risk_projects = []

    dimension_agg = defaultdict(lambda: {
        "dimension_id": "",
        "dimension_name": "",
        "total_score": 0.0,
        "count": 0,
    })
    mistake_counter = defaultdict(lambda: {
        "mistake": "",
        "count": 0,
        "source": "",
    })

    avg_score_bucket = []
    avg_pct_bucket = []

    for conv in conversations:
        snap = _safe_json_loads(conv.analysis_snapshot, {})
        student_name = student_map.get(conv.student_id, conv.student_id)
        project_title = conv.bound_file_name or conv.title or "未命名项目"

        # ----- project snapshot -----
        project_snap = snap.get("project", {}) or {}
        proj_alerts = ((project_snap.get("hypergraph_data") or {}).get("alerts") or [])
        alert_count = len(proj_alerts)

        issue_names = []
        for a in proj_alerts:
            rule_id = a.get("rule", "UnknownRule")
            rule_name = a.get("name", "未知断层")
            rule_trigger_frequency[rule_id] += 1
            alert_display_counter[f"[{rule_id}] {rule_name}"] += 1
            issue_names.append(rule_name)
            mistake_counter[f"rule::{rule_id}"]["mistake"] = rule_name
            mistake_counter[f"rule::{rule_id}"]["count"] += 1
            mistake_counter[f"rule::{rule_id}"]["source"] = "project"

        # ----- competition snapshot -----
        comp_snap = snap.get("competition", {}) or {}
        comp_generated = (comp_snap.get("generated_content") or {})
        comp_meta = comp_generated.get("competition_meta") or {}
        comp_summary = comp_generated.get("score_summary") or {}
        rubric_items = comp_generated.get("rubric_items") or []

        comp_name = comp_meta.get("short_name") or comp_meta.get("template_name")
        weighted_pct = float(comp_summary.get("weighted_score_pct", 0) or 0)
        avg_score = float(comp_summary.get("average_score", 0) or 0)

        if comp_name:
            competition_data[comp_name].append({
                "project_name": project_title,
                "student_name": student_name,
                "score": weighted_pct,
                "average_score": avg_score,
                "template_name": comp_meta.get("template_name", comp_name),
            })
            avg_pct_bucket.append(weighted_pct)
            avg_score_bucket.append(avg_score)

        for item in rubric_items:
            dim_id = item.get("dimension_id") or item.get("dimension_name")
            dim_name = item.get("dimension_name") or dim_id or "未知维度"
            score = float(item.get("estimated_score", 0) or 0)
            rec = dimension_agg[dim_id]
            rec["dimension_id"] = dim_id
            rec["dimension_name"] = dim_name
            rec["total_score"] += score
            rec["count"] += 1

            if score <= 2:
                key = f"dim::{dim_id}"
                mistake_counter[key]["mistake"] = dim_name
                mistake_counter[key]["count"] += 1
                mistake_counter[key]["source"] = "competition"

        # ----- high risk -----
        risk_reasons = []
        if alert_count >= 2:
            risk_reasons.append(f"触发 {alert_count} 条超图断层")
        if comp_name and weighted_pct < 60:
            risk_reasons.append(f"竞赛模拟得分偏低（{weighted_pct}/100）")
        if any(float((item or {}).get("estimated_score", 5) or 5) <= 1 for item in rubric_items):
            risk_reasons.append("存在极低分维度，需要优先补证")

        if risk_reasons:
            high_risk_projects.append({
                "project_name": project_title,
                "student_name": student_name,
                "alert_count": alert_count,
                "issues": "；".join(risk_reasons),
                "top_alerts": issue_names[:2],
                "competition_score": weighted_pct,
            })

    coverage_summary = []
    for dim in dimension_agg.values():
        avg_score = round(dim["total_score"] / dim["count"], 2) if dim["count"] else 0
        coverage_summary.append({
            "dimension_id": dim["dimension_id"],
            "dimension_name": dim["dimension_name"],
            "average_score": avg_score,
            "mastery_rate": round((avg_score / 5) * 100, 1),
            "sample_count": dim["count"],
        })
    coverage_summary.sort(key=lambda x: x["mastery_rate"], reverse=True)

    top_mistakes = []
    for key, value in sorted(mistake_counter.items(), key=lambda x: x[1]["count"], reverse=True)[:5]:
        top_mistakes.append({
            "mistake": value["mistake"],
            "count": value["count"],
            "percentage": _pct(value["count"], total_projects),
            "source": value["source"],
        })

    sorted_alerts = [
        {
            "rule": k,
            "count": v,
            "percentage": _pct(v, total_projects),
        }
        for k, v in sorted(alert_display_counter.items(), key=lambda x: x[1], reverse=True)
    ]

    for comp in list(competition_data.keys()):
        competition_data[comp] = sorted(competition_data[comp], key=lambda x: x["score"], reverse=True)

    high_risk_projects = sorted(
        high_risk_projects,
        key=lambda x: (x["alert_count"], x.get("competition_score", 100) * -1),
        reverse=True,
    )

    average_rubric_score = round(sum(avg_score_bucket) / len(avg_score_bucket), 2) if avg_score_bucket else 0
    average_competition_score_pct = round(sum(avg_pct_bucket) / len(avg_pct_bucket), 1) if avg_pct_bucket else 0

    teaching_interventions = _fallback_interventions(top_mistakes, coverage_summary)

    return {
        "class_name": class_name,
        "total_students": total_students,
        "total_projects": total_projects,
        "average_rubric_score": average_rubric_score,
        "average_competition_score_pct": average_competition_score_pct,
        "rule_trigger_frequency": dict(rule_trigger_frequency),
        "hypergraph_alerts": sorted_alerts,
        "competitions": dict(competition_data),
        "high_risk_projects": high_risk_projects,
        "coverage_summary": coverage_summary,
        "top_mistakes": top_mistakes,
        "teaching_interventions": teaching_interventions,
    }

