// import React, { useMemo, useRef, useEffect, useState } from 'react';
// import {
//   Briefcase,
//   Trophy,
//   Network,
//   AlertTriangle,
//   ShieldAlert,
//   BarChart3,
//   Radar,
//   ClipboardList,
//   CheckCircle,
//   X,
// } from 'lucide-react';
// import ForceGraph2D from 'react-force-graph-2d';
// import {
//   RadarChart,
//   PolarGrid,
//   PolarAngleAxis,
//   PolarRadiusAxis,
//   Radar as RechartsRadar,
//   ResponsiveContainer,
//   BarChart,
//   Bar,
//   XAxis,
//   YAxis,
//   CartesianGrid,
//   Tooltip,
// } from 'recharts';

// // 在前端同步后端规则的元数据配置，用于规则检视面板
// const RULE_METADATA = {
//   "System": { "name": "图谱元素过少", "severity": "high", "weight": 18 },
//   "R1": { "name": "全局逻辑散架", "severity": "critical", "weight": 30 },
//   "R2": { "name": "技术与商业双轨孤岛", "severity": "critical", "weight": 30 },
//   "R3": { "name": "叙事因果断裂", "severity": "high", "weight": 18 },
//   "R4": { "name": "合规逻辑游离", "severity": "medium", "weight": 10 },
//   "R5": { "name": "闭环要素严重缺失", "severity": "high", "weight": 18 },
//   "R6": { "name": "渠道与客群脱节", "severity": "medium", "weight": 10 },
//   "R7": { "name": "支付意愿支撑不足", "severity": "high", "weight": 18 },
//   "R8": { "name": "无竞争对手幻觉", "severity": "critical", "weight": 30 },
//   "R9": { "name": "市场漏斗断层", "severity": "medium", "weight": 10 },
//   "R10": { "name": "创新缺乏竞争对标", "severity": "medium", "weight": 10 },
//   "R11": { "name": "单位经济模型崩塌", "severity": "critical", "weight": 30 },
//   "R12": { "name": "利润空间黑盒", "severity": "high", "weight": 18 },
//   "R13": { "name": "现金流断裂高危", "severity": "critical", "weight": 30 },
//   "R14": { "name": "供应链脱离业务", "severity": "high", "weight": 18 },
//   "R15": { "name": "冷启动策略空转", "severity": "medium", "weight": 10 },
//   "R16": { "name": "技术壁垒无团队支撑", "severity": "medium", "weight": 10 },
//   "R17": { "name": "执行方案空壳", "severity": "medium", "weight": 10 },
//   "R18": { "name": "财务预测漂浮", "severity": "high", "weight": 18 },
//   "R19": { "name": "频次与收入模型错配", "severity": "high", "weight": 18 },
//   "R20": { "name": "公益属性过重", "severity": "medium", "weight": 10 },
// };

// const RULE_EDGE_BINDINGS = {
//   System: ['Core_Business_Loop'],
//   R1: ['Core_Business_Loop'],
//   R2: ['Core_Business_Loop', 'Tech_Barrier'],
//   R3: ['Narrative_Causality'],
//   R4: ['Compliance_Ethics', 'Core_Business_Loop'],
//   R5: ['Core_Business_Loop'],
//   R6: ['Channel_Physical_Access', 'Core_Business_Loop'],
//   R7: ['Willingness_To_Pay'],
//   R8: ['Real_Competition'],
//   R9: ['Market_Reachability'],
//   R10: ['Innovation_Verification', 'Real_Competition'],
//   R11: ['Unit_Economics'],
//   R12: ['Pricing_Space'],
//   R13: ['Cash_Flow_Health'],
//   R14: ['Supply_Chain_Sync', 'Core_Business_Loop'],
//   R15: ['Cold_Start_Engine', 'Core_Business_Loop'],
//   R16: ['R&D_Team_Match'],
//   R17: ['Resource_Feasibility'],
//   R18: ['Financial_Reasonableness', 'Core_Business_Loop'],
//   R19: ['Frequency_Mismatch'],
//   R20: ['Social_Value_Translation', 'Core_Business_Loop'],
// };

// const STAGE_ACCENTS = [
//   { bg: '#fff7ed', border: '#fdba74', header: '#f97316', soft: '#ffedd5', muted: '#9a3412' },
//   { bg: '#eff6ff', border: '#93c5fd', header: '#2563eb', soft: '#dbeafe', muted: '#1d4ed8' },
//   { bg: '#faf5ff', border: '#c4b5fd', header: '#7c3aed', soft: '#ede9fe', muted: '#6d28d9' },
// ];

// const SEMANTIC_DIMENSION_LABELS = {
//   field_type_consistency: '字段类型一致性',
//   channel_customer_fit: '渠道与客群适配',
//   narrative_causality: '痛点—方案因果链',
//   competition_realism: '竞争分析真实性',
//   market_funnel_consistency: '市场漏斗一致性',
//   innovation_against_competition: '创新对标充分性',
//   price_customer_fit: '定价与客群匹配',
//   unit_economics: '单位经济合理性',
//   pricing_space: '定价与利润空间',
//   cash_flow_health: '现金流安全性',
//   financial_reasonableness: '财务预测可信度',
//   frequency_revenue_fit: '频次与收费匹配',
//   tech_business_alignment: '技术与商业融合度',
//   compliance_industry: '合规路径充分性',
//   supply_chain_sync: '供应链与交付闭环',
//   cold_start_engine: '冷启动起盘能力',
//   team_tech_match: '团队与技术匹配',
//   resource_feasibility: '资源与里程碑可行性',
//   social_value_translation: '社会价值商业化转译',
// };

// const SEMANTIC_STATUS_META = {
//   contradictory: { label: '语义冲突', badge: 'bg-red-100 text-red-700 border-red-200', card: 'border-red-200 bg-red-50/60' },
//   suspicious: { label: '语义存疑', badge: 'bg-orange-100 text-orange-700 border-orange-200', card: 'border-orange-200 bg-orange-50/60' },
//   needs_evidence: { label: '待补证', badge: 'bg-amber-100 text-amber-700 border-amber-200', card: 'border-amber-200 bg-amber-50/60' },
//   confirmed: { label: '语义通过', badge: 'bg-emerald-100 text-emerald-700 border-emerald-200', card: 'border-emerald-200 bg-emerald-50/60' },
//   unknown: { label: '未复核', badge: 'bg-slate-100 text-slate-700 border-slate-200', card: 'border-slate-200 bg-slate-50' },
// };

// const SEVERITY_RANK = { critical: 4, high: 3, medium: 2, low: 1 };

// function uniqueOrdered(list = []) {
//   return Array.from(new Set((list || []).filter(Boolean)));
// }

// function normalizeSeverity(value) {
//   return String(value || 'medium').toLowerCase();
// }

// function buildTopologyModel({ hypergraph, projectStageFlow, formatNodeName, semanticEdgeQuality }) {
//   const edgeMap = hypergraph?.edges || {};
//   const stages = Object.values(projectStageFlow?.stages || {}).sort((a, b) => (a.index || 0) - (b.index || 0));
//   const alerts = [...(hypergraph?.alerts || [])];
//   const globalAlertMap = alerts.reduce((acc, alert) => {
//     if (alert?.rule) acc[alert.rule] = alert;
//     return acc;
//   }, {});

//   const parseConceptLabel = (raw) => {
//     if (!raw) return '';
//     let text = String(raw);
//     if (text.includes(': ')) text = text.split(': ')[1];
//     else if (text.includes(':')) text = text.split(':')[1];
//     else if (text.includes('：')) text = text.split('：')[1];
//     else text = formatNodeName(text);
//     return text.trim();
//   };

//   const ruleMap = {};
//   const conceptMap = {};
//   const topicMap = {};
//   const ruleToConcepts = {};
//   const ruleToTopics = {};
//   const conceptToRules = {};
//   const conceptToTopics = {};
//   const conceptFrequency = {};

//   const lanes = stages.map((stage, stageIdx) => {
//     const activeRuleSet = new Set(stage.active_rule_ids || []);
//     const resolvedRuleSet = new Set(stage.resolved_rule_ids || []);
//     const stageAlertMap = (stage.active_alerts || []).reduce((acc, alert) => {
//       if (alert?.rule) acc[alert.rule] = alert;
//       return acc;
//     }, {});

//     const ruleIds = stage.rule_ids || [];
//     const rules = ruleIds.map((ruleId) => {
//       const meta = RULE_METADATA[ruleId] || { name: ruleId, severity: 'medium', weight: 10 };
//       const topicKeys = uniqueOrdered(RULE_EDGE_BINDINGS[ruleId] || []);
//       const conceptIds = uniqueOrdered(topicKeys.flatMap((topicKey) => edgeMap[topicKey] || []));
//       const activeAlert = stageAlertMap[ruleId] || globalAlertMap[ruleId] || null;
//       const semanticQuality = semanticEdgeQuality?.[ruleId] || null;

//       let status = 'observed';
//       if ((stage.status || '') === 'locked') status = 'locked';
//       else if (resolvedRuleSet.has(ruleId)) status = 'resolved';
//       else if (activeRuleSet.has(ruleId) || activeAlert) status = 'active';

//       const rule = {
//         id: ruleId,
//         label: meta.name,
//         severity: normalizeSeverity(meta.severity),
//         weight: Number(meta.weight || 10),
//         status,
//         issue: activeAlert?.issue || '',
//         stageId: stage.id,
//         stageLabel: stage.label,
//         topicKeys,
//         conceptIds,
//         semanticQuality,
//       };

//       ruleMap[ruleId] = rule;
//       ruleToConcepts[ruleId] = conceptIds;
//       ruleToTopics[ruleId] = [];
//       conceptIds.forEach((conceptId) => {
//         conceptToRules[conceptId] = conceptToRules[conceptId] || [];
//         if (!conceptToRules[conceptId].includes(ruleId)) conceptToRules[conceptId].push(ruleId);
//         conceptFrequency[conceptId] = (conceptFrequency[conceptId] || 0) + 1;
//       });
//       return rule;
//     });

//     const topicKeys = uniqueOrdered(rules.flatMap((rule) => rule.topicKeys));
//     const topics = topicKeys.map((topicKey) => {
//       const conceptIds = uniqueOrdered((edgeMap[topicKey] || []).filter(Boolean));
//       const ownerRuleIds = rules.filter((rule) => rule.topicKeys.includes(topicKey)).map((rule) => rule.id);
//       const severity = ownerRuleIds.reduce((best, ruleId) => {
//         const current = ruleMap[ruleId]?.severity || 'medium';
//         return SEVERITY_RANK[current] > SEVERITY_RANK[best] ? current : best;
//       }, 'low');
//       const topicId = `${stage.id}::${topicKey}`;
//       const topic = {
//         id: topicId,
//         key: topicKey,
//         label: formatNodeName(topicKey),
//         stageId: stage.id,
//         ownerRuleIds,
//         conceptIds,
//         severity,
//         hasData: conceptIds.length > 0,
//       };
//       topicMap[topicId] = topic;
//       ownerRuleIds.forEach((ruleId) => {
//         ruleToTopics[ruleId] = ruleToTopics[ruleId] || [];
//         if (!ruleToTopics[ruleId].includes(topicId)) ruleToTopics[ruleId].push(topicId);
//       });
//       conceptIds.forEach((conceptId) => {
//         conceptToTopics[conceptId] = conceptToTopics[conceptId] || [];
//         if (!conceptToTopics[conceptId].includes(topicId)) conceptToTopics[conceptId].push(topicId);
//       });
//       return topic;
//     });

//     const conceptIds = uniqueOrdered(topics.flatMap((topic) => topic.conceptIds));
//     const concepts = conceptIds.map((conceptId) => {
//       const label = parseConceptLabel(conceptId);
//       const concept = {
//         id: conceptId,
//         label,
//         fullLabel: label,
//         ownerRuleIds: conceptToRules[conceptId] || [],
//         ownerTopicIds: conceptToTopics[conceptId] || [],
//       };
//       conceptMap[conceptId] = conceptMap[conceptId] || concept;
//       return concept;
//     });

//     return {
//       id: stage.id,
//       index: stage.index,
//       label: stage.label,
//       shortLabel: stage.short_label || `第${stage.index}阶段`,
//       progress: Number(stage.progress_pct || 0),
//       status: stage.status,
//       passThreshold: Number(stage.pass_threshold || 80),
//       rules,
//       topics,
//       concepts,
//       accent: STAGE_ACCENTS[stageIdx] || STAGE_ACCENTS[0],
//     };
//   });

//   return {
//     lanes,
//     ruleMap,
//     topicMap,
//     conceptMap,
//     ruleToConcepts,
//     ruleToTopics,
//     conceptToRules,
//     conceptToTopics,
//     conceptFrequency,
//   };
// }


// export default function SnapshotOverlay({ open, snapshot, onClose }) {
//   const containerRef = useRef(null);
//   const fgRef = useRef(null);

//   const [activeModeTab, setActiveModeTab] = useState('project');
//   // 默认 Tab 改为 'rules'
//   const [projectTab, setProjectTab] = useState('rules');
//   const [competitionTab, setCompetitionTab] = useState('overview');
//   const [topologyStageFilter, setTopologyStageFilter] = useState('');
//   const [selectedTopologyRule, setSelectedTopologyRule] = useState('');
//   const [selectedTopologyConcept, setSelectedTopologyConcept] = useState('');

//   const project = snapshot?.project?.generated_content;
//   const hypergraph = snapshot?.project?.hypergraph_data || snapshot?.hypergraph_data;
//   const projectStageFlow = snapshot?.project?.stage_flow || null;
//   const competition = snapshot?.competition?.generated_content;
//   const semanticReport = hypergraph?.semantic_report || {};
//   const semanticChecks = semanticReport?.checks || [];
//   const semanticSummary = semanticReport?.summary || {};
//   const semanticEdgeQuality = semanticReport?.edge_quality || {};
//   const structuralRuleStatus = hypergraph?.structural_rule_status || {};
//   const structuralResolvedRuleIds = structuralRuleStatus?.resolved_rule_ids || [];
//   const structuralActiveAlerts = structuralRuleStatus?.active_alerts || [];
//   const structuralFieldNotes = hypergraph?.structural_field_notes || [];

//   const stageFollowups = projectStageFlow?.current_followup_questions || [];

//   useEffect(() => {
//     if (competition && !project) setActiveModeTab('competition');
//     if (project && !competition) setActiveModeTab('project');
//   }, [project, competition]);

//   useEffect(() => {
//     if (!open) return;
//     setTopologyStageFilter(projectStageFlow?.current_stage_id || 'all');
//     setSelectedTopologyRule('');
//     setSelectedTopologyConcept('');
//   }, [open, projectStageFlow?.current_stage_id, hypergraph]);

//   const formatNodeName = (name) => {
//     const map = {
//       Target_Customer: '目标客群', Value_Proposition: '价值主张', Marketing_Channel: '营销渠道',
//       Revenue_Model: '收入模型', Cost_Structure: '成本结构', Core_Pain_Point: '核心痛点',
//       Price: '产品定价', LTV: '客户终身价值', CAC: '获客成本', Startup_Capital: '启动资金',
//       Account_Period: '账期', Seed_Users: '种子用户', Tech_Route: '技术路线',
//       Team_Background: '团队背景', Competitor_Pool: '竞争对手', IP: '知识产权',
//       Fulfill_Cost: '履约成本', Supplier_Network: '供应链', Control_Experiment: '对照实验',
//       TAM: '总潜在市场', SAM: '可服务市场', SOM: '可获得市场', Usage_Frequency: '使用频次',
//       Milestone_Plan: '里程碑', Policy_Constraints: '政策约束',
//       Core_Business_Loop: '商业核心闭环', Customer_Value_Misalignment: '客群与价值错位',
//       Channel_Physical_Access: '渠道物理触达', Willingness_To_Pay: '支付意愿支撑',
//       Market_Reachability: '市场规模漏斗', Frequency_Mismatch: '频次与收入错配',
//       Unit_Economics: '单位经济模型', Pricing_Space: '定价与利润空间',
//       Cash_Flow_Health: '现金流健康度', Financial_Reasonableness: '财务预测合理性',
//       Supply_Chain_Sync: '供应链履约交付', Cold_Start_Engine: '冷启动引擎',
//       R_D_Team_Match: '研发团队匹配', Resource_Feasibility: '资源方案可行性',
//       Tech_Barrier: '技术护城河', Real_Competition: '真实竞争格局',
//       Narrative_Causality: '叙事因果逻辑', Innovation_Verification: '创新差异化验证',
//       Compliance_Ethics: '合规与伦理限制', Social_Value_Translation: '社会价值转化',
//     };
//     return map[name] || name;
//   };

//   const formatSemanticDimension = (dimension) => SEMANTIC_DIMENSION_LABELS[dimension] || dimension || '语义校验';
//   const getSemanticStatusMeta = (status) => SEMANTIC_STATUS_META[String(status || 'unknown').toLowerCase()] || SEMANTIC_STATUS_META.unknown;

//   const getVisualLabel = (rawId) => {
//     if (!rawId) return '';
//     let text = String(rawId);
//     if (text.includes(': ')) text = text.split(': ')[1];
//     else if (text.includes(':')) text = text.split(':')[1];
//     else if (text.includes('：')) text = text.split('：')[1];
//     else text = formatNodeName(text);
//     if (text.length > 14) return text.substring(0, 14) + '...';
//     return text;
//   };

//   const graphData = useMemo(() => {
//     if (!hypergraph) return { nodes: [], links: [] };
//     const nodesData = [];
//     const linksData = [];
//     const nodeSet = new Set();
//     const discreteNodes = hypergraph.nodes || [];
//     const edges = hypergraph.edges || {};

//     discreteNodes.forEach((nodeName) => {
//       if (!nodeSet.has(nodeName)) {
//         nodesData.push({ id: nodeName, group: 1, type: 'entity' });
//         nodeSet.add(nodeName);
//       }
//     });

//     Object.entries(edges).forEach(([edgeName, linkedNodes]) => {
//       const formattedEdge = formatNodeName(edgeName);
//       const edgeNodeId = `REL_${edgeName}`;

//       nodesData.push({ id: edgeNodeId, label: formattedEdge, group: 3, type: 'relation' });

