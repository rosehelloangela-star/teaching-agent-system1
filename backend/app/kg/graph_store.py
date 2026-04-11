import os
from collections import defaultdict
from typing import List, Dict, Any
from neo4j import GraphDatabase
from collections import defaultdict


class TeachingKnowledgeGraph:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://neo4j_db:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None

        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self._initialize_base_ontology()
        except Exception as e:
            print(f"[KG_Logger] 无法连接 Neo4j 数据库。错误: {e}", flush=True)

    def close(self):
        if self.driver:
            self.driver.close()

    def _initialize_base_ontology(self):
        if not self.driver:
            return

        base_nodes = [
            # 1. 市场分析与需求探索
            ("总潜在市场(TAM)", "Concept"), ("可服务市场(SAM)", "Concept"), ("可获得市场(SOM)", "Concept"),
            ("用户画像(Persona)", "Concept"), ("核心痛点", "Concept"), ("伪需求", "Mistake"),
            ("TAM替代SOM", "Mistake"), ("自嗨型需求", "Mistake"),
            ("某校园单车项目精准定位单校区通勤SOM成功融资", "PositiveCase"),
            
            # 2. 产品与验证
            ("最小可行性产品(MVP)", "Concept"), ("产品市场契合度(PMF)", "Concept"), ("核心壁垒(Moat)", "Concept"),
            ("精益创业", "Concept"), ("冷启动(Cold Start)", "Concept"), ("技术专利(Patent)", "Concept"),
            ("憋大招开发(过度工程)", "Mistake"), ("用App验证伪需求", "Mistake"),
            ("某校园二手书平台用微信群+在线表格做低成本MVP验证", "PositiveCase"),
            
            # 3. 商业模式与获客
            ("商业模式(Business Model)", "Concept"), ("价值主张(Value Proposition)", "Concept"),
            ("获客成本(CAC)", "Concept"), ("用户终身价值(LTV)", "Concept"), ("网络效应", "Concept"),
            ("飞轮效应", "Concept"), ("B2B", "Concept"), ("B2C", "Concept"), ("B2B2C", "Concept"),
            ("SaaS", "Concept"), ("盈利模式(Revenue Model)", "Concept"), ("转化率(CVR)", "Concept"),
            ("LTV小于CAC", "Mistake"), ("把免费当模式", "Mistake"), ("依靠烧钱补贴获客", "NegativeCase"),
            
            # 4. 财务与运营
            ("盈亏平衡点(Break-even Point)", "Concept"), ("现金流(Cash Flow)", "Concept"),
            ("单均经济模型(Unit Economics)", "Concept"), ("烧钱率(Burn Rate)", "Concept"),
            ("投资回报率(ROI)", "Concept"), ("定价策略(Pricing)", "Concept"), ("毛利率(Gross Margin)", "Concept"),
            ("财务预测脱离业务逻辑", "Mistake"), ("忽视隐藏成本", "Mistake"),
            ("单杯奶茶UE模型清晰且边际成本递减", "PositiveCase"),
            
            # 5. 团队与股权分配
            ("核心团队(Core Team)", "Concept"), ("股权分配(Equity Distribution)", "Concept"),
            ("动态股权分配", "Concept"), ("期权池(Option Pool)", "Concept"), ("一致行动人协议", "Concept"),
            ("平均分配股权", "Mistake"), ("外部导师占股过大", "Mistake"), ("兼职创始人", "NegativeCase"),
            
            # 6. 赛事专属硬规与术语 (如互联网+、挑战杯)
            ("互联网+大赛参赛要求", "Concept"), ("项目负责人控股规定", "Concept"), ("红旅赛道", "Concept"),
            ("商业计划书(BP)", "Concept"), ("路演(Roadshow)", "Concept"), ("电梯演讲(Elevator Pitch)", "Concept"),
            ("违反负责人控股规定(通常需持有10%以上并担任实控人)", "Mistake"),
            ("团队成员未占核心主导", "NegativeCase")
        ]

        base_edges = [
            # 逻辑链路关联
            ("用户画像(Persona)", "核心痛点", "PREREQ"),
            ("核心痛点", "价值主张(Value Proposition)", "PREREQ"),
            ("价值主张(Value Proposition)", "最小可行性产品(MVP)", "PREREQ"),
            ("最小可行性产品(MVP)", "产品市场契合度(PMF)", "PREREQ"),
            ("总潜在市场(TAM)", "可服务市场(SAM)", "PREREQ"),
            ("可服务市场(SAM)", "可获得市场(SOM)", "PREREQ"),
            ("获客成本(CAC)", "用户终身价值(LTV)", "PREREQ"),
            ("核心团队(Core Team)", "股权分配(Equity Distribution)", "PREREQ"),
            ("互联网+大赛参赛要求", "项目负责人控股规定", "CONTAIN"),
            
            # 常见错误关联
            ("核心痛点", "伪需求", "COMMON_MISTAKE"),
            ("核心痛点", "自嗨型需求", "COMMON_MISTAKE"),
            ("可获得市场(SOM)", "TAM替代SOM", "COMMON_MISTAKE"),
            ("最小可行性产品(MVP)", "憋大招开发(过度工程)", "COMMON_MISTAKE"),
            ("最小可行性产品(MVP)", "用App验证伪需求", "COMMON_MISTAKE"),
            ("盈利模式(Revenue Model)", "把免费当模式", "COMMON_MISTAKE"),
            ("单均经济模型(Unit Economics)", "财务预测脱离业务逻辑", "COMMON_MISTAKE"),
            ("股权分配(Equity Distribution)", "平均分配股权", "COMMON_MISTAKE"),
            ("股权分配(Equity Distribution)", "外部导师占股过大", "COMMON_MISTAKE"),
            ("项目负责人控股规定", "违反负责人控股规定(通常需持有10%以上并担任实控人)", "COMMON_MISTAKE"),
            
            # 案例关联
            ("可获得市场(SOM)", "某校园单车项目精准定位单校区通勤SOM成功融资", "HAS_POSITIVE_CASE"),
            ("最小可行性产品(MVP)", "某校园二手书平台用微信群+在线表格做低成本MVP验证", "HAS_POSITIVE_CASE"),
            ("单均经济模型(Unit Economics)", "单杯奶茶UE模型清晰且边际成本递减", "HAS_POSITIVE_CASE"),
            ("获客成本(CAC)", "依靠烧钱补贴获客", "HAS_NEGATIVE_CASE"),
            ("核心团队(Core Team)", "兼职创始人", "HAS_NEGATIVE_CASE"),
            ("项目负责人控股规定", "团队成员未占核心主导", "HAS_NEGATIVE_CASE")
        ]

        with self.driver.session() as session:
            session.run("CREATE INDEX entity_name_idx IF NOT EXISTS FOR (n:Entity) ON (n.name)")
            for name, n_type in base_nodes:
                s_type = "".join(e for e in n_type if e.isalnum() or e == "_")
                session.run(f"MERGE (n:Entity:{s_type} {{name: $name}})", name=name)
            for head, tail, rel in base_edges:
                s_rel = "".join(e for e in rel if e.isalnum() or e == "_")
                session.run(
                    f"MATCH (h:Entity {{name:$h}}), (t:Entity {{name:$t}}) MERGE (h)-[:{s_rel}]->(t)",
                    h=head,
                    t=tail,
                )

    def add_knowledge_from_triplets(self, extracted_triplets: List[Dict[str, Any]]):
        if not extracted_triplets or not self.driver:
            return
        with self.driver.session() as session:
            for triplet in extracted_triplets:
                h, t, r = triplet.get("head"), triplet.get("tail"), triplet.get("relation")
                ht, tt = triplet.get("head_type", "Concept"), triplet.get("tail_type", "Concept")
                if h and t and r:
                    sr = "".join(e for e in r if e.isalnum() or e == "_")
                    sht = "".join(e for e in ht if e.isalnum() or e == "_")
                    stt = "".join(e for e in tt if e.isalnum() or e == "_")
                    query = f"""
                    MERGE (h:Entity:{sht} {{name:$h}})
                    MERGE (t:Entity:{stt} {{name:$t}})
                    MERGE (h)-[:{sr}]->(t)
                    """
                    session.run(query, h=h, t=t)

    def get_all_entity_names(self) -> List[str]:
        if not self.driver:
            return []
        with self.driver.session() as session:
            return [r["name"] for r in session.run("MATCH (n:Entity) RETURN n.name AS name")]

    def diagnose_missing_prereqs(self, detected_concepts: List[str]) -> List[str]:
        if not detected_concepts or not self.driver:
            return []
        q = """
        MATCH (p:Entity)-[:PREREQ]->(c:Entity)
        WHERE c.name IN $dc AND NOT p.name IN $dc
        RETURN DISTINCT p.name AS m
        """
        with self.driver.session() as session:
            return [r["m"] for r in session.run(q, dc=detected_concepts)]

    def get_common_mistakes(self, concept: str) -> List[str]:
        if not concept or not self.driver:
            return []
        with self.driver.session() as session:
            return [
                r["m"]
                for r in session.run(
                    "MATCH (c:Entity {name: $c})-[:COMMON_MISTAKE]->(m:Entity) RETURN m.name AS m",
                    c=concept,
                )
            ]

    def get_positive_cases(self, concept: str) -> List[str]:
        if not concept or not self.driver:
            return []
        with self.driver.session() as session:
            return [
                r["case"]
                for r in session.run(
                    "MATCH (c:Entity {name: $c})-[:HAS_POSITIVE_CASE]->(m:Entity) RETURN m.name AS case",
                    c=concept,
                )
            ]

    def get_negative_cases(self, concept: str) -> List[str]:
        if not concept or not self.driver:
            return []
        with self.driver.session() as session:
            return [
                r["case"]
                for r in session.run(
                    "MATCH (c:Entity {name: $c})-[:HAS_NEGATIVE_CASE]->(m:Entity) RETURN m.name AS case",
                    c=concept,
                )
            ]

    def expand_related_learning_concepts(self, detected_concepts: List[str], limit: int = 6) -> List[str]:
        if not detected_concepts or not self.driver:
            return []

        query = """
        MATCH (n:Entity)-[:PREREQ]-(m:Entity)
        WHERE n.name IN $concepts
        RETURN DISTINCT m.name AS name
        LIMIT $limit
        """
        with self.driver.session() as session:
            result = session.run(query, concepts=detected_concepts, limit=limit)
            return [r["name"] for r in result if r["name"] not in detected_concepts]

    def _normalize_triple_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        rel_obj = record.get("rel")
        rel_type = ""
        try:
            rel_type = rel_obj.type
        except Exception:
            rel_type = str(rel_obj)

        return {
            "source": record.get("source"),
            "relation": rel_type,
            "target": record.get("target"),
            "source_labels": list(record.get("source_labels", [])),
            "target_labels": list(record.get("target_labels", [])),
        }

    def get_related_triples(self, detected_concepts: List[str], max_triples: int = 30) -> List[Dict[str, Any]]:
        if not detected_concepts or not self.driver:
            return []

        query = """
        MATCH (n:Entity)-[rel]-(m:Entity)
        WHERE n.name IN $concepts
        RETURN DISTINCT
            n.name AS source,
            labels(n) AS source_labels,
            rel,
            m.name AS target,
            labels(m) AS target_labels
        LIMIT $max_triples
        """

        with self.driver.session() as session:
            result = session.run(query, concepts=detected_concepts, max_triples=max_triples)
            return [self._normalize_triple_record(record) for record in result]

    def get_learning_subgraph(self, detected_concepts: List[str], max_triples: int = 30) -> Dict[str, Any]:
        if not detected_concepts:
            return {
                "hit_nodes": [],
                "triples": [],
                "positive_cases": {},
                "negative_cases": {},
                "mistakes": {},
                "missing_prereqs": [],
                "fallback_case_needed": True,
            }

        positive_cases = defaultdict(list)
        negative_cases = defaultdict(list)
        mistakes = defaultdict(list)

        # 🌟 修改点 2：把邻居概念拉进来！(利用你已经写好的函数)
        expanded_concepts = self.expand_related_learning_concepts(detected_concepts, limit=5)
        all_target_concepts = list(set(detected_concepts + expanded_concepts))

        triples = self.get_related_triples(detected_concepts=detected_concepts, max_triples=max_triples)
        missing_prereqs = self.diagnose_missing_prereqs(detected_concepts)

        # 🌟 修改点 3：遍历所有相关概念（而不仅是直接命中的概念）来抓取案例和错误
        for concept in all_target_concepts:
            for item in self.get_common_mistakes(concept):
                mistakes[concept].append(item)
            for item in self.get_positive_cases(concept):
                positive_cases[concept].append(item)
            for item in self.get_negative_cases(concept):
                negative_cases[concept].append(item)

        has_real_case = any(
            len(items) > 0
            for items in list(positive_cases.values()) + list(negative_cases.values())
        )

        return {
            "hit_nodes": detected_concepts, 
            "expanded_nodes": expanded_concepts, # 可以把连带节点也返回
            "triples": triples,
            "positive_cases": dict(positive_cases),
            "negative_cases": dict(negative_cases),
            "mistakes": dict(mistakes),
            "missing_prereqs": missing_prereqs,
            "fallback_case_needed": not has_real_case,
        }

    def build_learning_context(self, kg_result: Dict[str, Any]) -> str:
        if not kg_result or not kg_result.get("hit_nodes"):
            return ""

        lines = ["【Neo4j 学习知识图谱检索结果】"]

        hit_nodes = kg_result.get("hit_nodes", [])
        if hit_nodes:
            lines.append(f"- 命中概念：{', '.join(hit_nodes)}")

        missing_prereqs = kg_result.get("missing_prereqs", [])
        if missing_prereqs:
            lines.append(f"- 缺失前置概念：{', '.join(missing_prereqs)}")

        for concept, items in (kg_result.get("mistakes", {}) or {}).items():
            if items:
                lines.append(f"- 概念【{concept}】常见错误：{', '.join(items)}")

        for concept, items in (kg_result.get("positive_cases", {}) or {}).items():
            if items:
                lines.append(f"- 概念【{concept}】正向案例：{', '.join(items)}")

        for concept, items in (kg_result.get("negative_cases", {}) or {}).items():
            if items:
                lines.append(f"- 概念【{concept}】反向案例：{', '.join(items)}")

        triples = kg_result.get("triples", [])
        if triples:
            lines.append(
                "- 本轮命中关系：" +
                "；".join(f"{t['source']} -[{t['relation']}]-> {t['target']}" for t in triples[:12])
            )

        return "\n".join(lines)

    def get_global_graph_for_visualization(self, limit: int = 500) -> Dict[str, Any]:
        """
        返回整个 Neo4j 图谱，给前端做“全图 + 当前命中高亮”
        """
        if not self.driver:
            return {"nodes": [], "triples": []}

        cypher = """
        MATCH (a)-[r]->(b)
        RETURN a.name AS source,
            labels(a)[0] AS source_type,
            type(r) AS relation,
            b.name AS target,
            labels(b)[0] AS target_type
        LIMIT $limit
        """

        triples: List[Dict[str, Any]] = []
        node_map: Dict[str, Dict[str, Any]] = {}

        with self.driver.session() as session:
            records = session.run(cypher, {"limit": limit})
            for record in records:
                source = record["source"]
                target = record["target"]
                relation = record["relation"]
                source_type = record["source_type"] or "Concept"
                target_type = record["target_type"] or "Concept"

                if not source or not target or not relation:
                    continue

                triples.append({
                    "source": source,
                    "relation": relation,
                    "target": target,
                })

                if source not in node_map:
                    node_map[source] = {"id": source, "label": source, "type": source_type}
                if target not in node_map:
                    node_map[target] = {"id": target, "label": target, "type": target_type}

        return {
            "nodes": list(node_map.values()),
            "triples": triples,
        }


    def get_query_graph_for_visualization(self, detected_concepts: List[str]) -> Dict[str, Any]:
        """
        返回当前问题命中的局部子图
        """
        kg_context = self.get_learning_subgraph(detected_concepts) if detected_concepts else {
            "hit_nodes": [],
            "triples": [],
            "missing_prereqs": [],
            "positive_cases": {},
            "negative_cases": {},
            "mistakes": {},
            "fallback_case_needed": True,
        }

        node_map: Dict[str, Dict[str, Any]] = {}

        for name in kg_context.get("hit_nodes", []) or []:
            node_map[name] = {
                "id": name,
                "label": name,
                "type": "Concept",
                "is_hit": True,
            }

        for triple in kg_context.get("triples", []) or []:
            s = triple.get("source")
            t = triple.get("target")
            if s and s not in node_map:
                node_map[s] = {"id": s, "label": s, "type": "Unknown", "is_hit": s in kg_context.get("hit_nodes", [])}
            if t and t not in node_map:
                node_map[t] = {"id": t, "label": t, "type": "Unknown", "is_hit": t in kg_context.get("hit_nodes", [])}

        return {
            "nodes": list(node_map.values()),
            "triples": kg_context.get("triples", []),
            "hit_nodes": kg_context.get("hit_nodes", []),
            "missing_prereqs": kg_context.get("missing_prereqs", []),
        }


