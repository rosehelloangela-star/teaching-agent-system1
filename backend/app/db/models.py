# from sqlalchemy import Column, String, Text, DateTime
# from sqlalchemy.sql import func
# from app.db.database import Base
# import uuid

# # 生成用户 ID (u_开头)
# def generate_user_uuid():
#     return f"u_{uuid.uuid4().hex[:8]}"

# # 生成项目 ID (p_开头)
# def generate_project_uuid():
#     return f"p_{uuid.uuid4().hex[:8]}"

# # ================= 1. 用户表 =================
# class User(Base):
#     __tablename__ = "users"

#     id = Column(String, primary_key=True, default=generate_user_uuid, index=True)
#     username = Column(String, unique=True, index=True, nullable=False)
#     password = Column(String, nullable=False)
    
#     real_name = Column(String, nullable=False)
#     class_name = Column(String, nullable=True)
    
#     role = Column(String, default="student") 
    
#     created_at = Column(DateTime(timezone=True), server_default=func.now())


# # ================= 2. 项目表 =================
# class Project(Base):
#     __tablename__ = "projects"

#     # 项目基础信息
#     id = Column(String, primary_key=True, default=generate_project_uuid, index=True)
#     name = Column(String, index=True, nullable=False)
#     student_id = Column(String, index=True, nullable=False) # 绑定具体学生 (可以用学号或预设的 user_id)
    
#     # 项目核心内容
#     content = Column(Text, nullable=True) # 学生在右侧工作台敲的 BP 文本
#     file_name = Column(String, nullable=True) # 学生上传的附件名

#     # 【新增这行】把对话记录当作 JSON 字符串存在这个字段里
#     chat_history = Column(Text, default="[]")
    
#     # 教师评估与流转状态
#     status = Column(String, default="pending") # 状态：pending(待评估), evaluated(已批改)
#     instructor_notes = Column(Text, nullable=True) # 老师发送的复核备注 (Review Notes)
#     assessment_result = Column(Text, nullable=True) # AI 自动生成的 Rubric 评分 JSON 字符串
    
#     # 时间戳 (自动管理)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


# 生成用户 ID (u_开头)
def generate_user_uuid():
    return f"u_{uuid.uuid4().hex[:8]}"


# 生成项目 ID (p_开头)
def generate_project_uuid():
    return f"p_{uuid.uuid4().hex[:8]}"


# 生成会话 ID (c_开头)
def generate_conversation_uuid():
    return f"c_{uuid.uuid4().hex[:8]}"


# ================= 1. 用户表 =================
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_user_uuid, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    real_name = Column(String, nullable=False)
    class_name = Column(String, nullable=True)

    role = Column(String, default="student")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ================= 2. 项目表（保留旧工作台） =================
class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=generate_project_uuid, index=True)
    name = Column(String, index=True, nullable=False)
    student_id = Column(String, index=True, nullable=False)

    content = Column(Text, nullable=True)
    file_name = Column(String, nullable=True)
    chat_history = Column(Text, default="[]")

    status = Column(String, default="pending")
    instructor_notes = Column(Text, nullable=True)
    assessment_result = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ================= 3. 会话表（自由对话持久化核心） =================
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=generate_conversation_uuid, index=True)
    student_id = Column(String, index=True, nullable=False)

    title = Column(String, nullable=False, default="新对话")
    chat_history = Column(Text, nullable=False, default="[]")

    bound_file_name = Column(String, nullable=True)
    bound_file_uploaded_at = Column(DateTime(timezone=True), nullable=True)
    bound_document_text = Column(Text, nullable=True)
    document_status = Column(String, nullable=False, default="none") 

    analysis_snapshot = Column(Text, nullable=False, default="{}")
    last_mode = Column(String, nullable=False, default="learning")
    
    # 【新增字段】：用于持久化存储该会话的学生画像评估报告
    evaluation_report = Column(Text, nullable=True) 

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# ================= 4. 班级报告表（新增） =================
# 用于持久化存储 Agent 生成的班级学情综合诊断报告
class ClassReport(Base):
    __tablename__ = "class_reports"

    id = Column(String, primary_key=True, default=lambda: f"cr_{uuid.uuid4().hex[:8]}", index=True)
    class_name = Column(String, unique=True, index=True, nullable=False)
    report_content = Column(Text, nullable=True) # 存放 JSON 字符串
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class KnowledgeCard(Base):
    __tablename__ = "knowledge_cards"

    id = Column(String, primary_key=True, index=True, default=lambda: f"card_{uuid.uuid4().hex[:8]}")
    title = Column(String, nullable=False)
    card_type = Column(String, default="case") # case / policy / method
    industry = Column(String)
    target_customer = Column(String)
    core_pain_point = Column(Text)
    solution = Column(Text)
    business_model = Column(Text)
    applicable_stages = Column(String)
    covered_rule_ids = Column(String) # 关联的规则ID
    evidence_items = Column(Text)     # 存储为 JSON 字符串
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # 也可以加上创建者教师 ID
    creator_id = Column(String, nullable=True)