//       linkedNodes.forEach((nodeRawId) => {
//         if (!nodeSet.has(nodeRawId)) {
//           nodesData.push({ id: nodeRawId, group: 2, type: 'entity' });
//           nodeSet.add(nodeRawId);
//         }
//         linksData.push({ source: nodeRawId, target: edgeNodeId });
//       });
//     });

//     return { nodes: nodesData, links: linksData };
//   }, [hypergraph]);

//   // 修改：大幅增加排斥力，让节点散开，并增加阻尼让它尽快稳定
//   useEffect(() => {
//     if (open && fgRef.current) {
//       fgRef.current.d3Force('charge').strength(-1500);
//       fgRef.current.d3Force('link').distance(110);
//       fgRef.current.d3VelocityDecay(0.3);
//     }
//   }, [open, graphData]);

//   useEffect(() => {
//     if (!open) return undefined;
//     const previousOverflow = document.body.style.overflow;
//     document.body.style.overflow = 'hidden';

//     const handleKeyDown = (event) => {
//       if (event.key === 'Escape') onClose?.();
//     };

//     window.addEventListener('keydown', handleKeyDown);
//     return () => {
//       document.body.style.overflow = previousOverflow;
//       window.removeEventListener('keydown', handleKeyDown);
//     };
//   }, [open, onClose]);

//   if (!open) return null;

//   const renderProjectStageFlow = () => {
//     if (!projectStageFlow) return null;

//     const stages = Object.values(projectStageFlow.stages || {}).sort((a, b) => (a.index || 0) - (b.index || 0));
//     const currentStage = stages.find((item) => item.id === projectStageFlow.current_stage_id) || stages[0];
//     const anchorStatus = currentStage?.anchor_status || {};
//     const gate = projectStageFlow?.current_stage_gate || {};
//     const blockers = gate?.blocked_reasons || [];

//     return (
//       <div className="space-y-4">
//         <div className="bg-amber-50 border border-amber-100 rounded-xl p-4 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
//           <div className="flex-1">
//             <div className="text-xs font-bold text-amber-600 mb-1">当前阶段</div>
//             <div className="text-base font-bold text-slate-800">
//               第{projectStageFlow.current_stage_index}阶段【{projectStageFlow.current_stage_label}】
//             </div>
//             <div className="text-sm text-slate-600 mt-1 leading-relaxed">
//               {currentStage?.goal || currentStage?.coach_hint || projectStageFlow.current_stage_entry_message || '系统将优先围绕当前阶段推进。'}
//             </div>
//             <div className="text-[11px] font-medium text-amber-800 mt-2 bg-amber-100/50 px-2 py-1 rounded inline-block">
//               🎯 进度算法：(已通关规则权重和 ÷ 本阶段考核总权重) × 100 + 真实调研证据加分
//             </div>
//           </div>

//           {/* 修改：百分比块瘦身，突出数字 */}
//           <div className="rounded-2xl bg-white border border-amber-200 px-5 py-3 shrink-0 text-center flex flex-col items-center justify-center shadow-sm">
//             <div className="text-[10px] text-amber-600 font-bold mb-1">阶段进度</div>
//             <div className="text-4xl font-black text-amber-600 leading-none">
//               {currentStage?.progress_pct ?? 0}<span className="text-lg font-bold ml-0.5">%</span>
//             </div>
//             <div className="text-[10px] text-slate-500 mt-1 font-semibold">及格线 {currentStage?.pass_threshold ?? 80}%</div>
//           </div>
//         </div>

//         {projectStageFlow.milestone_message && (
//           <div className="rounded-xl bg-white border border-amber-200 p-3 text-sm text-amber-700">
//             🎉 {projectStageFlow.milestone_message}
//           </div>
//         )}

//         <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
//           {stages.map((stage) => {
//             const active = stage.status === 'current';
//             const passed = stage.status === 'passed';
//             return (
//               <div key={stage.id} className={`rounded-xl border p-3 ${passed ? 'bg-emerald-50 border-emerald-100' : active ? 'bg-orange-50 border-orange-100' : 'bg-slate-50 border-slate-200'}`}>
//                 <div className={`text-xs font-bold mb-1 ${passed ? 'text-emerald-600' : active ? 'text-orange-600' : 'text-slate-500'}`}>
//                   {stage.short_label || `第${stage.index}阶段`}
//                 </div>
//                 <div className="font-semibold text-slate-800 text-sm mb-1">{stage.label}</div>
//                 <div className="text-xs text-slate-500">进度 {stage.progress_pct ?? 0}%</div>
//                 <div className="mt-2 w-full h-1.5 rounded-full bg-white/70 border border-white/40 overflow-hidden">
//                   <div className={`h-full ${passed ? 'bg-emerald-500' : active ? 'bg-orange-500' : 'bg-slate-300'}`} style={{ width: `${Math.min(stage.progress_pct ?? 0, 100)}%` }}></div>
//                 </div>
//               </div>
//             );
//           })}
//         </div>

//         <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
//           <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
//             <div className="text-sm font-bold text-slate-800 mb-2">本轮结构锚点</div>
//             <div className="space-y-2">
//               {(anchorStatus.groups || []).map((group) => (
//                 <div key={group.label} className={`rounded-lg border px-3 py-2 text-sm ${group.passed ? 'bg-emerald-50 border-emerald-100 text-emerald-700' : 'bg-red-50 border-red-100 text-red-700'}`}>
//                   <div className="font-semibold">{group.label}</div>
//                   <div className="text-xs mt-1">
//                     {group.passed ? `已识别：${(group.matched_keys || []).join(' / ')}` : `仍缺关键表达：${(group.required_keys || []).join(' / ')}`}
//                   </div>
//                 </div>
//               ))}
//             </div>
//           </div>

//           <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
//             <div className="text-sm font-bold text-slate-800 mb-2">本轮推荐追问</div>
//             {stageFollowups.length > 0 ? (
//               <ul className="space-y-2">
//                 {stageFollowups.slice(0, 3).map((item, idx) => (
//                   <li key={`${item.rule_id}-${idx}`} className="rounded-lg bg-slate-50 border border-slate-100 px-3 py-2 text-sm text-slate-700 leading-relaxed">
//                     <span className="font-semibold text-orange-600 mr-1">[{item.rule_id}]</span>
//                     {item.question}
//                   </li>
//                 ))}
//               </ul>
//             ) : (
//               <div className="text-sm text-slate-500">当前阶段暂无额外追问建议。</div>
//             )}
//           </div>
//         </div>
//       </div>
//     );
//   };

//   const renderStageRules = () => {
//     if (!projectStageFlow) return null;

//     const stages = Object.values(projectStageFlow.stages || {}).sort((a, b) => (a.index || 0) - (b.index || 0));
//     const currentStage = stages.find((item) => item.id === projectStageFlow.current_stage_id) || stages[0];
//     if (!currentStage) return null;

//     const allRuleIds = currentStage.rule_ids || [];
//     const resolvedRuleIds = currentStage.resolved_rule_ids || [];
//     const activeAlerts = currentStage.active_alerts || [];
//     const topologyAlertMap = (structuralActiveAlerts || []).reduce((acc, alert) => {
//       if (alert?.rule) acc[alert.rule] = alert;
//       return acc;
//     }, {});
//     const stageSemanticRuleIds = allRuleIds.filter((ruleId) => structuralResolvedRuleIds.includes(ruleId) && semanticEdgeQuality?.[ruleId]);
//     const stageSemanticSummary = {
//       riskyCount: stageSemanticRuleIds.filter((ruleId) => ['contradictory', 'suspicious'].includes(semanticEdgeQuality?.[ruleId]?.worst_status)).length,
//       needsEvidenceCount: stageSemanticRuleIds.filter((ruleId) => semanticEdgeQuality?.[ruleId]?.worst_status === 'needs_evidence').length,
//       confirmedCount: stageSemanticRuleIds.filter((ruleId) => semanticEdgeQuality?.[ruleId]?.worst_status === 'confirmed').length,
//     };

//     if (allRuleIds.length === 0) {
//       return (
//         <div className="py-12 text-center text-slate-400 bg-white rounded-b-xl">
//           <ShieldAlert size={36} className="mx-auto mb-3 opacity-20" />
//           <p className="text-sm">太棒了！本阶段暂无需要考核的专项规则。</p>
//         </div>
//       );
//     }

//     return (
//       <div className="space-y-4 p-4 bg-slate-50 max-h-[520px] overflow-y-auto rounded-b-xl">
//         <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
//           <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-3 mb-3">
//             <div>
//               <div className="text-sm font-bold text-slate-800">本阶段考核规则（先结构判定，后语义复核）</div>
//               <div className="text-xs text-slate-500 mt-1">仅显示当前阶段对应规则。系统会先判断规则对应的超边结构是否达成；这里的“结构达成”以拓扑关系是否通过为准。若标准字段表达还不够完整，系统会额外给出“字段完备度提示”，但不会直接否掉结构判定。只有结构先达成的规则，才继续进入语义复核。语义区会区分展示“结构命中字段”和“复核字段对”：前者表示本条规则在当前材料中已命中的相关结构字段，后者表示系统用于语义复核的核心字段对。语义“待补证”不会取消“已突破”，语义“存疑/冲突”会取消“已突破”。</div>
//             </div>
//             <div className="flex flex-wrap gap-2 text-xs">
//               <span className="px-2 py-1 rounded-full border border-red-200 bg-red-50 text-red-700 font-semibold">语义存疑 {stageSemanticSummary.riskyCount}</span>
//               <span className="px-2 py-1 rounded-full border border-amber-200 bg-amber-50 text-amber-700 font-semibold">待补证 {stageSemanticSummary.needsEvidenceCount}</span>
//               <span className="px-2 py-1 rounded-full border border-emerald-200 bg-emerald-50 text-emerald-700 font-semibold">语义通过 {stageSemanticSummary.confirmedCount}</span>
//             </div>
//           </div>

//           <div className="space-y-3">
//             {allRuleIds.map((ruleId) => {
//               const isPassed = resolvedRuleIds.includes(ruleId);
//               const activeAlert = activeAlerts.find((a) => a.rule === ruleId);
//               const structuralAlert = topologyAlertMap?.[ruleId] || null;
//               const structuralFieldNote = (structuralFieldNotes || []).find((item) => item?.rule === ruleId) || null;
//               const structurallyPassed = structuralResolvedRuleIds.includes(ruleId);
//               const meta = RULE_METADATA[ruleId] || { name: `规则 ${ruleId}`, severity: 'medium', weight: 10 };
//               const ruleSemanticItems = (semanticChecks || []).filter((item) => item?.rule_id === ruleId);
//               const ruleSemanticQuality = structurallyPassed ? (semanticEdgeQuality?.[ruleId] || null) : null;
//               const semanticUi = ruleSemanticQuality ? getSemanticStatusMeta(ruleSemanticQuality?.worst_status || 'unknown') : null;
//               const blockedBySemantic = structurallyPassed && !isPassed && ['contradictory', 'suspicious'].includes(ruleSemanticQuality?.worst_status);
//               const blockedByStructure = !structurallyPassed;

//               const sevMap = {
//                 critical: { label: `规则等级：高危（权重:${meta.weight}）`, color: isPassed ? 'text-emerald-700 bg-emerald-100 border-emerald-200' : 'text-red-700 bg-red-100 border-red-200' },
//                 high: { label: `规则等级：高风险（权重:${meta.weight}）`, color: isPassed ? 'text-emerald-700 bg-emerald-100 border-emerald-200' : 'text-orange-700 bg-orange-100 border-orange-200' },
//                 medium: { label: `规则等级：中风险（权重:${meta.weight}）`, color: isPassed ? 'text-emerald-700 bg-emerald-100 border-emerald-200' : 'text-amber-700 bg-amber-100 border-amber-200' },
//               };
//               const sev = sevMap[meta.severity] || sevMap.medium;

//               return (
//                 <div key={ruleId} className={`border rounded-xl p-3 shadow-sm transition-all ${isPassed ? 'bg-emerald-50/50 border-emerald-200' : 'bg-white border-red-200'}`}>
//                   <div className="flex flex-wrap items-start justify-between gap-4">
//                     <div className="flex items-center gap-2">
//                       {isPassed ? <CheckCircle size={16} className="text-emerald-500" /> : <AlertTriangle size={16} className="text-red-500" />}
//                       <span className="font-mono font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded text-xs border border-slate-200">{ruleId}</span>
//                       <h6 className={`font-bold text-sm ${isPassed ? 'text-emerald-800' : 'text-slate-800'}`}>{meta.name}</h6>
//                     </div>
//                     <div className="flex flex-wrap gap-2">
//                       <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${sev.color}`}>{sev.label}</span>
//                       {semanticUi && (
//                         <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${semanticUi.badge}`}>{semanticUi.label}</span>
//                       )}
//                     </div>
//                   </div>

//                   {blockedByStructure && structuralAlert && (
//                     <p className="mt-2 text-sm text-slate-600 leading-relaxed bg-red-50/60 p-2.5 rounded-lg border border-red-100">
//                       <span className="font-semibold text-red-700">结构判定未通过：</span>{structuralAlert.issue}
//                     </p>
//                   )}

//                   {structurallyPassed && structuralFieldNote && (
//                     <p className="mt-2 text-sm text-slate-600 leading-relaxed bg-amber-50/70 p-2.5 rounded-lg border border-amber-200">
//                       <span className="font-semibold text-amber-700">字段完备度提示：</span>{structuralFieldNote.issue}
//                     </p>
//                   )}

//                   {blockedBySemantic && activeAlert && (
//                     <p className="mt-2 text-sm text-slate-600 leading-relaxed bg-red-50/60 p-2.5 rounded-lg border border-red-100">
//                       <span className="font-semibold text-red-700">结构已达成，但语义复核未通过：</span>{activeAlert.issue}
//                     </p>
//                   )}

//                   {structurallyPassed && ruleSemanticItems.length > 0 && (
//                     <div className={`mt-3 rounded-xl border p-3 ${semanticUi?.card || 'border-slate-200 bg-slate-50'}`}>
//                       <div className="flex items-center justify-between gap-3 mb-2">
//                         <div className="text-xs font-bold text-slate-700">对应超边语义复核</div>
//                         <div className="text-[11px] text-slate-500">只对已通过结构判定的规则继续复核语义是否成立</div>
//                       </div>
//                       <div className="space-y-2">
//                         {ruleSemanticItems.map((item) => {
//                           const itemUi = getSemanticStatusMeta(item?.status);
//                           return (
//                             <div key={item.id} className="rounded-lg border border-white/80 bg-white/80 px-3 py-2">
//                               <div className="flex flex-wrap items-start justify-between gap-3">
//                                 <div>
//                                   <div className="text-[11px] font-bold text-slate-500 mb-1">{formatSemanticDimension(item.dimension)}</div>
//                                   <div className="text-sm font-semibold text-slate-800 leading-relaxed">
//                                     {formatNodeName(item.left_key)}：{item.left_value} <span className="text-slate-400 mx-1">×</span> {formatNodeName(item.right_key)}：{item.right_value}
//                                   </div>
//                                 </div>
//                                 <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${itemUi.badge}`}>{itemUi.label}</span>
//                               </div>
//                               <div className="mt-2 text-sm text-slate-700 leading-relaxed">{item.reason}</div>
//                               {Array.isArray(item.structural_hit_fields) && item.structural_hit_fields.length > 0 && (
//                                 <div className="mt-2 text-xs text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg px-2.5 py-2">
//                                   <span className="font-semibold text-indigo-700">结构命中字段：</span>
//                                   {item.structural_hit_fields.join('；')}
//                                 </div>
//                               )}
//                               <div className="mt-2 text-xs text-violet-700 bg-violet-50 border border-violet-200 rounded-lg px-2.5 py-2">
//                                 <span className="font-semibold text-violet-700">复核字段对：</span>
//                                 {formatNodeName(item.left_key)}：{item.left_value} × {formatNodeName(item.right_key)}：{item.right_value}
//                               </div>
//                               {item.evidence_hint && (
//                                 <div className="mt-2 text-xs text-slate-600 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-2">
//                                   <span className="font-semibold text-slate-700">建议补证：</span>{item.evidence_hint}
//                                 </div>
//                               )}
//                             </div>
//                           );
//                         })}
//                       </div>
//                     </div>
//                   )}

//                   {isPassed && semanticUi?.label === '待补证' && (
//                     <p className="mt-2 text-xs text-amber-700 font-semibold flex items-center gap-1">✓ 该规则已通过结构判定；当前语义结论为“待补证”，仍计入“已突破”</p>
//                   )}
//                   {isPassed && semanticUi?.label === '语义通过' && (
//                     <p className="mt-2 text-xs text-emerald-600 font-semibold flex items-center gap-1">✓ 该规则已通过结构判定，且语义复核通过；当前计入“已突破”</p>
//                   )}
//                   {isPassed && !semanticUi && (
//                     <p className="mt-2 text-xs text-emerald-600 font-semibold flex items-center gap-1">✓ 该规则属于结构性规则，当前按结构判定计入“已突破”</p>
//                   )}
//                   {blockedBySemantic && semanticUi && (
//                     <p className="mt-2 text-xs text-red-600 font-semibold flex items-center gap-1">✕ 该规则虽然已通过结构判定，但语义结论为“{semanticUi.label}”，因此当前不计入“已突破”</p>
//                   )}
//                   {blockedByStructure && (
//                     <p className="mt-2 text-xs text-slate-500">该规则当前仍停留在结构判定阶段；只有先满足对应超边结构要求，才会继续触发语义复核。</p>
//                   )}
//                 </div>
//               );
//             })}
//           </div>
//         </div>
//       </div>
//     );
//   };

//   const renderHypergraph = () => {
//     const topologyModel = buildTopologyModel({ hypergraph, projectStageFlow, formatNodeName, semanticEdgeQuality });
//     const lanes = topologyModel.lanes || [];

//     if (lanes.length === 0) {
//       return (
//         <div className="py-12 bg-white rounded-b-xl text-center">
//           <p className="text-sm text-slate-400">暂未提取到可用于阶段网图与关联矩阵的拓扑数据。</p>
//         </div>
//       );
//     }