kg_store = TeachingKnowledgeGraph()

# import os
# from typing import List, Dict, Any
# from neo4j import GraphDatabase

# class TeachingKnowledgeGraph:
#     def __init__(self):
#         # 建议后续将这三个变量移入 app.core.config 的 Settings 中
#         self.uri = os.getenv("NEO4J_URI", "bolt://localhost:8063")
#         self.user = os.getenv("NEO4J_USER", "neo4j")
#         self.password = os.getenv("NEO4J_PASSWORD", "password") # 替换为你的本地密码
        
#         try:
#             self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
#             self._initialize_base_ontology()
#         except Exception as e:
#             print(f"[KG_Store] 无法连接到 Neo4j 数据库，请检查服务是否启动。错误: {e}")

#     def close(self):
#         if hasattr(self, 'driver'):
#             self.driver.close()

#     def _initialize_base_ontology(self):
#         """初始化双创课程本体框架，创建索引并预置基础知识"""
#         base_nodes = [
#             ("产品市场契合度(PMF)", "Concept"), ("总潜在市场(TAM)", "Concept"),
#             ("可服务潜在市场(SAM)", "Concept"), ("可获得服务市场(SOM)", "Concept"),
#             ("用户画像(User Persona)", "Concept"), ("核心痛点(Core Pain Point)", "Concept"),
#             ("价值主张(Value Proposition)", "Concept"), ("商业模式(Business Model)", "Concept"),
#             ("精益画布(Lean Canvas)", "Method"), ("用户访谈(User Interview)", "Task"),
#             ("商业计划书(BP)", "Artifact"), ("伪需求", "Mistake"),
#             ("逻辑自洽幻觉", "Mistake"), ("无竞争对手错觉", "Mistake"),
#             ("TAM替代SOM", "Mistake")
#         ]
        
