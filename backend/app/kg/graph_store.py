import os
from typing import List, Dict, Any
from neo4j import GraphDatabase

class TeachingKnowledgeGraph:
    def __init__(self):
        # 建议后续将这三个变量移入 app.core.config 的 Settings 中
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:8063")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password") # 替换为你的本地密码
        
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self._initialize_base_ontology()
        except Exception as e:
            print(f"[KG_Store] 无法连接到 Neo4j 数据库，请检查服务是否启动。错误: {e}")

    def close(self):
        if hasattr(self, 'driver'):
            self.driver.close()

    def _initialize_base_ontology(self):
        """初始化双创课程本体框架，创建索引并预置基础知识"""
        base_nodes = [
            ("产品市场契合度(PMF)", "Concept"), ("总潜在市场(TAM)", "Concept"),
            ("可服务潜在市场(SAM)", "Concept"), ("可获得服务市场(SOM)", "Concept"),
            ("用户画像(User Persona)", "Concept"), ("核心痛点(Core Pain Point)", "Concept"),
            ("价值主张(Value Proposition)", "Concept"), ("商业模式(Business Model)", "Concept"),
            ("精益画布(Lean Canvas)", "Method"), ("用户访谈(User Interview)", "Task"),
            ("商业计划书(BP)", "Artifact"), ("伪需求", "Mistake"),
            ("逻辑自洽幻觉", "Mistake"), ("无竞争对手错觉", "Mistake"),
            ("TAM替代SOM", "Mistake")
        ]
        
        base_edges = [
            ("核心痛点(Core Pain Point)", "价值主张(Value Proposition)", "PREREQ"),
            ("用户画像(User Persona)", "核心痛点(Core Pain Point)", "PREREQ"),
            ("总潜在市场(TAM)", "可服务潜在市场(SAM)", "PREREQ"),
            ("可服务潜在市场(SAM)", "可获得服务市场(SOM)", "PREREQ"),
            ("精益画布(Lean Canvas)", "价值主张(Value Proposition)", "CONTAIN"),
            ("核心痛点(Core Pain Point)", "伪需求", "COMMON_MISTAKE"),
            ("商业计划书(BP)", "逻辑自洽幻觉", "COMMON_MISTAKE"),
            ("可获得服务市场(SOM)", "TAM替代SOM", "COMMON_MISTAKE"),
            ("用户访谈(User Interview)", "核心痛点(Core Pain Point)", "GENERATE")
        ]

        with self.driver.session() as session:
            # 1. 创建基于 name 属性的索引，大幅提升实体检索速度
            session.run("CREATE INDEX entity_name_idx IF NOT EXISTS FOR (n:Entity) ON (n.name)")
            
            # 2. 注入基础节点 (附加通用标签 Entity 和 具体类型标签)
            for name, n_type in base_nodes:
                safe_type = ''.join(e for e in n_type if e.isalnum() or e == '_')
                query = f"MERGE (n:Entity:{safe_type} {{name: $name}})"
                session.run(query, name=name)
                
            # 3. 注入基础关系
            for head, tail, rel in base_edges:
                safe_rel = ''.join(e for e in rel if e.isalnum() or e == '_')
                query = f"""
                MATCH (h:Entity {{name: $head}})
                MATCH (t:Entity {{name: $tail}})
                MERGE (h)-[:{safe_rel}]->(t)
                """
                session.run(query, head=head, tail=tail)

    def add_knowledge_from_triplets(self, extracted_triplets: List[Dict[str, Any]]):
        """将大模型抽取的三元组批量写入 Neo4j"""
        if not extracted_triplets: return
        
        with self.driver.session() as session:
            for triplet in extracted_triplets:
                head = triplet.get("head")
                head_type = triplet.get("head_type", "Concept")
                tail = triplet.get("tail")
                tail_type = triplet.get("tail_type", "Concept")
                rel = triplet.get("relation")

                if head and tail and rel:
                    safe_rel = ''.join(e for e in rel if e.isalnum() or e == '_')
                    safe_head_type = ''.join(e for e in head_type if e.isalnum() or e == '_')
                    safe_tail_type = ''.join(e for e in tail_type if e.isalnum() or e == '_')
                    
                    # 动态拼接 Cypher，确保节点和边同时被 MERGE
                    query = f"""
                    MERGE (h:Entity:{safe_head_type} {{name: $head}})
                    MERGE (t:Entity:{safe_tail_type} {{name: $tail}})
                    MERGE (h)-[:{safe_rel}]->(t)
                    """
                    session.run(query, head=head, tail=tail)

    def get_all_entity_names(self) -> List[str]:
        """拉取所有实体名称，用于在 critic 中与用户输入做字符串碰撞"""
        with self.driver.session() as session:
            result = session.run("MATCH (n:Entity) RETURN n.name AS name")
            return [record["name"] for record in result]

    def diagnose_missing_prereqs(self, detected_concepts: List[str]) -> List[str]:
        """Cypher 级诊断：找到 detected_concepts 依赖的前置条件，且该前置条件不在列表中"""
        if not detected_concepts: return []
        
        query = """
        MATCH (pred:Entity)-[:PREREQ]->(concept:Entity)
        WHERE concept.name IN $detected_concepts 
          AND NOT pred.name IN $detected_concepts
        RETURN DISTINCT pred.name AS missing_prereq
        """
        with self.driver.session() as session:
            result = session.run(query, detected_concepts=detected_concepts)
            return [record["missing_prereq"] for record in result]

    def get_common_mistakes(self, concept: str) -> List[str]:
        """Cypher 查询特定概念的高发错误"""
        query = """
        MATCH (c:Entity {name: $concept})-[:COMMON_MISTAKE]->(m:Entity)
        RETURN m.name AS mistake
        """
        with self.driver.session() as session:
            result = session.run(query, concept=concept)
            return [record["mistake"] for record in result]

# 全局单例
kg_store = TeachingKnowledgeGraph()