//     const currentStageId = projectStageFlow?.current_stage_id || lanes[0]?.id || 'all';
//     const activeStageId = topologyStageFilter || currentStageId || 'all';
//     const visibleLanes = activeStageId === 'all' ? lanes : lanes.filter((lane) => lane.id === activeStageId);

//     const selectedRule = selectedTopologyRule ? topologyModel.ruleMap[selectedTopologyRule] : null;
//     const selectedConcept = selectedTopologyConcept ? topologyModel.conceptMap[selectedTopologyConcept] : null;

//     let highlightedRuleIds = new Set();
//     let highlightedTopicIds = new Set();
//     let highlightedConceptIds = new Set();

//     if (selectedRule && selectedConcept) {
//       const conceptIds = new Set(topologyModel.ruleToConcepts[selectedRule.id] || []);
//       if (conceptIds.has(selectedConcept.id)) {
//         highlightedRuleIds = new Set([selectedRule.id]);
//         highlightedConceptIds = new Set([selectedConcept.id]);
//         highlightedTopicIds = new Set(
//           (topologyModel.ruleToTopics[selectedRule.id] || []).filter((topicId) =>
//             (topologyModel.topicMap[topicId]?.conceptIds || []).includes(selectedConcept.id)
//           )
//         );
//       } else {
//         highlightedRuleIds = new Set([selectedRule.id]);
//         highlightedConceptIds = new Set([selectedConcept.id]);
//       }
//     } else if (selectedRule) {
//       highlightedRuleIds = new Set([selectedRule.id]);
//       highlightedTopicIds = new Set(topologyModel.ruleToTopics[selectedRule.id] || []);
//       highlightedConceptIds = new Set(topologyModel.ruleToConcepts[selectedRule.id] || []);
//     } else if (selectedConcept) {
//       highlightedConceptIds = new Set([selectedConcept.id]);
//       highlightedRuleIds = new Set(topologyModel.conceptToRules[selectedConcept.id] || []);
//       highlightedTopicIds = new Set(topologyModel.conceptToTopics[selectedConcept.id] || []);
//     }

//     const hasFocus = highlightedRuleIds.size > 0 || highlightedConceptIds.size > 0 || highlightedTopicIds.size > 0;

//     const laneWidth = visibleLanes.length === 1 ? 1100 : visibleLanes.length === 2 ? 540 : 360;
//     const laneGap = 18;
//     const outerPadding = 16;
//     const baseTop = 104;
//     const rowGapRule = 54;
//     const rowGapTopic = 54;
//     const rowGapConcept = 46;

//     const laneHeights = visibleLanes.map((lane) => {
//       const rowCount = Math.max(lane.rules.length, lane.topics.length, lane.concepts.length, 4);
//       return Math.max(360, baseTop + rowCount * Math.max(rowGapRule, rowGapConcept) + 24);
//     });
//     const svgHeight = Math.max(...laneHeights, 420);
//     const svgWidth = outerPadding * 2 + visibleLanes.length * laneWidth + Math.max(0, visibleLanes.length - 1) * laneGap;

//     const positions = { rules: {}, topics: {}, concepts: {} };

//     visibleLanes.forEach((lane, laneIndex) => {
//       const laneX = outerPadding + laneIndex * (laneWidth + laneGap);
//       const ruleX = laneX + Math.max(70, laneWidth * 0.16);
//       const topicX = laneX + laneWidth * 0.50;
//       const conceptX = laneX + laneWidth * 0.82;

//       lane.rules.forEach((rule, idx) => {
//         positions.rules[rule.id] = { x: ruleX, y: baseTop + idx * rowGapRule };
//       });
//       lane.topics.forEach((topic, idx) => {
//         positions.topics[topic.id] = { x: topicX, y: baseTop + idx * rowGapTopic };
//       });
//       lane.concepts.forEach((concept, idx) => {
//         positions.concepts[`${lane.id}::${concept.id}`] = { x: conceptX, y: baseTop + idx * rowGapConcept };
//       });
//     });

//     const linkOpacity = (type, sourceId, targetId) => {
//       if (!hasFocus) return type === 'topic-concept' ? 0.35 : 0.48;
//       if (type === 'rule-topic') {
//         return highlightedRuleIds.has(sourceId) && highlightedTopicIds.has(targetId) ? 0.88 : 0.08;
//       }
//       const conceptRawId = targetId.split('::').slice(1).join('::');
//       return highlightedTopicIds.has(sourceId) && highlightedConceptIds.has(conceptRawId) ? 0.82 : 0.06;
//     };

//     const rowRules = visibleLanes.flatMap((lane) => lane.rules);
//     const matrixConceptIds = uniqueOrdered(
//       rowRules.flatMap((rule) => topologyModel.ruleToConcepts[rule.id] || [])
//     ).sort((a, b) => (topologyModel.conceptFrequency[b] || 0) - (topologyModel.conceptFrequency[a] || 0));

//     const cappedMatrixConceptIds = matrixConceptIds.slice(0, activeStageId === 'all' ? 12 : 14);
//     const hiddenMatrixCount = Math.max(0, matrixConceptIds.length - cappedMatrixConceptIds.length);

//     const getRulePillStyle = (rule) => {
//       const semanticStatus = rule?.semanticQuality?.worst_status || 'unknown';
//       if (rule.status === 'resolved') {
//         return { fill: '#ecfdf5', stroke: '#34d399', text: '#047857', badge: semanticStatus === 'confirmed' ? '结构+语义通过' : (semanticStatus === 'needs_evidence' ? '结构通过·待补证' : '结构通过') };
//       }
//       if (rule.status === 'locked') {
//         return { fill: '#f8fafc', stroke: '#cbd5e1', text: '#94a3b8', badge: '未解锁' };
//       }
//       if (rule.status === 'active') {
//         if (semanticStatus === 'contradictory' || semanticStatus === 'suspicious') return { fill: '#fff1f2', stroke: '#fb7185', text: '#be123c', badge: '语义存疑' };
//         if (semanticStatus === 'needs_evidence') return { fill: '#fffbeb', stroke: '#f59e0b', text: '#b45309', badge: '待补证' };
//         if (rule.severity === 'critical') return { fill: '#fff1f2', stroke: '#fb7185', text: '#be123c', badge: '结构未过' };
//         if (rule.severity === 'high') return { fill: '#fff7ed', stroke: '#fb923c', text: '#c2410c', badge: '结构未过' };
//         return { fill: '#fffbeb', stroke: '#f59e0b', text: '#b45309', badge: '结构未过' };
//       }
//       if (semanticStatus === 'confirmed') return { fill: '#ecfeff', stroke: '#67e8f9', text: '#0f766e', badge: '语义通过' };
//       return { fill: '#eff6ff', stroke: '#93c5fd', text: '#1d4ed8', badge: '观察中' };
//     };

//     const getTopicStyle = (topic) => {
//       const hasActiveOwner = topic.ownerRuleIds.some((ruleId) => topologyModel.ruleMap[ruleId]?.status === 'active');
//       if (!topic.hasData) return { fill: '#ffffff', stroke: '#cbd5e1', text: '#94a3b8' };
//       if (hasActiveOwner) return { fill: '#fff7ed', stroke: '#fdba74', text: '#b45309' };
//       return { fill: '#ffffff', stroke: '#a5b4fc', text: '#4f46e5' };
//     };

//     const getConceptStyle = (conceptId) => {
//       const ownerRules = topologyModel.conceptToRules[conceptId] || [];
//       const hasActiveOwner = ownerRules.some((ruleId) => topologyModel.ruleMap[ruleId]?.status === 'active');
//       const hasResolvedOwner = ownerRules.some((ruleId) => topologyModel.ruleMap[ruleId]?.status === 'resolved');
//       if (hasActiveOwner) return { fill: '#fff7ed', stroke: '#fdba74', text: '#9a3412' };
//       if (hasResolvedOwner) return { fill: '#ecfdf5', stroke: '#86efac', text: '#166534' };
//       return { fill: '#f8fafc', stroke: '#cbd5e1', text: '#475569' };
//     };

//     const renderNodeLabel = (text, maxLength = 10) => {
//       if (!text) return '';
//       return text.length > maxLength ? `${text.slice(0, maxLength)}…` : text;
//     };

//     const ruleDetail = selectedRule ? topologyModel.ruleMap[selectedRule.id] : null;
//     const conceptDetail = selectedConcept ? topologyModel.conceptMap[selectedConcept.id] : null;

//     return (
//       <div className="bg-white rounded-b-xl">
//         <div className="border-b border-slate-200 px-4 py-3 bg-slate-50/70">
//           <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
//             <div>
//               <div className="text-sm font-bold text-slate-800">三阶段分层网图 + 规则 × 概念关联矩阵</div>
//               <div className="text-xs text-slate-500 mt-1">
//                 将“阶段—规则—逻辑主题—文档概念”拆开显示；上方看结构，下方看覆盖密度。
//               </div>
//             </div>
//             <div className="flex flex-wrap gap-2">
//               <button
//                 type="button"
//                 onClick={() => {
//                   setTopologyStageFilter('all');
//                   setSelectedTopologyRule('');
//                   setSelectedTopologyConcept('');
//                 }}
//                 className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-colors ${activeStageId === 'all' ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}`}
//               >
//                 全阶段总览
//               </button>
//               {lanes.map((lane) => (
//                 <button
//                   key={lane.id}
//                   type="button"
//                   onClick={() => {
//                     setTopologyStageFilter(lane.id);
//                     setSelectedTopologyRule('');
//                     setSelectedTopologyConcept('');
//                   }}
//                   className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-colors ${activeStageId === lane.id ? 'text-white border-transparent' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}`}
//                   style={activeStageId === lane.id ? { backgroundColor: lane.accent.header } : undefined}
//                 >
//                   第{lane.index}阶段 · {lane.progress}%
//                 </button>
//               ))}
//             </div>
//           </div>
//         </div>

//         <div className="p-4 space-y-4">
//           <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_320px] gap-4">
//             <div className="rounded-2xl border border-slate-200 overflow-hidden bg-white">
//               <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-slate-200 bg-white">
//                 <div className="text-sm font-bold text-slate-800">阶段分层网图</div>
//                 <div className="flex flex-wrap gap-2 text-[11px]">
//                   <span className="inline-flex items-center gap-1 rounded-full bg-red-50 text-red-700 border border-red-100 px-2 py-1">高危 / 待修</span>
//                   <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100 px-2 py-1">已突破</span>
//                   <span className="inline-flex items-center gap-1 rounded-full bg-slate-50 text-slate-500 border border-slate-200 px-2 py-1">未解锁 / 无数据</span>
//                 </div>
//               </div>
//               <div className="overflow-auto bg-slate-50/60">
//                 <svg width={svgWidth} height={svgHeight} className="block min-w-full">
//                   {visibleLanes.map((lane, laneIndex) => {
//                     const laneX = outerPadding + laneIndex * (laneWidth + laneGap);
//                     const laneRectHeight = laneHeights[laneIndex] - 16;
//                     const laneCurrent = currentStageId === lane.id;
//                     return (
//                       <g key={lane.id}>
//                         <rect x={laneX} y={12} width={laneWidth} height={laneRectHeight} rx={20} fill={lane.accent.bg} stroke={laneCurrent ? lane.accent.header : lane.accent.border} strokeWidth={laneCurrent ? 2.2 : 1.2} />
//                         <rect x={laneX + 1} y={13} width={laneWidth - 2} height={44} rx={18} fill={lane.accent.soft} stroke="none" />
//                         <text x={laneX + 18} y={40} fontSize="15" fontWeight="700" fill={lane.accent.muted}>第{lane.index}阶段 · {lane.label}</text>
//                         <text x={laneX + laneWidth - 18} y={40} textAnchor="end" fontSize="12" fontWeight="700" fill={lane.accent.header}>{lane.progress}% / {lane.passThreshold}%</text>
//                         <text x={laneX + Math.max(70, laneWidth * 0.16)} y={80} textAnchor="middle" fontSize="11" fontWeight="700" fill="#64748b">规则</text>
//                         <text x={laneX + laneWidth * 0.50} y={80} textAnchor="middle" fontSize="11" fontWeight="700" fill="#64748b">逻辑主题</text>
//                         <text x={laneX + laneWidth * 0.82} y={80} textAnchor="middle" fontSize="11" fontWeight="700" fill="#64748b">文档概念</text>
//                       </g>
//                     );
//                   })}

//                   {visibleLanes.map((lane) =>
//                     lane.rules.flatMap((rule) => {
//                       const source = positions.rules[rule.id];
//                       if (!source) return [];
//                       return (topologyModel.ruleToTopics[rule.id] || []).filter((topicId) => positions.topics[topicId]).map((topicId) => {
//                         const target = positions.topics[topicId];
//                         const opacity = linkOpacity('rule-topic', rule.id, topicId);
//                         return <path key={`rule-topic-${rule.id}-${topicId}`} d={`M ${source.x + 54} ${source.y} C ${source.x + 100} ${source.y}, ${target.x - 70} ${target.y}, ${target.x - 48} ${target.y}`} fill="none" stroke={rule.status === 'resolved' ? '#34d399' : '#cbd5e1'} strokeWidth={rule.status === 'resolved' ? 2.2 : 1.8} strokeOpacity={opacity} strokeLinecap="round" />;
//                       });
//                     })
//                   )}

//                   {visibleLanes.map((lane) =>
//                     lane.topics.flatMap((topic) => {
//                       const source = positions.topics[topic.id];
//                       if (!source) return [];
//                       return (topic.conceptIds || []).filter((conceptId) => positions.concepts[`${lane.id}::${conceptId}`]).map((conceptId) => {
//                         const target = positions.concepts[`${lane.id}::${conceptId}`];
//                         const opacity = linkOpacity('topic-concept', topic.id, `${lane.id}::${conceptId}`);
//                         return <path key={`topic-concept-${topic.id}-${conceptId}`} d={`M ${source.x + 52} ${source.y} C ${source.x + 100} ${source.y}, ${target.x - 82} ${target.y}, ${target.x - 50} ${target.y}`} fill="none" stroke="#94a3b8" strokeWidth={1.6} strokeOpacity={opacity} strokeLinecap="round" strokeDasharray={topic.hasData ? '0' : '5 5'} />;
//                       });
//                     })
//                   )}

//                   {visibleLanes.map((lane) =>
//                     lane.rules.map((rule) => {
//                       const pos = positions.rules[rule.id];
//                       if (!pos) return null;
//                       const style = getRulePillStyle(rule);
//                       const isFocused = !hasFocus || highlightedRuleIds.has(rule.id);
//                       return (
//                         <g key={`rule-${rule.id}`} transform={`translate(${pos.x}, ${pos.y})`} onClick={() => { setSelectedTopologyRule((prev) => (prev === rule.id ? '' : rule.id)); setSelectedTopologyConcept(''); }} className="cursor-pointer" opacity={isFocused ? 1 : 0.34}>
//                           <title>{`${rule.id} · ${rule.label}${rule.issue ? `
// ${rule.issue}` : ''}`}</title>
//                           <rect x={-56} y={-17} width={112} height={34} rx={17} fill={style.fill} stroke={style.stroke} strokeWidth={selectedTopologyRule === rule.id ? 2.8 : 1.8} />
//                           <text textAnchor="middle" dominantBaseline="middle" fontSize="11.5" fontWeight="700" fill={style.text}>{rule.id}</text>
//                           <text textAnchor="middle" y={23} fontSize="10.5" fontWeight="700" fill={style.text}>{style.badge}</text>
//                         </g>
//                       );
//                     })
//                   )}

//                   {visibleLanes.map((lane) =>
//                     lane.topics.map((topic) => {
//                       const pos = positions.topics[topic.id];
//                       if (!pos) return null;
//                       const style = getTopicStyle(topic);
//                       const isFocused = !hasFocus || highlightedTopicIds.has(topic.id);
//                       return (
//                         <g key={`topic-${topic.id}`} transform={`translate(${pos.x}, ${pos.y})`} onClick={() => { const ownerRule = topic.ownerRuleIds?.[0] || ''; setSelectedTopologyRule((prev) => (prev === ownerRule ? '' : ownerRule)); setSelectedTopologyConcept(''); }} className="cursor-pointer" opacity={isFocused ? 1 : 0.38}>
//                           <title>{`${topic.label}${topic.hasData ? '' : `\n当前文档尚未抽取到该主题下的明确概念`}`}</title>
//                           <rect x={-58} y={-16} width={116} height={32} rx={12} fill={style.fill} stroke={style.stroke} strokeWidth={selectedTopologyRule && topic.ownerRuleIds.includes(selectedTopologyRule) ? 2.4 : 1.6} />
//                           <text textAnchor="middle" dominantBaseline="middle" fontSize="11" fontWeight="700" fill={style.text}>{renderNodeLabel(topic.label, 8)}</text>
//                         </g>
//                       );
//                     })
//                   )}

//                   {visibleLanes.map((lane) =>
//                     lane.concepts.map((concept) => {
//                       const pos = positions.concepts[`${lane.id}::${concept.id}`];
//                       if (!pos) return null;
//                       const style = getConceptStyle(concept.id);
//                       const isFocused = !hasFocus || highlightedConceptIds.has(concept.id);
//                       return (
//                         <g key={`concept-${lane.id}-${concept.id}`} transform={`translate(${pos.x}, ${pos.y})`} onClick={() => { setSelectedTopologyConcept((prev) => (prev === concept.id ? '' : concept.id)); if (selectedTopologyRule && !(topologyModel.ruleToConcepts[selectedTopologyRule] || []).includes(concept.id)) { setSelectedTopologyRule(''); } }} className="cursor-pointer" opacity={isFocused ? 1 : 0.36}>
//                           <title>{concept.fullLabel}</title>
//                           <rect x={-62} y={-15} width={124} height={30} rx={10} fill={style.fill} stroke={style.stroke} strokeWidth={selectedTopologyConcept === concept.id ? 2.4 : 1.4} />
//                           <text textAnchor="middle" dominantBaseline="middle" fontSize="11" fontWeight="600" fill={style.text}>{renderNodeLabel(concept.fullLabel, 9)}</text>
//                         </g>
//                       );
//                     })
//                   )}
//                 </svg>
//               </div>
//               <div className="px-4 py-3 border-t border-slate-200 bg-slate-50 text-xs text-slate-500 flex flex-wrap gap-x-4 gap-y-1">
//                 <span>点击规则节点：聚焦该规则影响的主题与概念</span>
//                 <span>点击概念节点：反查它被哪些规则反复命中</span>
//                 <span>阶段切换：查看单阶段或全阶段总览</span>
//               </div>
//             </div>