#         base_edges = [
#             ("核心痛点(Core Pain Point)", "价值主张(Value Proposition)", "PREREQ"),
#             ("用户画像(User Persona)", "核心痛点(Core Pain Point)", "PREREQ"),
#             ("总潜在市场(TAM)", "可服务潜在市场(SAM)", "PREREQ"),
#             ("可服务潜在市场(SAM)", "可获得服务市场(SOM)", "PREREQ"),
#             ("精益画布(Lean Canvas)", "价值主张(Value Proposition)", "CONTAIN"),
#             ("核心痛点(Core Pain Point)", "伪需求", "COMMON_MISTAKE"),
#             ("商业计划书(BP)", "逻辑自洽幻觉", "COMMON_MISTAKE"),
#             ("可获得服务市场(SOM)", "TAM替代SOM", "COMMON_MISTAKE"),
#             ("用户访谈(User Interview)", "核心痛点(Core Pain Point)", "GENERATE")
#         ]

#         with self.driver.session() as session:
#             # 1. 创建基于 name 属性的索引，大幅提升实体检索速度
#             session.run("CREATE INDEX entity_name_idx IF NOT EXISTS FOR (n:Entity) ON (n.name)")
            
#             # 2. 注入基础节点 (附加通用标签 Entity 和 具体类型标签)
#             for name, n_type in base_nodes:
#                 safe_type = ''.join(e for e in n_type if e.isalnum() or e == '_')
#                 query = f"MERGE (n:Entity:{safe_type} {{name: $name}})"
#                 session.run(query, name=name)
                