//             <div className="space-y-4">
//               <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
//                 <div className="text-sm font-bold text-slate-800 mb-3">当前聚焦说明</div>
//                 {!ruleDetail && !conceptDetail ? (
//                   <div className="text-sm text-slate-500 leading-relaxed">默认展示当前阶段的整体拓扑。可点击规则节点或矩阵单元格，查看“某条规则为什么打到某个概念”，以及它当前的语义是否通过。</div>
//                 ) : (
//                   <div className="space-y-3">
//                     {ruleDetail && (
//                       <div className="rounded-xl border border-slate-200 p-3 bg-slate-50">
//                         <div className="flex items-center justify-between gap-3 mb-2">
//                           <div className="text-sm font-bold text-slate-800">{ruleDetail.id} · {ruleDetail.label}</div>
//                           <span className={`text-[11px] font-bold px-2 py-1 rounded-full ${ruleDetail.status === 'resolved' ? 'bg-emerald-100 text-emerald-700' : ruleDetail.status === 'active' ? 'bg-orange-100 text-orange-700' : 'bg-slate-100 text-slate-600'}`}>{ruleDetail.status === 'resolved' ? '已突破' : ruleDetail.status === 'active' ? '待修' : ruleDetail.status === 'locked' ? '未解锁' : '观察中'}</span>
//                         </div>
//                         <div className="text-xs text-slate-600 leading-relaxed">{ruleDetail.issue || '当前规则没有额外的预警文本，图中主要展示其作用到的逻辑主题与文档概念。'}</div>
//                         {ruleDetail.semanticQuality && (
//                           <div className="mt-2 text-[11px] text-slate-600 leading-relaxed">语义状态：{getSemanticStatusMeta(ruleDetail.semanticQuality.worst_status).label}；涉及 {ruleDetail.semanticQuality.count || 0} 组校验，风险 {ruleDetail.semanticQuality.risky_count || 0} 组。</div>
//                         )}
//                         <div className="mt-3 text-[11px] text-slate-500 leading-relaxed">关联主题：{(ruleDetail.topicKeys || []).map((key) => formatNodeName(key)).join('、') || '暂无'}</div>
//                       </div>
//                     )}
//                     {conceptDetail && (
//                       <div className="rounded-xl border border-slate-200 p-3 bg-slate-50">
//                         <div className="text-sm font-bold text-slate-800 mb-2">概念命中：{conceptDetail.fullLabel}</div>
//                         <div className="text-xs text-slate-600 leading-relaxed">该概念目前关联 {((topologyModel.conceptToRules[conceptDetail.id] || []).length)} 条规则：{(topologyModel.conceptToRules[conceptDetail.id] || []).map((ruleId) => `${ruleId} ${topologyModel.ruleMap[ruleId]?.label || ''}`).join('、') || '暂无'}</div>
//                       </div>
//                     )}
//                     <button type="button" onClick={() => { setSelectedTopologyRule(''); setSelectedTopologyConcept(''); }} className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50">清除聚焦</button>
//                   </div>
//                 )}
//               </div>

//               <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
//                 <div className="text-sm font-bold text-slate-800 mb-3">图例</div>
//                 <div className="space-y-2 text-xs text-slate-600">
//                   <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-orange-200 border border-orange-300"></span> 当前仍阻塞的规则 / 概念</div>
//                   <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-emerald-200 border border-emerald-300"></span> 已解除或已通过的规则链</div>
//                   <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-slate-200 border border-slate-300"></span> 未来阶段或暂未抽取到数据的结构位</div>
//                   <div className="text-[11px] text-slate-500 pt-1 leading-relaxed">这不是自由散点图，而是按阶段把“规则—主题—概念”拆成三列，让学生和教师都能直接看懂逻辑链条。</div>
//                 </div>
//               </div>
//             </div>
//           </div>

//           <div className="rounded-2xl border border-slate-200 overflow-hidden bg-white shadow-sm">
//             <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-slate-200 bg-white">
//               <div>
//                 <div className="text-sm font-bold text-slate-800">规则 × 概念关联矩阵</div>
//                 <div className="text-xs text-slate-500 mt-1">纵向看规则，横向看概念；颜色越深，说明该规则越直接地命中了该概念。</div>
//               </div>
//               {hiddenMatrixCount > 0 && <div className="text-[11px] text-slate-500">为保证清晰度，已折叠其余 {hiddenMatrixCount} 个低频概念</div>}
//             </div>
//             <div className="overflow-auto">
//               <table className="min-w-full border-separate border-spacing-0 text-xs">
//                 <thead>
//                   <tr>
//                     <th className="sticky left-0 z-10 bg-white border-b border-r border-slate-200 px-3 py-3 text-left min-w-[180px] text-slate-600">规则 \ 概念</th>
//                     {cappedMatrixConceptIds.map((conceptId) => (
//                       <th key={conceptId} className="border-b border-slate-200 px-2 py-3 bg-white min-w-[88px] align-bottom">
//                         <div className="font-semibold text-slate-700 leading-tight">{renderNodeLabel(topologyModel.conceptMap[conceptId]?.fullLabel || conceptId, 12)}</div>
//                       </th>
//                     ))}
//                   </tr>
//                 </thead>
//                 <tbody>
//                   {rowRules.map((rule) => {
//                     const rowStyle = getRulePillStyle(rule);
//                     return (
//                       <tr key={`matrix-${rule.id}`}>
//                         <td className="sticky left-0 z-[1] bg-white border-r border-b border-slate-200 px-3 py-2 min-w-[180px]">
//                           <button type="button" onClick={() => { setSelectedTopologyRule((prev) => (prev === rule.id ? '' : rule.id)); setSelectedTopologyConcept(''); }} className="w-full text-left">
//                             <div className="font-bold" style={{ color: rowStyle.text }}>{rule.id}</div>
//                             <div className="text-slate-600 mt-0.5">{rule.label}</div>
//                           </button>
//                         </td>
//                         {cappedMatrixConceptIds.map((conceptId) => {
//                           const linked = (topologyModel.ruleToConcepts[rule.id] || []).includes(conceptId);
//                           const selectedPair = selectedTopologyRule === rule.id && selectedTopologyConcept === conceptId;
//                           let cellClass = 'bg-white';
//                           if (linked && rule.status === 'resolved') cellClass = 'bg-emerald-100';
//                           else if (linked && rule.status === 'active' && ['contradictory', 'suspicious'].includes(rule.semanticQuality?.worst_status)) cellClass = 'bg-red-100';
//                           else if (linked && rule.status === 'active' && rule.semanticQuality?.worst_status === 'needs_evidence') cellClass = 'bg-amber-100';
//                           else if (linked && rule.status === 'active') cellClass = rule.severity === 'critical' ? 'bg-red-100' : 'bg-orange-100';
//                           else if (linked && rule.semanticQuality?.worst_status === 'confirmed') cellClass = 'bg-emerald-50';
//                           else if (linked) cellClass = 'bg-blue-50';

//                           return (
//                             <td key={`${rule.id}-${conceptId}`} className="border-b border-slate-200 px-2 py-2 text-center">
//                               <button
//                                 type="button"
//                                 onClick={() => {
//                                   if (!linked) return;
//                                   setSelectedTopologyRule(rule.id);
//                                   setSelectedTopologyConcept(conceptId);
//                                 }}
//                                 className={`mx-auto flex h-9 w-9 items-center justify-center rounded-lg border text-[11px] font-bold transition-all ${linked ? 'cursor-pointer border-slate-200 hover:scale-105' : 'cursor-default border-slate-100 text-slate-200'} ${cellClass} ${selectedPair ? 'ring-2 ring-slate-900 ring-offset-1' : ''}`}
//                                 title={linked ? `${rule.id} ↔ ${topologyModel.conceptMap[conceptId]?.fullLabel || conceptId}` : '当前规则未直接命中该概念'}
//                               >
//                                 {linked ? '●' : '·'}
//                               </button>
//                             </td>
//                           );
//                         })}
//                       </tr>
//                     );
//                   })}
//                 </tbody>
//               </table>
//             </div>
//           </div>
//         </div>
//       </div>
//     );
//   };


//   const competitionMeta = competition?.competition_meta || {};
//   const competitionSummary = competition?.score_summary || {};
//   const competitionCharts = competition?.panel_charts || {};
//   const competitionItems = competition?.rubric_items || [];
//   const topTasks = competition?.top_tasks || [];

//   const renderCompetitionOverview = () => (
//     <div className="space-y-4">
//       <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
//         <div className="bg-purple-50 border border-purple-100 rounded-xl p-4">
//           <div className="text-xs text-purple-600 mb-1">当前赛事模板</div>
//           <div className="font-bold text-purple-800">{competitionMeta.template_name || '竞赛模式'}</div>
//           <div className="text-xs text-purple-600 mt-1">{competitionMeta.matched_alias || '系统自动识别'}</div>
//         </div>
//         <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
//           <div className="text-xs text-blue-600 mb-1">综合预估得分</div>
//           <div className="font-bold text-blue-800">{competitionSummary.weighted_score_text || '—'}</div>
//           <div className="text-xs text-blue-600 mt-1">平均单项分：{competitionSummary.average_score ?? '—'}</div>
//         </div>
//         <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
//           <div className="text-xs text-amber-600 mb-1">模板专属维度</div>
//           <div className="font-bold text-amber-800 text-sm leading-relaxed">
//             {(competitionMeta.exclusive_dimensions || []).map((item) => item.dimension_name).join(' / ') || '—'}
//           </div>
//         </div>
//         <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-4">
//           <div className="text-xs text-emerald-600 mb-1">评价重心</div>
//           <div className="font-bold text-emerald-800 text-sm leading-relaxed">{competitionMeta.focus_hint || '—'}</div>
//         </div>
//       </div>

//       <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
//         <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
//           <div className="flex items-center gap-2 mb-3 text-slate-800 font-bold text-sm"><Radar size={16} className="text-purple-600" /> Rubric 分数雷达图</div>
//           <div className="h-80">
//             <ResponsiveContainer width="100%" height="100%">
//               <RadarChart data={competitionCharts.radar || []} outerRadius="70%">
//                 <PolarGrid />
//                 <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 11 }} />
//                 <PolarRadiusAxis angle={90} domain={[0, 5]} tickCount={6} />
//                 <RechartsRadar name="Score" dataKey="score" stroke="#7c3aed" fill="#c4b5fd" fillOpacity={0.45} />
//               </RadarChart>
//             </ResponsiveContainer>
//           </div>
//         </div>

//         <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
//           <div className="flex items-center gap-2 mb-3 text-slate-800 font-bold text-sm"><BarChart3 size={16} className="text-blue-600" /> 维度权重分布</div>
//           <div className="h-80">
//             <ResponsiveContainer width="100%" height="100%">
//               <BarChart data={competitionCharts.weight_compare || []} layout="vertical" margin={{ left: 20, right: 10, top: 8, bottom: 8 }}>
//                 <CartesianGrid strokeDasharray="3 3" />
//                 <XAxis type="number" />
//                 <YAxis dataKey="dimension" type="category" width={90} tick={{ fontSize: 11 }} />
//                 <Tooltip />
//                 <Bar dataKey="weight" fill="#60a5fa" radius={[0, 4, 4, 0]} />
//               </BarChart>
//             </ResponsiveContainer>
//           </div>
//         </div>
//       </div>

//       <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//         <div className="bg-red-50 border border-red-100 rounded-xl p-4">
//           <div className="text-sm font-bold text-red-800 mb-2">高风险维度</div>
//           <div className="space-y-2">
//             {(competitionSummary.high_risk_dimensions || []).length > 0 ? (competitionSummary.high_risk_dimensions || []).map((item) => (
//               <div key={item.dimension_id} className="bg-white rounded-lg border border-red-100 px-3 py-2 text-sm text-red-700">
//                 {item.dimension_name} · {item.score}/5 · 权重 {item.weight}%
//               </div>
//             )) : <div className="text-sm text-red-600">暂无高风险维度。</div>}
//           </div>
//         </div>
//         <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
//           <div className="text-sm font-bold text-slate-800 mb-2">物理权重偏移说明</div>
//           <p className="text-sm text-slate-600 leading-relaxed">{competitionMeta.expected_shift || '—'}</p>
//           <div className="mt-3 text-xs text-slate-500">识别依据：{competitionMeta.recognition_basis || '—'}</div>
//         </div>
//       </div>
//     </div>
//   );

//   const renderCompetitionDimensions = () => (
//     <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
//       <div className="overflow-x-auto">
//         <table className="min-w-full text-sm">
//           <thead className="bg-slate-50 text-slate-700">
//             <tr>
//               <th className="px-4 py-3 text-left">维度</th>
//               <th className="px-4 py-3 text-left">类别</th>
//               <th className="px-4 py-3 text-right">权重</th>
//               <th className="px-4 py-3 text-right">分数</th>
//               <th className="px-4 py-3 text-left">缺失证据</th>
//               <th className="px-4 py-3 text-left">24h 修复</th>
//               <th className="px-4 py-3 text-left">72h 修复</th>
//             </tr>
//           </thead>
//           <tbody>
//             {competitionItems.map((item) => (
//               <tr key={item.dimension_id} className="border-t border-slate-100 align-top">
//                 <td className="px-4 py-3 font-medium text-slate-800">{item.dimension_name}</td>
//                 <td className="px-4 py-3 text-slate-500">{item.category === 'exclusive' ? '赛事专属' : '通用'}</td>
//                 <td className="px-4 py-3 text-right text-slate-600">{item.weight}%</td>
//                 <td className="px-4 py-3 text-right">
//                   <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-bold ${item.estimated_score <= 2 ? 'bg-red-100 text-red-700' : item.estimated_score < 3.5 ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}`}>
//                     {item.estimated_score}/5
//                   </span>
//                 </td>
//                 <td className="px-4 py-3 text-slate-600 whitespace-pre-wrap">{(item.missing_evidence || []).join('；') || '暂无明显缺口'}</td>
//                 <td className="px-4 py-3 text-slate-600 whitespace-pre-wrap">{item.minimal_fix_24h || '—'}</td>
//                 <td className="px-4 py-3 text-slate-600 whitespace-pre-wrap">{item.minimal_fix_72h || '—'}</td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       </div>
//     </div>
//   );

//   const renderCompetitionTasks = () => (
//     <div className="space-y-4">
//       <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//         {topTasks.map((task, idx) => (
//           <div key={`${task.task_desc}-${idx}`} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
//             <div className="font-bold text-purple-700 text-sm mb-2">{task.task_desc}</div>
//             <div className="text-xs text-slate-500 mb-2">{task.timeframe} · {task.roi_reason}</div>
//             <div className="text-sm text-slate-600 leading-relaxed">{task.template_example}</div>
//           </div>
//         ))}
//       </div>

//       <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
//         <div className="text-sm font-bold text-slate-800 mb-2">评委追问预演</div>
//         <ul className="list-disc pl-5 space-y-2 text-sm text-slate-600">
//           {(competition.quick_questions || []).map((q, idx) => <li key={`${q}-${idx}`}>{q}</li>)}
//         </ul>
//       </div>
//     </div>
//   );

//   const modeTabs = [
//     project && { id: 'project', label: '项目', icon: Briefcase, color: 'text-orange-600' },
//     competition && { id: 'competition', label: '竞赛', icon: Trophy, color: 'text-purple-600' },
//   ].filter(Boolean);

//   return (
//     <div className="fixed inset-0 z-[120]">
//       <div className="absolute inset-0 bg-slate-900/30 backdrop-blur-[1px]" onClick={() => onClose?.()} />
//       <div className="absolute inset-0 flex items-center justify-center p-4 md:p-6">
//         <div className="relative w-full max-w-6xl h-[88vh] rounded-2xl border border-amber-200 bg-white shadow-2xl overflow-hidden">
//           <div className="sticky top-0 z-10 flex items-center justify-between gap-3 border-b border-slate-200 bg-white/95 px-4 py-3 backdrop-blur">
//             <div>
//               <div className="text-sm font-bold text-slate-800">文档分析面板</div>
//               <div className="text-xs text-slate-500">项目 / 竞赛快照会随对话持续更新</div>
//             </div>
//             <button
//               type="button"
//               onClick={() => onClose?.()}
//               className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-semibold text-slate-600 hover:bg-slate-50"
//             >
//               <X size={16} /> 关闭
//             </button>
//           </div>
//           <div className="h-[calc(88vh-61px)] overflow-y-auto p-4">
//             {!project && !competition && (
//               <div className="text-sm text-amber-700">
//                 当前已绑定文档，但还没有项目模式/竞赛模式的快照数据。先运行一次对应模式，这里就会自动更新。
//               </div>
//             )}

//             {modeTabs.length > 0 && (
//               <div className="flex items-center gap-2 border-b border-slate-200 pb-3 mb-4">
//                 {modeTabs.map((tab) => {
//                   const Icon = tab.icon;
//                   const active = activeModeTab === tab.id;
//                   return (
//                     <button
//                       key={tab.id}
//                       onClick={() => setActiveModeTab(tab.id)}
//                       className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border text-sm font-semibold transition-colors ${active ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}`}
//                     >
//                       <Icon size={16} className={active ? 'text-white' : tab.color} />
//                       {tab.label}
//                     </button>
//                   );
//                 })}
//               </div>
//             )}

//             {activeModeTab === 'project' && project && (
//               <div className="space-y-4 mb-5">
//                 <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
//                   <Briefcase size={18} className="text-orange-600" />
//                   <h4 className="font-bold text-slate-800 text-base">项目模式快照</h4>
//                 </div>

//                 {renderProjectStageFlow()}