#             # 3. 注入基础关系
#             for head, tail, rel in base_edges:
#                 safe_rel = ''.join(e for e in rel if e.isalnum() or e == '_')
#                 query = f"""
#                 MATCH (h:Entity {{name: $head}})
#                 MATCH (t:Entity {{name: $tail}})
#                 MERGE (h)-[:{safe_rel}]->(t)
#                 """
#                 session.run(query, head=head, tail=tail)

#     def add_knowledge_from_triplets(self, extracted_triplets: List[Dict[str, Any]]):
#         """将大模型抽取的三元组批量写入 Neo4j"""
#         if not extracted_triplets: return
        
#         with self.driver.session() as session:
#             for triplet in extracted_triplets:
#                 head = triplet.get("head")
#                 head_type = triplet.get("head_type", "Concept")
#                 tail = triplet.get("tail")
#                 tail_type = triplet.get("tail_type", "Concept")
#                 rel = triplet.get("relation")

#                 if head and tail and rel:
#                     safe_rel = ''.join(e for e in rel if e.isalnum() or e == '_')
#                     safe_head_type = ''.join(e for e in head_type if e.isalnum() or e == '_')
#                     safe_tail_type = ''.join(e for e in tail_type if e.isalnum() or e == '_')
                    
#                     # 动态拼接 Cypher，确保节点和边同时被 MERGE
#                     query = f"""
#                     MERGE (h:Entity:{safe_head_type} {{name: $head}})
#                     MERGE (t:Entity:{safe_tail_type} {{name: $tail}})
#                     MERGE (h)-[:{safe_rel}]->(t)
#                     """
#                     session.run(query, head=head, tail=tail)