//                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//                   <div className="bg-orange-50 border border-orange-100 rounded-xl p-3 shadow-sm">
//                     <div className="text-sm font-semibold text-orange-800 mb-1">逻辑缺陷</div>
//                     <div className="text-sm text-orange-700 leading-relaxed">{project.logic_flaw || '暂无'}</div>
//                   </div>
//                   <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 shadow-sm">
//                     <div className="text-sm font-semibold text-slate-800 mb-1">证据缺口</div>
//                     <div className="text-sm text-slate-600 leading-relaxed">{project.evidence_gap || '暂无'}</div>
//                   </div>
//                 </div>

//                 <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 shadow-sm">
//                   <div className="text-sm font-bold text-emerald-800 mb-2">唯一核心突破任务</div>
//                   <div className="text-sm text-emerald-700 mb-3">{project.only_one_task || '暂无'}</div>
//                   <div className="text-xs text-emerald-900 bg-white rounded-lg p-3 border border-emerald-100 shadow-sm">
//                     <strong>验收标准：</strong> {project.acceptance_criteria || '暂无'}
//                   </div>
//                 </div>

//                 <div className="mt-6 border border-slate-200 rounded-xl overflow-hidden shadow-sm">
//                   <div className="flex border-b border-slate-200 bg-white">
//                     {/* 修改：重命名 Tab，突出阶段规则检视 */}
//                     <button
//                       onClick={() => setProjectTab('rules')}
//                       className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 transition-colors relative ${projectTab === 'rules' ? 'text-blue-600 bg-blue-50/50' : 'text-slate-500 hover:bg-slate-50'}`}
//                     >
//                       <ClipboardList size={16} /> 阶段规则检视
//                       {projectTab === 'rules' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-600" />}
//                     </button>
//                     <button
//                       onClick={() => setProjectTab('topology')}
//                       className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 transition-colors relative ${projectTab === 'topology' ? 'text-blue-600 bg-blue-50/50' : 'text-slate-500 hover:bg-slate-50'}`}
//                     >
//                       <Network size={16} /> 逻辑拓扑结构图
//                       {projectTab === 'topology' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-600" />}
//                     </button>
//                   </div>
//                   <div>{projectTab === 'rules' ? renderStageRules() : renderHypergraph()}</div>
//                 </div>
//               </div>
//             )}

//             {activeModeTab === 'competition' && competition && (
//               <div className="space-y-4">
//                 <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
//                   <Trophy size={18} className="text-purple-600" />
//                   <h4 className="font-bold text-slate-800 text-base">竞赛模式快照</h4>
//                 </div>

//                 <div className="flex flex-wrap gap-2 border border-slate-200 rounded-xl bg-slate-50 p-2">
//                   {[
//                     { id: 'overview', label: '总览', icon: Trophy },
//                     { id: 'dimensions', label: '逐项评分', icon: ClipboardList },
//                     { id: 'tasks', label: '冲刺任务', icon: BarChart3 },
//                   ].map((tab) => {
//                     const Icon = tab.icon;
//                     const active = competitionTab === tab.id;
//                     return (
//                       <button
//                         key={tab.id}
//                         onClick={() => setCompetitionTab(tab.id)}
//                         className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold transition-colors ${active ? 'bg-white text-purple-700 shadow-sm border border-purple-100' : 'text-slate-600 hover:bg-white'}`}
//                       >
//                         <Icon size={15} /> {tab.label}
//                       </button>
//                     );
//                   })}
//                 </div>

//                 {competitionTab === 'overview' && renderCompetitionOverview()}
//                 {competitionTab === 'dimensions' && renderCompetitionDimensions()}
//                 {competitionTab === 'tasks' && renderCompetitionTasks()}
//               </div>
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }







import React, { useMemo, useRef, useEffect, useState } from 'react';
import {
  Briefcase,
  Trophy,
  Network,
  AlertTriangle,
  ShieldAlert,
  BarChart3,
  Radar,
  ClipboardList,
  CheckCircle,
  X,
} from 'lucide-react';
import ForceGraph2D from 'react-force-graph-2d';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar as RechartsRadar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';

// 在前端同步后端规则的元数据配置，用于规则检视面板
const RULE_METADATA = {
  "System": { "name": "图谱元素过少", "severity": "high", "weight": 18 },
  "R1": { "name": "全局逻辑散架", "severity": "critical", "weight": 30 },
  "R2": { "name": "技术与商业双轨孤岛", "severity": "critical", "weight": 30 },
  "R3": { "name": "叙事因果断裂", "severity": "high", "weight": 18 },
  "R4": { "name": "合规逻辑游离", "severity": "medium", "weight": 10 },
  "R5": { "name": "闭环要素严重缺失", "severity": "high", "weight": 18 },
  "R6": { "name": "渠道与客群脱节", "severity": "medium", "weight": 10 },
  "R7": { "name": "支付意愿支撑不足", "severity": "high", "weight": 18 },
  "R8": { "name": "无竞争对手幻觉", "severity": "critical", "weight": 30 },
  "R9": { "name": "市场漏斗断层", "severity": "medium", "weight": 10 },
  "R10": { "name": "创新缺乏竞争对标", "severity": "medium", "weight": 10 },
  "R11": { "name": "单位经济模型崩塌", "severity": "critical", "weight": 30 },
  "R12": { "name": "利润空间黑盒", "severity": "high", "weight": 18 },
  "R13": { "name": "现金流断裂高危", "severity": "critical", "weight": 30 },
  "R14": { "name": "供应链脱离业务", "severity": "high", "weight": 18 },
  "R15": { "name": "冷启动策略空转", "severity": "medium", "weight": 10 },
  "R16": { "name": "技术壁垒无团队支撑", "severity": "medium", "weight": 10 },
  "R17": { "name": "执行方案空壳", "severity": "medium", "weight": 10 },
  "R18": { "name": "财务预测漂浮", "severity": "high", "weight": 18 },
  "R19": { "name": "频次与收入模型错配", "severity": "high", "weight": 18 },
  "R20": { "name": "公益属性过重", "severity": "medium", "weight": 10 },
};

const RULE_EDGE_BINDINGS = {
  System: ['Core_Business_Loop'],
  R1: ['Core_Business_Loop'],
  R2: ['Core_Business_Loop', 'Tech_Barrier'],
  R3: ['Narrative_Causality'],
  R4: ['Compliance_Ethics', 'Core_Business_Loop'],
  R5: ['Core_Business_Loop'],
  R6: ['Channel_Physical_Access', 'Core_Business_Loop'],
  R7: ['Willingness_To_Pay'],
  R8: ['Real_Competition'],
  R9: ['Market_Reachability'],
  R10: ['Innovation_Verification', 'Real_Competition'],
  R11: ['Unit_Economics'],
  R12: ['Pricing_Space'],
  R13: ['Cash_Flow_Health'],
  R14: ['Supply_Chain_Sync', 'Core_Business_Loop'],
  R15: ['Cold_Start_Engine', 'Core_Business_Loop'],
  R16: ['R&D_Team_Match'],
  R17: ['Resource_Feasibility'],
  R18: ['Financial_Reasonableness', 'Core_Business_Loop'],
  R19: ['Frequency_Mismatch'],
  R20: ['Social_Value_Translation', 'Core_Business_Loop'],
};

const STAGE_ACCENTS = [
  { bg: '#fff7ed', border: '#fdba74', header: '#f97316', soft: '#ffedd5', muted: '#9a3412' },
  { bg: '#eff6ff', border: '#93c5fd', header: '#2563eb', soft: '#dbeafe', muted: '#1d4ed8' },
  { bg: '#faf5ff', border: '#c4b5fd', header: '#7c3aed', soft: '#ede9fe', muted: '#6d28d9' },
];

const SEMANTIC_DIMENSION_LABELS = {
  field_type_consistency: '字段类型一致性',
  channel_customer_fit: '渠道与客群适配',
  narrative_causality: '痛点—方案因果链',
  competition_realism: '竞争分析真实性',
  market_funnel_consistency: '市场漏斗一致性',
  innovation_against_competition: '创新对标充分性',
  price_customer_fit: '定价与客群匹配',
  unit_economics: '单位经济合理性',
  pricing_space: '定价与利润空间',
  cash_flow_health: '现金流安全性',
  financial_reasonableness: '财务预测可信度',
  frequency_revenue_fit: '频次与收费匹配',
  tech_business_alignment: '技术与商业融合度',
  compliance_industry: '合规路径充分性',
  supply_chain_sync: '供应链与交付闭环',
  cold_start_engine: '冷启动起盘能力',
  team_tech_match: '团队与技术匹配',
  resource_feasibility: '资源与里程碑可行性',
  social_value_translation: '社会价值商业化转译',
};

const SEMANTIC_STATUS_META = {
  contradictory: { label: '语义冲突', badge: 'bg-red-100 text-red-700 border-red-200', card: 'border-red-200 bg-red-50/60' },
  suspicious: { label: '语义存疑', badge: 'bg-orange-100 text-orange-700 border-orange-200', card: 'border-orange-200 bg-orange-50/60' },
  needs_evidence: { label: '待补证', badge: 'bg-amber-100 text-amber-700 border-amber-200', card: 'border-amber-200 bg-amber-50/60' },
  confirmed: { label: '语义通过', badge: 'bg-emerald-100 text-emerald-700 border-emerald-200', card: 'border-emerald-200 bg-emerald-50/60' },
  unknown: { label: '未复核', badge: 'bg-slate-100 text-slate-700 border-slate-200', card: 'border-slate-200 bg-slate-50' },
};

const SEVERITY_RANK = { critical: 4, high: 3, medium: 2, low: 1 };

function uniqueOrdered(list = []) {
  return Array.from(new Set((list || []).filter(Boolean)));
}

function normalizeSeverity(value) {
  return String(value || 'medium').toLowerCase();
}

function buildTopologyModel({ hypergraph, projectStageFlow, formatNodeName, semanticEdgeQuality }) {
  const edgeMap = hypergraph?.edges || {};
  const stages = Object.values(projectStageFlow?.stages || {}).sort((a, b) => (a.index || 0) - (b.index || 0));
  const alerts = [...(hypergraph?.alerts || [])];
  const globalAlertMap = alerts.reduce((acc, alert) => {
    if (alert?.rule) acc[alert.rule] = alert;
    return acc;
  }, {});

  const parseConceptLabel = (raw) => {
    if (!raw) return '';
    let text = String(raw);
    if (text.includes(': ')) text = text.split(': ')[1];
    else if (text.includes(':')) text = text.split(':')[1];
    else if (text.includes('：')) text = text.split('：')[1];
    else text = formatNodeName(text);
    return text.trim();
  };

  const ruleMap = {};
  const conceptMap = {};
  const topicMap = {};
  const ruleToConcepts = {};
  const ruleToTopics = {};
  const conceptToRules = {};
  const conceptToTopics = {};
  const conceptFrequency = {};

  const lanes = stages.map((stage, stageIdx) => {
    const activeRuleSet = new Set(stage.active_rule_ids || []);
    const resolvedRuleSet = new Set(stage.resolved_rule_ids || []);
    const stageAlertMap = (stage.active_alerts || []).reduce((acc, alert) => {
      if (alert?.rule) acc[alert.rule] = alert;
      return acc;
    }, {});

    const ruleIds = stage.rule_ids || [];
    const rules = ruleIds.map((ruleId) => {
      const meta = RULE_METADATA[ruleId] || { name: ruleId, severity: 'medium', weight: 10 };
      const topicKeys = uniqueOrdered(RULE_EDGE_BINDINGS[ruleId] || []);
      const conceptIds = uniqueOrdered(topicKeys.flatMap((topicKey) => edgeMap[topicKey] || []));
      const activeAlert = stageAlertMap[ruleId] || globalAlertMap[ruleId] || null;
      const semanticQuality = semanticEdgeQuality?.[ruleId] || null;

      let status = 'observed';
      if ((stage.status || '') === 'locked') status = 'locked';
      else if (resolvedRuleSet.has(ruleId)) status = 'resolved';
      else if (activeRuleSet.has(ruleId) || activeAlert) status = 'active';

      const rule = {
        id: ruleId,
        label: meta.name,
        severity: normalizeSeverity(meta.severity),
        weight: Number(meta.weight || 10),
        status,
        issue: activeAlert?.issue || '',
        stageId: stage.id,
        stageLabel: stage.label,
        topicKeys,
        conceptIds,
        semanticQuality,
      };

      ruleMap[ruleId] = rule;
      ruleToConcepts[ruleId] = conceptIds;
      ruleToTopics[ruleId] = [];
      conceptIds.forEach((conceptId) => {
        conceptToRules[conceptId] = conceptToRules[conceptId] || [];
        if (!conceptToRules[conceptId].includes(ruleId)) conceptToRules[conceptId].push(ruleId);
        conceptFrequency[conceptId] = (conceptFrequency[conceptId] || 0) + 1;
      });
      return rule;
    });

    const topicKeys = uniqueOrdered(rules.flatMap((rule) => rule.topicKeys));
    const topics = topicKeys.map((topicKey) => {
      const conceptIds = uniqueOrdered((edgeMap[topicKey] || []).filter(Boolean));
      const ownerRuleIds = rules.filter((rule) => rule.topicKeys.includes(topicKey)).map((rule) => rule.id);
      const severity = ownerRuleIds.reduce((best, ruleId) => {
        const current = ruleMap[ruleId]?.severity || 'medium';
        return SEVERITY_RANK[current] > SEVERITY_RANK[best] ? current : best;
      }, 'low');
      const topicId = `${stage.id}::${topicKey}`;
      const topic = {
        id: topicId,
        key: topicKey,
        label: formatNodeName(topicKey),
        stageId: stage.id,
        ownerRuleIds,
        conceptIds,
        severity,
        hasData: conceptIds.length > 0,
      };
      topicMap[topicId] = topic;
      ownerRuleIds.forEach((ruleId) => {
        ruleToTopics[ruleId] = ruleToTopics[ruleId] || [];
        if (!ruleToTopics[ruleId].includes(topicId)) ruleToTopics[ruleId].push(topicId);
      });
      conceptIds.forEach((conceptId) => {
        conceptToTopics[conceptId] = conceptToTopics[conceptId] || [];
        if (!conceptToTopics[conceptId].includes(topicId)) conceptToTopics[conceptId].push(topicId);
      });
      return topic;
    });

    const conceptIds = uniqueOrdered(topics.flatMap((topic) => topic.conceptIds));
    const concepts = conceptIds.map((conceptId) => {
      const label = parseConceptLabel(conceptId);
      const concept = {
        id: conceptId,
        label,
        fullLabel: label,
        ownerRuleIds: conceptToRules[conceptId] || [],
        ownerTopicIds: conceptToTopics[conceptId] || [],
      };
      conceptMap[conceptId] = conceptMap[conceptId] || concept;
      return concept;
    });

    return {
      id: stage.id,
      index: stage.index,
      label: stage.label,
      shortLabel: stage.short_label || `第${stage.index}阶段`,
      progress: Number(stage.progress_pct || 0),
      status: stage.status,
      passThreshold: Number(stage.pass_threshold || 80),
      rules,
      topics,
      concepts,
      accent: STAGE_ACCENTS[stageIdx] || STAGE_ACCENTS[0],
    };
  });

  return {
    lanes,
    ruleMap,
    topicMap,
    conceptMap,
    ruleToConcepts,
    ruleToTopics,
    conceptToRules,
    conceptToTopics,
    conceptFrequency,
  };
}


export default function SnapshotOverlay({ open, snapshot, onClose }) {
  const containerRef = useRef(null);
  const fgRef = useRef(null);

  const [activeModeTab, setActiveModeTab] = useState('project');
  // 默认 Tab 改为 'rules'
  const [projectTab, setProjectTab] = useState('rules');
  const [competitionTab, setCompetitionTab] = useState('overview');
  const [topologyStageFilter, setTopologyStageFilter] = useState('');
  const [selectedTopologyRule, setSelectedTopologyRule] = useState('');
  const [selectedTopologyConcept, setSelectedTopologyConcept] = useState('');

  const project = snapshot?.project?.generated_content;
  const hypergraph = snapshot?.project?.hypergraph_data || snapshot?.hypergraph_data;
  const projectStageFlow = snapshot?.project?.stage_flow || null;
  const competition = snapshot?.competition?.generated_content;
  const semanticReport = hypergraph?.semantic_report || {};
  const semanticChecks = semanticReport?.checks || [];
  const semanticSummary = semanticReport?.summary || {};
  const semanticEdgeQuality = semanticReport?.edge_quality || {};
  const structuralRuleStatus = hypergraph?.structural_rule_status || {};
  const structuralResolvedRuleIds = structuralRuleStatus?.resolved_rule_ids || [];
  const structuralActiveAlerts = structuralRuleStatus?.active_alerts || [];
  const structuralFieldNotes = hypergraph?.structural_field_notes || [];

  const stageFollowups = projectStageFlow?.current_followup_questions || [];

  useEffect(() => {
    if (competition && !project) setActiveModeTab('competition');
    if (project && !competition) setActiveModeTab('project');
  }, [project, competition]);

  useEffect(() => {
    if (!open) return;
    setTopologyStageFilter(projectStageFlow?.current_stage_id || 'all');
    setSelectedTopologyRule('');
    setSelectedTopologyConcept('');
  }, [open, projectStageFlow?.current_stage_id, hypergraph]);

  const formatNodeName = (name) => {
    const map = {
      Target_Customer: '目标客群', Value_Proposition: '价值主张', Marketing_Channel: '营销渠道',
      Revenue_Model: '收入模型', Cost_Structure: '成本结构', Core_Pain_Point: '核心痛点',
      Price: '产品定价', LTV: '客户终身价值', CAC: '获客成本', Startup_Capital: '启动资金',
      Account_Period: '账期', Seed_Users: '种子用户', Tech_Route: '技术路线',
      Team_Background: '团队背景', Competitor_Pool: '竞争对手', IP: '知识产权',
      Fulfill_Cost: '履约成本', Supplier_Network: '供应链', Control_Experiment: '对照实验',
      TAM: '总潜在市场', SAM: '可服务市场', SOM: '可获得市场', Usage_Frequency: '使用频次',
      Milestone_Plan: '里程碑', Policy_Constraints: '政策约束',
      Core_Business_Loop: '商业核心闭环', Customer_Value_Misalignment: '客群与价值错位',
      Channel_Physical_Access: '渠道物理触达', Willingness_To_Pay: '支付意愿支撑',
      Market_Reachability: '市场规模漏斗', Frequency_Mismatch: '频次与收入错配',
      Unit_Economics: '单位经济模型', Pricing_Space: '定价与利润空间',
      Cash_Flow_Health: '现金流健康度', Financial_Reasonableness: '财务预测合理性',
      Supply_Chain_Sync: '供应链履约交付', Cold_Start_Engine: '冷启动引擎',
      R_D_Team_Match: '研发团队匹配', Resource_Feasibility: '资源方案可行性',
      Tech_Barrier: '技术护城河', Real_Competition: '真实竞争格局',
      Narrative_Causality: '叙事因果逻辑', Innovation_Verification: '创新差异化验证',
      Compliance_Ethics: '合规与伦理限制', Social_Value_Translation: '社会价值转化',
    };
    return map[name] || name;
  };

  const formatSemanticDimension = (dimension) => SEMANTIC_DIMENSION_LABELS[dimension] || dimension || '语义校验';
  const getSemanticStatusMeta = (status) => SEMANTIC_STATUS_META[String(status || 'unknown').toLowerCase()] || SEMANTIC_STATUS_META.unknown;

  const getVisualLabel = (rawId) => {
    if (!rawId) return '';
    let text = String(rawId);
    if (text.includes(': ')) text = text.split(': ')[1];
    else if (text.includes(':')) text = text.split(':')[1];
    else if (text.includes('：')) text = text.split('：')[1];
    else text = formatNodeName(text);
    if (text.length > 14) return text.substring(0, 14) + '...';
    return text;
  };

  const graphData = useMemo(() => {
    if (!hypergraph) return { nodes: [], links: [] };
    const nodesData = [];
    const linksData = [];
    const nodeSet = new Set();
    const discreteNodes = hypergraph.nodes || [];
    const edges = hypergraph.edges || {};

    discreteNodes.forEach((nodeName) => {
      if (!nodeSet.has(nodeName)) {
        nodesData.push({ id: nodeName, group: 1, type: 'entity' });
        nodeSet.add(nodeName);
      }
    });

    Object.entries(edges).forEach(([edgeName, linkedNodes]) => {
      const formattedEdge = formatNodeName(edgeName);
      const edgeNodeId = `REL_${edgeName}`;

      nodesData.push({ id: edgeNodeId, label: formattedEdge, group: 3, type: 'relation' });

      linkedNodes.forEach((nodeRawId) => {
        if (!nodeSet.has(nodeRawId)) {
          nodesData.push({ id: nodeRawId, group: 2, type: 'entity' });
          nodeSet.add(nodeRawId);
        }
        linksData.push({ source: nodeRawId, target: edgeNodeId });
      });
    });

    return { nodes: nodesData, links: linksData };
  }, [hypergraph]);

  // 修改：大幅增加排斥力，让节点散开，并增加阻尼让它尽快稳定
  useEffect(() => {
    if (open && fgRef.current) {
      fgRef.current.d3Force('charge').strength(-1500);
      fgRef.current.d3Force('link').distance(110);
      fgRef.current.d3VelocityDecay(0.3);
    }
  }, [open, graphData]);

  useEffect(() => {
    if (!open) return undefined;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') onClose?.();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [open, onClose]);

  if (!open) return null;

  const renderProjectStageFlow = () => {
    if (!projectStageFlow) return null;

    const stages = Object.values(projectStageFlow.stages || {}).sort((a, b) => (a.index || 0) - (b.index || 0));
    const currentStage = stages.find((item) => item.id === projectStageFlow.current_stage_id) || stages[0];
    const anchorStatus = currentStage?.anchor_status || {};
    const gate = projectStageFlow?.current_stage_gate || {};
    const blockers = gate?.blocked_reasons || [];

    return (
      <div className="space-y-4">
        <div className="bg-amber-50 border border-amber-100 rounded-xl p-4 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex-1">
            <div className="text-xs font-bold text-amber-600 mb-1">当前阶段</div>
            <div className="text-base font-bold text-slate-800">
              第{projectStageFlow.current_stage_index}阶段【{projectStageFlow.current_stage_label}】
            </div>
            <div className="text-sm text-slate-600 mt-1 leading-relaxed">
              {currentStage?.goal || currentStage?.coach_hint || projectStageFlow.current_stage_entry_message || '系统将优先围绕当前阶段推进。'}
            </div>
            <div className="text-[11px] font-medium text-amber-800 mt-2 bg-amber-100/50 px-2 py-1 rounded inline-block">
              🎯 进度算法：(已通关规则权重和 ÷ 本阶段考核总权重) × 100 + 真实调研证据加分
            </div>
          </div>

          {/* 修改：百分比块瘦身，突出数字 */}
          <div className="rounded-2xl bg-white border border-amber-200 px-5 py-3 shrink-0 text-center flex flex-col items-center justify-center shadow-sm">
            <div className="text-[10px] text-amber-600 font-bold mb-1">阶段进度</div>
            <div className="text-4xl font-black text-amber-600 leading-none">
              {currentStage?.progress_pct ?? 0}<span className="text-lg font-bold ml-0.5">%</span>
            </div>
            <div className="text-[10px] text-slate-500 mt-1 font-semibold">及格线 {currentStage?.pass_threshold ?? 80}%</div>
          </div>
        </div>

        {projectStageFlow.milestone_message && (
          <div className="rounded-xl bg-white border border-amber-200 p-3 text-sm text-amber-700">
            🎉 {projectStageFlow.milestone_message}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {stages.map((stage) => {
            const active = stage.status === 'current';
            const passed = stage.status === 'passed';
            return (
              <div key={stage.id} className={`rounded-xl border p-3 ${passed ? 'bg-emerald-50 border-emerald-100' : active ? 'bg-orange-50 border-orange-100' : 'bg-slate-50 border-slate-200'}`}>
                <div className={`text-xs font-bold mb-1 ${passed ? 'text-emerald-600' : active ? 'text-orange-600' : 'text-slate-500'}`}>
                  {stage.short_label || `第${stage.index}阶段`}
                </div>
                <div className="font-semibold text-slate-800 text-sm mb-1">{stage.label}</div>
                <div className="text-xs text-slate-500">进度 {stage.progress_pct ?? 0}%</div>
                <div className="mt-2 w-full h-1.5 rounded-full bg-white/70 border border-white/40 overflow-hidden">
                  <div className={`h-full ${passed ? 'bg-emerald-500' : active ? 'bg-orange-500' : 'bg-slate-300'}`} style={{ width: `${Math.min(stage.progress_pct ?? 0, 100)}%` }}></div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div className="text-sm font-bold text-slate-800 mb-2">本轮结构锚点</div>
            <div className="space-y-2">
              {(anchorStatus.groups || []).map((group) => (
                <div key={group.label} className={`rounded-lg border px-3 py-2 text-sm ${group.passed ? 'bg-emerald-50 border-emerald-100 text-emerald-700' : 'bg-red-50 border-red-100 text-red-700'}`}>
                  <div className="font-semibold">{group.label}</div>
                  <div className="text-xs mt-1">
                    {group.passed ? `已识别：${(group.matched_keys || []).join(' / ')}` : `仍缺关键表达：${(group.required_keys || []).join(' / ')}`}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div className="text-sm font-bold text-slate-800 mb-2">本轮推荐追问</div>
            {stageFollowups.length > 0 ? (
              <ul className="space-y-2">
                {stageFollowups.slice(0, 3).map((item, idx) => (
                  <li key={`${item.rule_id}-${idx}`} className="rounded-lg bg-slate-50 border border-slate-100 px-3 py-2 text-sm text-slate-700 leading-relaxed">
                    <span className="font-semibold text-orange-600 mr-1">[{item.rule_id}]</span>
                    {item.question}
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-sm text-slate-500">当前阶段暂无额外追问建议。</div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderStageRules = () => {
    if (!projectStageFlow) return null;

    const stages = Object.values(projectStageFlow.stages || {}).sort((a, b) => (a.index || 0) - (b.index || 0));
    const currentStage = stages.find((item) => item.id === projectStageFlow.current_stage_id) || stages[0];
    if (!currentStage) return null;

    const allRuleIds = currentStage.rule_ids || [];
    const resolvedRuleIds = currentStage.resolved_rule_ids || [];
    const activeAlerts = currentStage.active_alerts || [];
    const topologyAlertMap = (structuralActiveAlerts || []).reduce((acc, alert) => {
      if (alert?.rule) acc[alert.rule] = alert;
      return acc;
    }, {});
    const stageSemanticRuleIds = allRuleIds.filter((ruleId) => structuralResolvedRuleIds.includes(ruleId) && semanticEdgeQuality?.[ruleId]);
    const stageSemanticSummary = {
      riskyCount: stageSemanticRuleIds.filter((ruleId) => ['contradictory', 'suspicious'].includes(semanticEdgeQuality?.[ruleId]?.worst_status)).length,
      needsEvidenceCount: stageSemanticRuleIds.filter((ruleId) => semanticEdgeQuality?.[ruleId]?.worst_status === 'needs_evidence').length,
      confirmedCount: stageSemanticRuleIds.filter((ruleId) => semanticEdgeQuality?.[ruleId]?.worst_status === 'confirmed').length,
    };

    if (allRuleIds.length === 0) {
      return (
        <div className="py-12 text-center text-slate-400 bg-white rounded-b-xl">
          <ShieldAlert size={36} className="mx-auto mb-3 opacity-20" />
          <p className="text-sm">太棒了！本阶段暂无需要考核的专项规则。</p>
        </div>
      );
    }

    return (
      <div className="space-y-4 p-4 bg-slate-50 max-h-[520px] overflow-y-auto rounded-b-xl">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-3 mb-3">
            <div>
              <div className="text-sm font-bold text-slate-800">本阶段考核规则（先结构判定，后语义复核）</div>
              <div className="text-xs text-slate-500 mt-1">仅显示当前阶段对应规则。系统会先判断规则对应的超边结构是否达成；这里的“结构达成”以拓扑关系是否通过为准。若标准字段表达还不够完整，系统会额外给出“字段完备度提示”，但不会直接否掉结构判定。只有结构先达成的规则，才继续进入语义复核。语义区会区分展示“结构命中字段”和“复核字段对”：前者表示本条规则在当前材料中已命中的相关结构字段，后者表示系统用于语义复核的核心字段对。语义“待补证”不会取消“已突破”，语义“存疑/冲突”会取消“已突破”。</div>
            </div>
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="px-2 py-1 rounded-full border border-red-200 bg-red-50 text-red-700 font-semibold">语义存疑 {stageSemanticSummary.riskyCount}</span>
              <span className="px-2 py-1 rounded-full border border-amber-200 bg-amber-50 text-amber-700 font-semibold">待补证 {stageSemanticSummary.needsEvidenceCount}</span>
              <span className="px-2 py-1 rounded-full border border-emerald-200 bg-emerald-50 text-emerald-700 font-semibold">语义通过 {stageSemanticSummary.confirmedCount}</span>
            </div>
          </div>

          <div className="space-y-3">
            {allRuleIds.map((ruleId) => {
              const isPassed = resolvedRuleIds.includes(ruleId);
              const activeAlert = activeAlerts.find((a) => a.rule === ruleId);
              const structuralAlert = topologyAlertMap?.[ruleId] || null;
              const structuralFieldNote = (structuralFieldNotes || []).find((item) => item?.rule === ruleId) || null;
              const structurallyPassed = structuralResolvedRuleIds.includes(ruleId);
              const meta = RULE_METADATA[ruleId] || { name: `规则 ${ruleId}`, severity: 'medium', weight: 10 };
              const ruleSemanticItems = (semanticChecks || []).filter((item) => item?.rule_id === ruleId);
              const ruleSemanticQuality = structurallyPassed ? (semanticEdgeQuality?.[ruleId] || null) : null;
              const semanticUi = ruleSemanticQuality ? getSemanticStatusMeta(ruleSemanticQuality?.worst_status || 'unknown') : null;
              const blockedBySemantic = structurallyPassed && !isPassed && ['contradictory', 'suspicious'].includes(ruleSemanticQuality?.worst_status);
              const blockedByStructure = !structurallyPassed;

              const sevMap = {
                critical: { label: `规则等级：高危（权重:${meta.weight}）`, color: isPassed ? 'text-emerald-700 bg-emerald-100 border-emerald-200' : 'text-red-700 bg-red-100 border-red-200' },
                high: { label: `规则等级：高风险（权重:${meta.weight}）`, color: isPassed ? 'text-emerald-700 bg-emerald-100 border-emerald-200' : 'text-orange-700 bg-orange-100 border-orange-200' },
                medium: { label: `规则等级：中风险（权重:${meta.weight}）`, color: isPassed ? 'text-emerald-700 bg-emerald-100 border-emerald-200' : 'text-amber-700 bg-amber-100 border-amber-200' },
              };
              const sev = sevMap[meta.severity] || sevMap.medium;

              return (
                <div key={ruleId} className={`border rounded-xl p-3 shadow-sm transition-all ${isPassed ? 'bg-emerald-50/50 border-emerald-200' : 'bg-white border-red-200'}`}>
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="flex items-center gap-2">
                      {isPassed ? <CheckCircle size={16} className="text-emerald-500" /> : <AlertTriangle size={16} className="text-red-500" />}
                      <span className="font-mono font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded text-xs border border-slate-200">{ruleId}</span>
                      <h6 className={`font-bold text-sm ${isPassed ? 'text-emerald-800' : 'text-slate-800'}`}>{meta.name}</h6>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${sev.color}`}>{sev.label}</span>
                      {semanticUi && (
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${semanticUi.badge}`}>{semanticUi.label}</span>
                      )}
                    </div>
                  </div>

                  {blockedByStructure && structuralAlert && (
                    <p className="mt-2 text-sm text-slate-600 leading-relaxed bg-red-50/60 p-2.5 rounded-lg border border-red-100">
                      <span className="font-semibold text-red-700">结构判定未通过：</span>{structuralAlert.issue}
                    </p>
                  )}

                  {structurallyPassed && structuralFieldNote && (
                    <p className="mt-2 text-sm text-slate-600 leading-relaxed bg-amber-50/70 p-2.5 rounded-lg border border-amber-200">
                      <span className="font-semibold text-amber-700">字段完备度提示：</span>{structuralFieldNote.issue}
                    </p>
                  )}

                  {blockedBySemantic && activeAlert && (
                    <p className="mt-2 text-sm text-slate-600 leading-relaxed bg-red-50/60 p-2.5 rounded-lg border border-red-100">
                      <span className="font-semibold text-red-700">结构已达成，但语义复核未通过：</span>{activeAlert.issue}
                    </p>
                  )}

                  {structurallyPassed && ruleSemanticItems.length > 0 && (
                    <div className={`mt-3 rounded-xl border p-3 ${semanticUi?.card || 'border-slate-200 bg-slate-50'}`}>
                      <div className="flex items-center justify-between gap-3 mb-2">
                        <div className="text-xs font-bold text-slate-700">对应超边语义复核</div>
                        <div className="text-[11px] text-slate-500">只对已通过结构判定的规则继续复核语义是否成立</div>
                      </div>
                      <div className="space-y-2">
                        {ruleSemanticItems.map((item) => {
                          const itemUi = getSemanticStatusMeta(item?.status);
                          return (
                            <div key={item.id} className="rounded-lg border border-white/80 bg-white/80 px-3 py-2">
                              <div className="flex flex-wrap items-start justify-between gap-3">
                                <div>
                                  <div className="text-[11px] font-bold text-slate-500 mb-1">{formatSemanticDimension(item.dimension)}</div>
                                  <div className="text-sm font-semibold text-slate-800 leading-relaxed">
                                    {formatNodeName(item.left_key)}：{item.left_value} <span className="text-slate-400 mx-1">×</span> {formatNodeName(item.right_key)}：{item.right_value}
                                  </div>
                                </div>
                                <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${itemUi.badge}`}>{itemUi.label}</span>
                              </div>
                              <div className="mt-2 text-sm text-slate-700 leading-relaxed">{item.reason}</div>
                              {Array.isArray(item.structural_hit_fields) && item.structural_hit_fields.length > 0 && (
                                <div className="mt-2 text-xs text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg px-2.5 py-2">
                                  <span className="font-semibold text-indigo-700">结构命中字段：</span>
                                  {item.structural_hit_fields.join('；')}
                                </div>
                              )}
                              <div className="mt-2 text-xs text-violet-700 bg-violet-50 border border-violet-200 rounded-lg px-2.5 py-2">
                                <span className="font-semibold text-violet-700">复核字段对：</span>
                                {formatNodeName(item.left_key)}：{item.left_value} × {formatNodeName(item.right_key)}：{item.right_value}
                              </div>
                              {item.evidence_hint && (
                                <div className="mt-2 text-xs text-slate-600 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-2">
                                  <span className="font-semibold text-slate-700">建议补证：</span>{item.evidence_hint}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {isPassed && semanticUi?.label === '待补证' && (
                    <p className="mt-2 text-xs text-amber-700 font-semibold flex items-center gap-1">✓ 该规则已通过结构判定；当前语义结论为“待补证”，仍计入“已突破”</p>
                  )}
                  {isPassed && semanticUi?.label === '语义通过' && (
                    <p className="mt-2 text-xs text-emerald-600 font-semibold flex items-center gap-1">✓ 该规则已通过结构判定，且语义复核通过；当前计入“已突破”</p>
                  )}
                  {isPassed && !semanticUi && (
                    <p className="mt-2 text-xs text-emerald-600 font-semibold flex items-center gap-1">✓ 该规则属于结构性规则，当前按结构判定计入“已突破”</p>
                  )}
                  {blockedBySemantic && semanticUi && (
                    <p className="mt-2 text-xs text-red-600 font-semibold flex items-center gap-1">✕ 该规则虽然已通过结构判定，但语义结论为“{semanticUi.label}”，因此当前不计入“已突破”</p>
                  )}
                  {blockedByStructure && (
                    <p className="mt-2 text-xs text-slate-500">该规则当前仍停留在结构判定阶段；只有先满足对应超边结构要求，才会继续触发语义复核。</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  const renderHypergraph = () => {
    const topologyModel = buildTopologyModel({ hypergraph, projectStageFlow, formatNodeName, semanticEdgeQuality });
    const lanes = topologyModel.lanes || [];

    if (lanes.length === 0) {
      return (
        <div className="py-12 bg-white rounded-b-xl text-center">
          <p className="text-sm text-slate-400">暂未提取到可用于阶段网图与关联矩阵的拓扑数据。</p>
        </div>
      );
    }

    const currentStageId = projectStageFlow?.current_stage_id || lanes[0]?.id || 'all';
    const activeStageId = topologyStageFilter || currentStageId || 'all';
    const visibleLanes = activeStageId === 'all' ? lanes : lanes.filter((lane) => lane.id === activeStageId);

    const selectedRule = selectedTopologyRule ? topologyModel.ruleMap[selectedTopologyRule] : null;
    const selectedConcept = selectedTopologyConcept ? topologyModel.conceptMap[selectedTopologyConcept] : null;

    let highlightedRuleIds = new Set();
    let highlightedTopicIds = new Set();
    let highlightedConceptIds = new Set();

    if (selectedRule && selectedConcept) {
      const conceptIds = new Set(topologyModel.ruleToConcepts[selectedRule.id] || []);
      if (conceptIds.has(selectedConcept.id)) {
        highlightedRuleIds = new Set([selectedRule.id]);
        highlightedConceptIds = new Set([selectedConcept.id]);
        highlightedTopicIds = new Set(
          (topologyModel.ruleToTopics[selectedRule.id] || []).filter((topicId) =>
            (topologyModel.topicMap[topicId]?.conceptIds || []).includes(selectedConcept.id)
          )
        );
      } else {
        highlightedRuleIds = new Set([selectedRule.id]);
        highlightedConceptIds = new Set([selectedConcept.id]);
      }
    } else if (selectedRule) {
      highlightedRuleIds = new Set([selectedRule.id]);
      highlightedTopicIds = new Set(topologyModel.ruleToTopics[selectedRule.id] || []);
      highlightedConceptIds = new Set(topologyModel.ruleToConcepts[selectedRule.id] || []);
    } else if (selectedConcept) {
      highlightedConceptIds = new Set([selectedConcept.id]);
      highlightedRuleIds = new Set(topologyModel.conceptToRules[selectedConcept.id] || []);
      highlightedTopicIds = new Set(topologyModel.conceptToTopics[selectedConcept.id] || []);
    }

    const hasFocus = highlightedRuleIds.size > 0 || highlightedConceptIds.size > 0 || highlightedTopicIds.size > 0;

    const laneWidth = visibleLanes.length === 1 ? 1100 : visibleLanes.length === 2 ? 540 : 360;
    const laneGap = 18;
    const outerPadding = 16;
    const baseTop = 104;
    const rowGapRule = 54;
    const rowGapTopic = 54;
    const rowGapConcept = 46;

    const laneHeights = visibleLanes.map((lane) => {
      const rowCount = Math.max(lane.rules.length, lane.topics.length, lane.concepts.length, 4);
      return Math.max(360, baseTop + rowCount * Math.max(rowGapRule, rowGapConcept) + 24);
    });
    const svgHeight = Math.max(...laneHeights, 420);
    const svgWidth = outerPadding * 2 + visibleLanes.length * laneWidth + Math.max(0, visibleLanes.length - 1) * laneGap;

    const positions = { rules: {}, topics: {}, concepts: {} };

    visibleLanes.forEach((lane, laneIndex) => {
      const laneX = outerPadding + laneIndex * (laneWidth + laneGap);
      const ruleX = laneX + Math.max(70, laneWidth * 0.16);
      const topicX = laneX + laneWidth * 0.50;
      const conceptX = laneX + laneWidth * 0.82;

      lane.rules.forEach((rule, idx) => {
        positions.rules[rule.id] = { x: ruleX, y: baseTop + idx * rowGapRule };
      });
      lane.topics.forEach((topic, idx) => {
        positions.topics[topic.id] = { x: topicX, y: baseTop + idx * rowGapTopic };
      });
      lane.concepts.forEach((concept, idx) => {
        positions.concepts[`${lane.id}::${concept.id}`] = { x: conceptX, y: baseTop + idx * rowGapConcept };
      });
    });

    const linkOpacity = (type, sourceId, targetId) => {
      if (!hasFocus) return type === 'topic-concept' ? 0.35 : 0.48;
      if (type === 'rule-topic') {
        return highlightedRuleIds.has(sourceId) && highlightedTopicIds.has(targetId) ? 0.88 : 0.08;
      }
      const conceptRawId = targetId.split('::').slice(1).join('::');
      return highlightedTopicIds.has(sourceId) && highlightedConceptIds.has(conceptRawId) ? 0.82 : 0.06;
    };

    const rowRules = visibleLanes.flatMap((lane) => lane.rules);
    const matrixConceptIds = uniqueOrdered(
      rowRules.flatMap((rule) => topologyModel.ruleToConcepts[rule.id] || [])
    ).sort((a, b) => (topologyModel.conceptFrequency[b] || 0) - (topologyModel.conceptFrequency[a] || 0));

    const cappedMatrixConceptIds = matrixConceptIds.slice(0, activeStageId === 'all' ? 12 : 14);
    const hiddenMatrixCount = Math.max(0, matrixConceptIds.length - cappedMatrixConceptIds.length);

    const getRulePillStyle = (rule) => {
      const semanticStatus = rule?.semanticQuality?.worst_status || 'unknown';
      if (rule.status === 'resolved') {
        return { fill: '#ecfdf5', stroke: '#34d399', text: '#047857', badge: semanticStatus === 'confirmed' ? '结构+语义通过' : (semanticStatus === 'needs_evidence' ? '结构通过·待补证' : '结构通过') };
      }
      if (rule.status === 'locked') {
        return { fill: '#f8fafc', stroke: '#cbd5e1', text: '#94a3b8', badge: '未解锁' };
      }
      if (rule.status === 'active') {
        if (semanticStatus === 'contradictory' || semanticStatus === 'suspicious') return { fill: '#fff1f2', stroke: '#fb7185', text: '#be123c', badge: '语义存疑' };
        if (semanticStatus === 'needs_evidence') return { fill: '#fffbeb', stroke: '#f59e0b', text: '#b45309', badge: '待补证' };
        if (rule.severity === 'critical') return { fill: '#fff1f2', stroke: '#fb7185', text: '#be123c', badge: '结构未过' };
        if (rule.severity === 'high') return { fill: '#fff7ed', stroke: '#fb923c', text: '#c2410c', badge: '结构未过' };
        return { fill: '#fffbeb', stroke: '#f59e0b', text: '#b45309', badge: '结构未过' };
      }
      if (semanticStatus === 'confirmed') return { fill: '#ecfeff', stroke: '#67e8f9', text: '#0f766e', badge: '语义通过' };
      return { fill: '#eff6ff', stroke: '#93c5fd', text: '#1d4ed8', badge: '观察中' };
    };

    const getTopicStyle = (topic) => {
      const hasActiveOwner = topic.ownerRuleIds.some((ruleId) => topologyModel.ruleMap[ruleId]?.status === 'active');
      if (!topic.hasData) return { fill: '#ffffff', stroke: '#cbd5e1', text: '#94a3b8' };
      if (hasActiveOwner) return { fill: '#fff7ed', stroke: '#fdba74', text: '#b45309' };
      return { fill: '#ffffff', stroke: '#a5b4fc', text: '#4f46e5' };
    };

    const getConceptStyle = (conceptId) => {
      const ownerRules = topologyModel.conceptToRules[conceptId] || [];
      const hasActiveOwner = ownerRules.some((ruleId) => topologyModel.ruleMap[ruleId]?.status === 'active');
      const hasResolvedOwner = ownerRules.some((ruleId) => topologyModel.ruleMap[ruleId]?.status === 'resolved');
      if (hasActiveOwner) return { fill: '#fff7ed', stroke: '#fdba74', text: '#9a3412' };
      if (hasResolvedOwner) return { fill: '#ecfdf5', stroke: '#86efac', text: '#166534' };
      return { fill: '#f8fafc', stroke: '#cbd5e1', text: '#475569' };
    };

    const renderNodeLabel = (text, maxLength = 10) => {
      if (!text) return '';
      return text.length > maxLength ? `${text.slice(0, maxLength)}…` : text;
    };

    const ruleDetail = selectedRule ? topologyModel.ruleMap[selectedRule.id] : null;
    const conceptDetail = selectedConcept ? topologyModel.conceptMap[selectedConcept.id] : null;

    return (
      <div className="bg-white rounded-b-xl">
        <div className="border-b border-slate-200 px-4 py-3 bg-slate-50/70">
          <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <div className="text-sm font-bold text-slate-800">三阶段分层网图 + 规则 × 概念关联矩阵</div>
              <div className="text-xs text-slate-500 mt-1">
                将“阶段—规则—逻辑主题—文档概念”拆开显示；上方看结构，下方看覆盖密度。
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => {
                  setTopologyStageFilter('all');
                  setSelectedTopologyRule('');
                  setSelectedTopologyConcept('');
                }}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-colors ${activeStageId === 'all' ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}`}
              >
                全阶段总览
              </button>
              {lanes.map((lane) => (
                <button
                  key={lane.id}
                  type="button"
                  onClick={() => {
                    setTopologyStageFilter(lane.id);
                    setSelectedTopologyRule('');
                    setSelectedTopologyConcept('');
                  }}
                  className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-colors ${activeStageId === lane.id ? 'text-white border-transparent' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}`}
                  style={activeStageId === lane.id ? { backgroundColor: lane.accent.header } : undefined}
                >
                  第{lane.index}阶段 · {lane.progress}%
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="p-4 space-y-4">
          <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_320px] gap-4">
            <div className="rounded-2xl border border-slate-200 overflow-hidden bg-white">
              <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-slate-200 bg-white">
                <div className="text-sm font-bold text-slate-800">阶段分层网图</div>
                <div className="flex flex-wrap gap-2 text-[11px]">
                  <span className="inline-flex items-center gap-1 rounded-full bg-red-50 text-red-700 border border-red-100 px-2 py-1">高危 / 待修</span>
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100 px-2 py-1">已突破</span>
                  <span className="inline-flex items-center gap-1 rounded-full bg-slate-50 text-slate-500 border border-slate-200 px-2 py-1">未解锁 / 无数据</span>
                </div>
              </div>
              <div className="overflow-auto bg-slate-50/60">
                <svg width={svgWidth} height={svgHeight} className="block min-w-full">
                  {visibleLanes.map((lane, laneIndex) => {
                    const laneX = outerPadding + laneIndex * (laneWidth + laneGap);
                    const laneRectHeight = laneHeights[laneIndex] - 16;
                    const laneCurrent = currentStageId === lane.id;
                    return (
                      <g key={lane.id}>
                        <rect x={laneX} y={12} width={laneWidth} height={laneRectHeight} rx={20} fill={lane.accent.bg} stroke={laneCurrent ? lane.accent.header : lane.accent.border} strokeWidth={laneCurrent ? 2.2 : 1.2} />
                        <rect x={laneX + 1} y={13} width={laneWidth - 2} height={44} rx={18} fill={lane.accent.soft} stroke="none" />
                        <text x={laneX + 18} y={40} fontSize="15" fontWeight="700" fill={lane.accent.muted}>第{lane.index}阶段 · {lane.label}</text>
                        <text x={laneX + laneWidth - 18} y={40} textAnchor="end" fontSize="12" fontWeight="700" fill={lane.accent.header}>{lane.progress}% / {lane.passThreshold}%</text>
                        <text x={laneX + Math.max(70, laneWidth * 0.16)} y={80} textAnchor="middle" fontSize="11" fontWeight="700" fill="#64748b">规则</text>
                        <text x={laneX + laneWidth * 0.50} y={80} textAnchor="middle" fontSize="11" fontWeight="700" fill="#64748b">逻辑主题</text>
                        <text x={laneX + laneWidth * 0.82} y={80} textAnchor="middle" fontSize="11" fontWeight="700" fill="#64748b">文档概念</text>
                      </g>
                    );
                  })}

                  {visibleLanes.map((lane) =>
                    lane.rules.flatMap((rule) => {
                      const source = positions.rules[rule.id];
                      if (!source) return [];
                      return (topologyModel.ruleToTopics[rule.id] || []).filter((topicId) => positions.topics[topicId]).map((topicId) => {
                        const target = positions.topics[topicId];
                        const opacity = linkOpacity('rule-topic', rule.id, topicId);
                        return <path key={`rule-topic-${rule.id}-${topicId}`} d={`M ${source.x + 54} ${source.y} C ${source.x + 100} ${source.y}, ${target.x - 70} ${target.y}, ${target.x - 48} ${target.y}`} fill="none" stroke={rule.status === 'resolved' ? '#34d399' : '#cbd5e1'} strokeWidth={rule.status === 'resolved' ? 2.2 : 1.8} strokeOpacity={opacity} strokeLinecap="round" />;
                      });
                    })
                  )}

                  {visibleLanes.map((lane) =>
                    lane.topics.flatMap((topic) => {
                      const source = positions.topics[topic.id];
                      if (!source) return [];
                      return (topic.conceptIds || []).filter((conceptId) => positions.concepts[`${lane.id}::${conceptId}`]).map((conceptId) => {
                        const target = positions.concepts[`${lane.id}::${conceptId}`];
                        const opacity = linkOpacity('topic-concept', topic.id, `${lane.id}::${conceptId}`);
                        return <path key={`topic-concept-${topic.id}-${conceptId}`} d={`M ${source.x + 52} ${source.y} C ${source.x + 100} ${source.y}, ${target.x - 82} ${target.y}, ${target.x - 50} ${target.y}`} fill="none" stroke="#94a3b8" strokeWidth={1.6} strokeOpacity={opacity} strokeLinecap="round" strokeDasharray={topic.hasData ? '0' : '5 5'} />;
                      });
                    })
                  )}

                  {visibleLanes.map((lane) =>
                    lane.rules.map((rule) => {
                      const pos = positions.rules[rule.id];
                      if (!pos) return null;
                      const style = getRulePillStyle(rule);
                      const isFocused = !hasFocus || highlightedRuleIds.has(rule.id);
                      return (
                        <g key={`rule-${rule.id}`} transform={`translate(${pos.x}, ${pos.y})`} onClick={() => { setSelectedTopologyRule((prev) => (prev === rule.id ? '' : rule.id)); setSelectedTopologyConcept(''); }} className="cursor-pointer" opacity={isFocused ? 1 : 0.34}>
                          <title>{`${rule.id} · ${rule.label}${rule.issue ? `
${rule.issue}` : ''}`}</title>
                          <rect x={-56} y={-17} width={112} height={34} rx={17} fill={style.fill} stroke={style.stroke} strokeWidth={selectedTopologyRule === rule.id ? 2.8 : 1.8} />
                          <text textAnchor="middle" dominantBaseline="middle" fontSize="11.5" fontWeight="700" fill={style.text}>{rule.id}</text>
                          <text textAnchor="middle" y={23} fontSize="10.5" fontWeight="700" fill={style.text}>{style.badge}</text>
                        </g>
                      );
                    })
                  )}

                  {visibleLanes.map((lane) =>
                    lane.topics.map((topic) => {
                      const pos = positions.topics[topic.id];
                      if (!pos) return null;
                      const style = getTopicStyle(topic);
                      const isFocused = !hasFocus || highlightedTopicIds.has(topic.id);
                      return (
                        <g key={`topic-${topic.id}`} transform={`translate(${pos.x}, ${pos.y})`} onClick={() => { const ownerRule = topic.ownerRuleIds?.[0] || ''; setSelectedTopologyRule((prev) => (prev === ownerRule ? '' : ownerRule)); setSelectedTopologyConcept(''); }} className="cursor-pointer" opacity={isFocused ? 1 : 0.38}>
                          <title>{`${topic.label}${topic.hasData ? '' : `\n当前文档尚未抽取到该主题下的明确概念`}`}</title>
                          <rect x={-58} y={-16} width={116} height={32} rx={12} fill={style.fill} stroke={style.stroke} strokeWidth={selectedTopologyRule && topic.ownerRuleIds.includes(selectedTopologyRule) ? 2.4 : 1.6} />
                          <text textAnchor="middle" dominantBaseline="middle" fontSize="11" fontWeight="700" fill={style.text}>{renderNodeLabel(topic.label, 8)}</text>
                        </g>
                      );
                    })
                  )}

                  {visibleLanes.map((lane) =>
                    lane.concepts.map((concept) => {
                      const pos = positions.concepts[`${lane.id}::${concept.id}`];
                      if (!pos) return null;
                      const style = getConceptStyle(concept.id);
                      const isFocused = !hasFocus || highlightedConceptIds.has(concept.id);
                      return (
                        <g key={`concept-${lane.id}-${concept.id}`} transform={`translate(${pos.x}, ${pos.y})`} onClick={() => { setSelectedTopologyConcept((prev) => (prev === concept.id ? '' : concept.id)); if (selectedTopologyRule && !(topologyModel.ruleToConcepts[selectedTopologyRule] || []).includes(concept.id)) { setSelectedTopologyRule(''); } }} className="cursor-pointer" opacity={isFocused ? 1 : 0.36}>
                          <title>{concept.fullLabel}</title>
                          <rect x={-62} y={-15} width={124} height={30} rx={10} fill={style.fill} stroke={style.stroke} strokeWidth={selectedTopologyConcept === concept.id ? 2.4 : 1.4} />
                          <text textAnchor="middle" dominantBaseline="middle" fontSize="11" fontWeight="600" fill={style.text}>{renderNodeLabel(concept.fullLabel, 9)}</text>
                        </g>
                      );
                    })
                  )}
                </svg>
              </div>
              <div className="px-4 py-3 border-t border-slate-200 bg-slate-50 text-xs text-slate-500 flex flex-wrap gap-x-4 gap-y-1">
                <span>点击规则节点：聚焦该规则影响的主题与概念</span>
                <span>点击概念节点：反查它被哪些规则反复命中</span>
                <span>阶段切换：查看单阶段或全阶段总览</span>
              </div>
            </div>

            <div className="space-y-4">
              <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="text-sm font-bold text-slate-800 mb-3">当前聚焦说明</div>
                {!ruleDetail && !conceptDetail ? (
                  <div className="text-sm text-slate-500 leading-relaxed">默认展示当前阶段的整体拓扑。可点击规则节点或矩阵单元格，查看“某条规则为什么打到某个概念”，以及它当前的语义是否通过。</div>
                ) : (
                  <div className="space-y-3">
                    {ruleDetail && (
                      <div className="rounded-xl border border-slate-200 p-3 bg-slate-50">
                        <div className="flex items-center justify-between gap-3 mb-2">
                          <div className="text-sm font-bold text-slate-800">{ruleDetail.id} · {ruleDetail.label}</div>
                          <span className={`text-[11px] font-bold px-2 py-1 rounded-full ${ruleDetail.status === 'resolved' ? 'bg-emerald-100 text-emerald-700' : ruleDetail.status === 'active' ? 'bg-orange-100 text-orange-700' : 'bg-slate-100 text-slate-600'}`}>{ruleDetail.status === 'resolved' ? '已突破' : ruleDetail.status === 'active' ? '待修' : ruleDetail.status === 'locked' ? '未解锁' : '观察中'}</span>
                        </div>
                        <div className="text-xs text-slate-600 leading-relaxed">{ruleDetail.issue || '当前规则没有额外的预警文本，图中主要展示其作用到的逻辑主题与文档概念。'}</div>
                        {ruleDetail.semanticQuality && (
                          <div className="mt-2 text-[11px] text-slate-600 leading-relaxed">语义状态：{getSemanticStatusMeta(ruleDetail.semanticQuality.worst_status).label}；涉及 {ruleDetail.semanticQuality.count || 0} 组校验，风险 {ruleDetail.semanticQuality.risky_count || 0} 组。</div>
                        )}
                        <div className="mt-3 text-[11px] text-slate-500 leading-relaxed">关联主题：{(ruleDetail.topicKeys || []).map((key) => formatNodeName(key)).join('、') || '暂无'}</div>
                      </div>
                    )}
                    {conceptDetail && (
                      <div className="rounded-xl border border-slate-200 p-3 bg-slate-50">
                        <div className="text-sm font-bold text-slate-800 mb-2">概念命中：{conceptDetail.fullLabel}</div>
                        <div className="text-xs text-slate-600 leading-relaxed">该概念目前关联 {((topologyModel.conceptToRules[conceptDetail.id] || []).length)} 条规则：{(topologyModel.conceptToRules[conceptDetail.id] || []).map((ruleId) => `${ruleId} ${topologyModel.ruleMap[ruleId]?.label || ''}`).join('、') || '暂无'}</div>
                      </div>
                    )}
                    <button type="button" onClick={() => { setSelectedTopologyRule(''); setSelectedTopologyConcept(''); }} className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50">清除聚焦</button>
                  </div>
                )}
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="text-sm font-bold text-slate-800 mb-3">图例</div>
                <div className="space-y-2 text-xs text-slate-600">
                  <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-orange-200 border border-orange-300"></span> 当前仍阻塞的规则 / 概念</div>
                  <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-emerald-200 border border-emerald-300"></span> 已解除或已通过的规则链</div>
                  <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-slate-200 border border-slate-300"></span> 未来阶段或暂未抽取到数据的结构位</div>
                  <div className="text-[11px] text-slate-500 pt-1 leading-relaxed">这不是自由散点图，而是按阶段把“规则—主题—概念”拆成三列，让学生和教师都能直接看懂逻辑链条。</div>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 overflow-hidden bg-white shadow-sm">
            <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-slate-200 bg-white">
              <div>
                <div className="text-sm font-bold text-slate-800">规则 × 概念关联矩阵</div>
                <div className="text-xs text-slate-500 mt-1">纵向看规则，横向看概念；颜色越深，说明该规则越直接地命中了该概念。</div>
              </div>
              {hiddenMatrixCount > 0 && <div className="text-[11px] text-slate-500">为保证清晰度，已折叠其余 {hiddenMatrixCount} 个低频概念</div>}
            </div>
            <div className="overflow-auto">
              <table className="min-w-full border-separate border-spacing-0 text-xs">
                <thead>
                  <tr>
                    <th className="sticky left-0 z-10 bg-white border-b border-r border-slate-200 px-3 py-3 text-left min-w-[180px] text-slate-600">规则 \ 概念</th>
                    {cappedMatrixConceptIds.map((conceptId) => (
                      <th key={conceptId} className="border-b border-slate-200 px-2 py-3 bg-white min-w-[88px] align-bottom">
                        <div className="font-semibold text-slate-700 leading-tight">{renderNodeLabel(topologyModel.conceptMap[conceptId]?.fullLabel || conceptId, 12)}</div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rowRules.map((rule) => {
                    const rowStyle = getRulePillStyle(rule);
                    return (
                      <tr key={`matrix-${rule.id}`}>
                        <td className="sticky left-0 z-[1] bg-white border-r border-b border-slate-200 px-3 py-2 min-w-[180px]">
                          <button type="button" onClick={() => { setSelectedTopologyRule((prev) => (prev === rule.id ? '' : rule.id)); setSelectedTopologyConcept(''); }} className="w-full text-left">
                            <div className="font-bold" style={{ color: rowStyle.text }}>{rule.id}</div>
                            <div className="text-slate-600 mt-0.5">{rule.label}</div>
                          </button>
                        </td>
                        {cappedMatrixConceptIds.map((conceptId) => {
                          const linked = (topologyModel.ruleToConcepts[rule.id] || []).includes(conceptId);
                          const selectedPair = selectedTopologyRule === rule.id && selectedTopologyConcept === conceptId;
                          let cellClass = 'bg-white';
                          if (linked && rule.status === 'resolved') cellClass = 'bg-emerald-100';
                          else if (linked && rule.status === 'active' && ['contradictory', 'suspicious'].includes(rule.semanticQuality?.worst_status)) cellClass = 'bg-red-100';
                          else if (linked && rule.status === 'active' && rule.semanticQuality?.worst_status === 'needs_evidence') cellClass = 'bg-amber-100';
                          else if (linked && rule.status === 'active') cellClass = rule.severity === 'critical' ? 'bg-red-100' : 'bg-orange-100';
                          else if (linked && rule.semanticQuality?.worst_status === 'confirmed') cellClass = 'bg-emerald-50';
                          else if (linked) cellClass = 'bg-blue-50';

                          return (
                            <td key={`${rule.id}-${conceptId}`} className="border-b border-slate-200 px-2 py-2 text-center">
                              <button
                                type="button"
                                onClick={() => {
                                  if (!linked) return;
                                  setSelectedTopologyRule(rule.id);
                                  setSelectedTopologyConcept(conceptId);
                                }}
                                className={`mx-auto flex h-9 w-9 items-center justify-center rounded-lg border text-[11px] font-bold transition-all ${linked ? 'cursor-pointer border-slate-200 hover:scale-105' : 'cursor-default border-slate-100 text-slate-200'} ${cellClass} ${selectedPair ? 'ring-2 ring-slate-900 ring-offset-1' : ''}`}
                                title={linked ? `${rule.id} ↔ ${topologyModel.conceptMap[conceptId]?.fullLabel || conceptId}` : '当前规则未直接命中该概念'}
                              >
                                {linked ? '●' : '·'}
                              </button>
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  };


  const competitionMeta = competition?.competition_meta || {};
  const competitionSummary = competition?.score_summary || {};
  const competitionCharts = competition?.panel_charts || {};
  const competitionItems = competition?.rubric_items || [];
  const topTasks = competition?.top_tasks || [];

  const renderCompetitionOverview = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-purple-50 border border-purple-100 rounded-xl p-4">
          <div className="text-xs text-purple-600 mb-1">当前赛事模板</div>
          <div className="font-bold text-purple-800">{competitionMeta.template_name || '竞赛模式'}</div>
          <div className="text-xs text-purple-600 mt-1">{competitionMeta.matched_alias || '系统自动识别'}</div>
        </div>
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
          <div className="text-xs text-blue-600 mb-1">综合预估得分</div>
          <div className="font-bold text-blue-800">{competitionSummary.weighted_score_text || '—'}</div>
          <div className="text-xs text-blue-600 mt-1">平均单项分：{competitionSummary.average_score ?? '—'}</div>
        </div>
        <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
          <div className="text-xs text-amber-600 mb-1">模板专属维度</div>
          <div className="font-bold text-amber-800 text-sm leading-relaxed">
            {(competitionMeta.exclusive_dimensions || []).map((item) => item.dimension_name).join(' / ') || '—'}
          </div>
        </div>
        <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-4">
          <div className="text-xs text-emerald-600 mb-1">评价重心</div>
          <div className="font-bold text-emerald-800 text-sm leading-relaxed">{competitionMeta.focus_hint || '—'}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-3 text-slate-800 font-bold text-sm"><Radar size={16} className="text-purple-600" /> Rubric 分数雷达图</div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={competitionCharts.radar || []} outerRadius="70%">
                <PolarGrid />
                <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 11 }} />
                <PolarRadiusAxis angle={90} domain={[0, 5]} tickCount={6} />
                <RechartsRadar name="Score" dataKey="score" stroke="#7c3aed" fill="#c4b5fd" fillOpacity={0.45} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-3 text-slate-800 font-bold text-sm"><BarChart3 size={16} className="text-blue-600" /> 维度权重分布</div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={competitionCharts.weight_compare || []} layout="vertical" margin={{ left: 20, right: 10, top: 8, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="dimension" type="category" width={90} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="weight" fill="#60a5fa" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-red-50 border border-red-100 rounded-xl p-4">
          <div className="text-sm font-bold text-red-800 mb-2">高风险维度</div>
          <div className="space-y-2">
            {(competitionSummary.high_risk_dimensions || []).length > 0 ? (competitionSummary.high_risk_dimensions || []).map((item) => (
              <div key={item.dimension_id} className="bg-white rounded-lg border border-red-100 px-3 py-2 text-sm text-red-700">
                {item.dimension_name} · {item.score}/5 · 权重 {item.weight}%
              </div>
            )) : <div className="text-sm text-red-600">暂无高风险维度。</div>}
          </div>
        </div>
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
          <div className="text-sm font-bold text-slate-800 mb-2">物理权重偏移说明</div>
          <p className="text-sm text-slate-600 leading-relaxed">{competitionMeta.expected_shift || '—'}</p>
          <div className="mt-3 text-xs text-slate-500">识别依据：{competitionMeta.recognition_basis || '—'}</div>
        </div>
      </div>
    </div>
  );

  const renderCompetitionDimensions = () => (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-slate-700">
            <tr>
              <th className="px-4 py-3 text-left">维度</th>
              <th className="px-4 py-3 text-left">类别</th>
              <th className="px-4 py-3 text-right">权重</th>
              <th className="px-4 py-3 text-right">分数</th>
              <th className="px-4 py-3 text-left">缺失证据</th>
              <th className="px-4 py-3 text-left">24h 修复</th>
              <th className="px-4 py-3 text-left">72h 修复</th>
            </tr>
          </thead>
          <tbody>
            {competitionItems.map((item) => (
              <tr key={item.dimension_id} className="border-t border-slate-100 align-top">
                <td className="px-4 py-3 font-medium text-slate-800">{item.dimension_name}</td>
                <td className="px-4 py-3 text-slate-500">{item.category === 'exclusive' ? '赛事专属' : '通用'}</td>
                <td className="px-4 py-3 text-right text-slate-600">{item.weight}%</td>
                <td className="px-4 py-3 text-right">
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-bold ${item.estimated_score <= 2 ? 'bg-red-100 text-red-700' : item.estimated_score < 3.5 ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}`}>
                    {item.estimated_score}/5
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-600 whitespace-pre-wrap">{(item.missing_evidence || []).join('；') || '暂无明显缺口'}</td>
                <td className="px-4 py-3 text-slate-600 whitespace-pre-wrap">{item.minimal_fix_24h || '—'}</td>
                <td className="px-4 py-3 text-slate-600 whitespace-pre-wrap">{item.minimal_fix_72h || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderCompetitionTasks = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {topTasks.map((task, idx) => (
          <div key={`${task.task_desc}-${idx}`} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div className="font-bold text-purple-700 text-sm mb-2">{task.task_desc}</div>
            <div className="text-xs text-slate-500 mb-2">{task.timeframe} · {task.roi_reason}</div>
            <div className="text-sm text-slate-600 leading-relaxed">{task.template_example}</div>
          </div>
        ))}
      </div>

      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
        <div className="text-sm font-bold text-slate-800 mb-2">评委追问预演</div>
        <ul className="list-disc pl-5 space-y-2 text-sm text-slate-600">
          {(competition.quick_questions || []).map((q, idx) => <li key={`${q}-${idx}`}>{q}</li>)}
        </ul>
      </div>
    </div>
  );

  const modeTabs = [
    project && { id: 'project', label: '项目', icon: Briefcase, color: 'text-orange-600' },
    competition && { id: 'competition', label: '竞赛', icon: Trophy, color: 'text-purple-600' },
  ].filter(Boolean);

  return (
    <div className="fixed inset-0 z-[120]">
      <div className="absolute inset-0 bg-slate-900/30 backdrop-blur-[1px]" onClick={() => onClose?.()} />
      <div className="absolute inset-0 flex items-center justify-center p-4 md:p-6">
        <div className="relative w-full max-w-6xl h-[88vh] rounded-2xl border border-amber-200 bg-white shadow-2xl overflow-hidden">
          <div className="sticky top-0 z-10 flex items-center justify-between gap-3 border-b border-slate-200 bg-white/95 px-4 py-3 backdrop-blur">
            <div>
              <div className="text-sm font-bold text-slate-800">文档分析面板</div>
              <div className="text-xs text-slate-500">项目 / 竞赛快照会随对话持续更新</div>
            </div>
            <button
              type="button"
              onClick={() => onClose?.()}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-semibold text-slate-600 hover:bg-slate-50"
            >
              <X size={16} /> 关闭
            </button>
          </div>
          <div className="h-[calc(88vh-61px)] overflow-y-auto p-4">
            {!project && !competition && (
              <div className="text-sm text-amber-700">
                当前已绑定文档，但还没有项目模式/竞赛模式的快照数据。先运行一次对应模式，这里就会自动更新。
              </div>
            )}

            {modeTabs.length > 0 && (
              <div className="flex items-center gap-2 border-b border-slate-200 pb-3 mb-4">
                {modeTabs.map((tab) => {
                  const Icon = tab.icon;
                  const active = activeModeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveModeTab(tab.id)}
                      className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border text-sm font-semibold transition-colors ${active ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}`}
                    >
                      <Icon size={16} className={active ? 'text-white' : tab.color} />
                      {tab.label}
                    </button>
                  );
                })}
              </div>
            )}

            {activeModeTab === 'project' && project && (
              <div className="space-y-4 mb-5">
                <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
                  <Briefcase size={18} className="text-orange-600" />
                  <h4 className="font-bold text-slate-800 text-base">项目模式快照</h4>
                </div>

                {renderProjectStageFlow()}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-orange-50 border border-orange-100 rounded-xl p-3 shadow-sm">
                    <div className="text-sm font-semibold text-orange-800 mb-1">逻辑缺陷</div>
                    <div className="text-sm text-orange-700 leading-relaxed">{project.logic_flaw || '暂无'}</div>
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 shadow-sm">
                    <div className="text-sm font-semibold text-slate-800 mb-1">证据缺口</div>
                    <div className="text-sm text-slate-600 leading-relaxed">{project.evidence_gap || '暂无'}</div>
                  </div>
                </div>

                <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 shadow-sm">
                  <div className="text-sm font-bold text-emerald-800 mb-2">唯一核心突破任务</div>
                  <div className="text-sm text-emerald-700 mb-3">{project.only_one_task || '暂无'}</div>
                  <div className="text-xs text-emerald-900 bg-white rounded-lg p-3 border border-emerald-100 shadow-sm">
                    <strong>验收标准：</strong> {project.acceptance_criteria || '暂无'}
                  </div>
                </div>

                <div className="mt-6 border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                  <div className="flex border-b border-slate-200 bg-white">
                    {/* 修改：重命名 Tab，突出阶段规则检视 */}
                    <button
                      onClick={() => setProjectTab('rules')}
                      className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 transition-colors relative ${projectTab === 'rules' ? 'text-blue-600 bg-blue-50/50' : 'text-slate-500 hover:bg-slate-50'}`}
                    >
                      <ClipboardList size={16} /> 阶段规则检视
                      {projectTab === 'rules' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-600" />}
                    </button>
                    <button
                      onClick={() => setProjectTab('topology')}
                      className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 transition-colors relative ${projectTab === 'topology' ? 'text-blue-600 bg-blue-50/50' : 'text-slate-500 hover:bg-slate-50'}`}
                    >
                      <Network size={16} /> 逻辑拓扑结构图
                      {projectTab === 'topology' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-600" />}
                    </button>
                  </div>
                  <div>{projectTab === 'rules' ? renderStageRules() : renderHypergraph()}</div>
                </div>
              </div>
            )}

            {activeModeTab === 'competition' && competition && (
              <div className="space-y-4">
                <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
                  <Trophy size={18} className="text-purple-600" />
                  <h4 className="font-bold text-slate-800 text-base">竞赛模式快照</h4>
                </div>

                <div className="flex flex-wrap gap-2 border border-slate-200 rounded-xl bg-slate-50 p-2">
                  {[
                    { id: 'overview', label: '总览', icon: Trophy },
                    { id: 'dimensions', label: '逐项评分', icon: ClipboardList },
                    { id: 'tasks', label: '冲刺任务', icon: BarChart3 },
                  ].map((tab) => {
                    const Icon = tab.icon;
                    const active = competitionTab === tab.id;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setCompetitionTab(tab.id)}
                        className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold transition-colors ${active ? 'bg-white text-purple-700 shadow-sm border border-purple-100' : 'text-slate-600 hover:bg-white'}`}
                      >
                        <Icon size={15} /> {tab.label}
                      </button>
                    );
                  })}
                </div>

                {competitionTab === 'overview' && renderCompetitionOverview()}
                {competitionTab === 'dimensions' && renderCompetitionDimensions()}
                {competitionTab === 'tasks' && renderCompetitionTasks()}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}