#     def get_all_entity_names(self) -> List[str]:
#         """拉取所有实体名称，用于在 critic 中与用户输入做字符串碰撞"""
#         with self.driver.session() as session:
#             result = session.run("MATCH (n:Entity) RETURN n.name AS name")
#             return [record["name"] for record in result]

#     def diagnose_missing_prereqs(self, detected_concepts: List[str]) -> List[str]:
#         """Cypher 级诊断：找到 detected_concepts 依赖的前置条件，且该前置条件不在列表中"""
#         if not detected_concepts: return []
        
#         query = """
#         MATCH (pred:Entity)-[:PREREQ]->(concept:Entity)
#         WHERE concept.name IN $detected_concepts 
#           AND NOT pred.name IN $detected_concepts
#         RETURN DISTINCT pred.name AS missing_prereq
#         """
#         with self.driver.session() as session:
#             result = session.run(query, detected_concepts=detected_concepts)
#             return [record["missing_prereq"] for record in result]

#     def get_common_mistakes(self, concept: str) -> List[str]:
#         """Cypher 查询特定概念的高发错误"""
#         query = """
#         MATCH (c:Entity {name: $concept})-[:COMMON_MISTAKE]->(m:Entity)
#         RETURN m.name AS mistake
#         """
#         with self.driver.session() as session:
#             result = session.run(query, concept=concept)
#             return [record["mistake"] for record in result]

# # 全局单例
# kg_store = TeachingKnowledgeGraph()