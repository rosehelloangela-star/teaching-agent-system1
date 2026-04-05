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
  "System": {"name": "图谱元素过少", "severity": "high", "weight": 18},
  "R1": {"name": "全局逻辑散架", "severity": "critical", "weight": 30},
  "R2": {"name": "技术与商业双轨孤岛", "severity": "critical", "weight": 30},
  "R3": {"name": "叙事因果断裂", "severity": "high", "weight": 18},
  "R4": {"name": "合规逻辑游离", "severity": "medium", "weight": 10},
  "R5": {"name": "闭环要素严重缺失", "severity": "high", "weight": 18},
  "R6": {"name": "渠道与客群脱节", "severity": "medium", "weight": 10},
  "R7": {"name": "支付意愿支撑不足", "severity": "high", "weight": 18},
  "R8": {"name": "无竞争对手幻觉", "severity": "critical", "weight": 30},
  "R9": {"name": "市场漏斗断层", "severity": "medium", "weight": 10},
  "R10": {"name": "创新缺乏竞争对标", "severity": "medium", "weight": 10},
  "R11": {"name": "单位经济模型崩塌", "severity": "critical", "weight": 30},
  "R12": {"name": "利润空间黑盒", "severity": "high", "weight": 18},
  "R13": {"name": "现金流断裂高危", "severity": "critical", "weight": 30},
  "R14": {"name": "供应链脱离业务", "severity": "high", "weight": 18},
  "R15": {"name": "冷启动策略空转", "severity": "medium", "weight": 10},
  "R16": {"name": "技术壁垒无团队支撑", "severity": "medium", "weight": 10},
  "R17": {"name": "执行方案空壳", "severity": "medium", "weight": 10},
  "R18": {"name": "财务预测漂浮", "severity": "high", "weight": 18},
  "R19": {"name": "频次与收入模型错配", "severity": "high", "weight": 18},
  "R20": {"name": "公益属性过重", "severity": "medium", "weight": 10},
};

export default function SnapshotOverlay({ open, snapshot, onClose }) {
  const containerRef = useRef(null);
  const fgRef = useRef(null);

  const [activeModeTab, setActiveModeTab] = useState('project');
  // 默认 Tab 改为 'rules'
  const [projectTab, setProjectTab] = useState('rules');
  const [competitionTab, setCompetitionTab] = useState('overview');

  const project = snapshot?.project?.generated_content;
  const hypergraph = snapshot?.project?.hypergraph_data || snapshot?.hypergraph_data;
  const projectStageFlow = snapshot?.project?.stage_flow || null;
  const competition = snapshot?.competition?.generated_content;
  
  const stageFollowups = projectStageFlow?.current_followup_questions || [];

  useEffect(() => {
    if (competition && !project) setActiveModeTab('competition');
    if (project && !competition) setActiveModeTab('project');
  }, [project, competition]);

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

  // 修改：用完整的阶段规则面板替换原有的底层预警
  const renderStageRules = () => {
    if (!projectStageFlow) return null;
    
    const stages = Object.values(projectStageFlow.stages || {}).sort((a, b) => (a.index || 0) - (b.index || 0));
    const currentStage = stages.find((item) => item.id === projectStageFlow.current_stage_id) || stages[0];
    if (!currentStage) return null;

    const allRuleIds = currentStage.rule_ids || [];
    const activeRuleIds = currentStage.active_rule_ids || [];
    const resolvedRuleIds = currentStage.resolved_rule_ids || [];
    const activeAlerts = currentStage.active_alerts || [];

    if (allRuleIds.length === 0) {
      return (
        <div className="py-12 text-center text-slate-400 bg-white rounded-b-xl">
          <ShieldAlert size={36} className="mx-auto mb-3 opacity-20" />
          <p className="text-sm">太棒了！本阶段暂无需要考核的专项规则。</p>
        </div>
      );
    }

    return (
      <div className="space-y-3 p-4 bg-slate-50 max-h-[400px] overflow-y-auto rounded-b-xl">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-bold text-slate-800">本阶段考核规则明细（当前进度影响权重）</span>
        </div>
        {allRuleIds.map(ruleId => {
          const isPassed = resolvedRuleIds.includes(ruleId);
          const activeAlert = activeAlerts.find(a => a.rule === ruleId);
          const meta = RULE_METADATA[ruleId] || { name: `规则 ${ruleId}`, severity: 'medium', weight: 10 };

          const sevMap = {
            critical: { label: `高危 (权重:${meta.weight})`, color: isPassed ? 'text-emerald-700 bg-emerald-100 border-emerald-200' : 'text-red-700 bg-red-100 border-red-200' },
            high: { label: `高风险 (权重:${meta.weight})`, color: isPassed ? 'text-emerald-700 bg-emerald-100 border-emerald-200' : 'text-orange-700 bg-orange-100 border-orange-200' },
            medium: { label: `中风险 (权重:${meta.weight})`, color: isPassed ? 'text-emerald-700 bg-emerald-100 border-emerald-200' : 'text-amber-700 bg-amber-100 border-amber-200' },
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
                 <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${sev.color}`}>
                   {sev.label}
                 </span>
               </div>
               {!isPassed && activeAlert && (
                 <p className="mt-2 text-sm text-slate-600 leading-relaxed bg-red-50/50 p-2.5 rounded-lg border border-red-100">
                   {activeAlert.issue}
                 </p>
               )}
               {isPassed && (
                 <p className="mt-2 text-xs text-emerald-600 font-semibold flex items-center gap-1">
                   ✓ 该规则要素已被证实，成功突破
                 </p>
               )}
            </div>
          )
        })}
      </div>
    );
  };

  const renderHypergraph = () => {
    if (graphData.nodes.length === 0) {
      return (
        <div className="py-12 bg-white rounded-b-xl text-center">
          <p className="text-sm text-slate-400">暂未提取到有效的商业要素连接。</p>
        </div>
      );
    }

    return (
      <div className="w-full bg-white rounded-b-xl overflow-hidden relative">
        <div className="absolute top-2 left-2 z-10 text-[10px] text-slate-400 font-medium bg-white/80 px-2 py-1 rounded pointer-events-none border border-slate-100 shadow-sm">
          图谱已锁定 · 支持鼠标滚轮缩放与拖拽
        </div>
        <div ref={containerRef} className="w-full h-80 cursor-move">
          <ForceGraph2D
            ref={fgRef}
            width={containerRef.current?.offsetWidth || 800}
            height={320}
            graphData={graphData}
            d3VelocityDecay={0.1}
            // 修改：加入预热和锁定帧，防止无限乱弹。100帧后停止计算并自动剧中缩放
            cooldownTicks={100}
            onEngineStop={() => fgRef.current?.zoomToFit(400, 30)}
            
            linkColor={() => '#cbd5e1'}
            linkWidth={1.5}
            nodeCanvasObject={(node, ctx, globalScale) => {
              const isRelation = node.type === 'relation';
              const label = isRelation ? node.label : getVisualLabel(node.id);

              const fontSize = isRelation ? 12 / globalScale : 14 / globalScale;
              ctx.font = `${isRelation ? '700' : '600'} ${fontSize}px Sans-Serif`;
              const textWidth = ctx.measureText(label).width;

              const paddingX = isRelation ? 24 : 36;
              const paddingY = isRelation ? 16 : 24;
              const w = textWidth + paddingX / globalScale;
              const h = fontSize + paddingY / globalScale;

              const x = node.x - w / 2;
              const y = node.y - h / 2;
              const r = isRelation ? h / 2 : 8 / globalScale;

              ctx.beginPath();
              ctx.moveTo(x + r, y);
              ctx.lineTo(x + w - r, y);
              ctx.quadraticCurveTo(x + w, y, x + w, y + r);
              ctx.lineTo(x + w, y + h - r);
              ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
              ctx.lineTo(x + r, y + h);
              ctx.quadraticCurveTo(x, y + h, x, y + h - r);
              ctx.lineTo(x, y + r);
              ctx.quadraticCurveTo(x, y, x + r, y);
              ctx.closePath();

              if (isRelation) {
                ctx.fillStyle = 'rgba(245, 158, 11, 0.95)';
                ctx.strokeStyle = '#d97706';
                ctx.fillStyleText = '#ffffff';
              } else {
                ctx.fillStyle = node.group === 1 ? 'rgba(241, 245, 249, 0.95)' : 'rgba(239, 246, 255, 0.95)';
                ctx.strokeStyle = node.group === 1 ? '#cbd5e1' : '#3b82f6';
                ctx.fillStyleText = node.group === 1 ? '#64748b' : '#1e40af';
              }

              ctx.fill();
              ctx.lineWidth = 1.5 / globalScale;
              ctx.stroke();

              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillStyle = ctx.fillStyleText;
              ctx.fillText(label, node.x, node.y);

              node.__bckgDimensions = [w * globalScale, h * globalScale];
            }}
            nodePointerAreaPaint={(node, color, ctx) => {
              ctx.fillStyle = color;
              const bckgDimensions = node.__bckgDimensions;
              if (bckgDimensions) {
                ctx.fillRect(
                  node.x - bckgDimensions[0] / 2,
                  node.y - bckgDimensions[1] / 2,
                  bckgDimensions[0],
                  bckgDimensions[1]
                );
              } else {
                ctx.beginPath();
                ctx.arc(node.x, node.y, 20, 0, 2 * Math.PI, false);
                ctx.fill();
              }
            }}
          />
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

// export default function SnapshotOverlay({ open, snapshot, onClose }) {
//   const containerRef = useRef(null);
//   const fgRef = useRef(null);

//   const [activeModeTab, setActiveModeTab] = useState('project');
//   const [projectTab, setProjectTab] = useState('alerts');
//   const [competitionTab, setCompetitionTab] = useState('overview');

//   const project = snapshot?.project?.generated_content;
//   const hypergraph = snapshot?.project?.hypergraph_data || snapshot?.hypergraph_data;
//   const projectStageFlow = snapshot?.project?.stage_flow || null;
//   const competition = snapshot?.competition?.generated_content;
//   const alerts = hypergraph?.alerts || [];
//   const stageFocusAlerts = projectStageFlow?.current_stage_alerts || [];
//   const stageFollowups = projectStageFlow?.current_followup_questions || [];

//   useEffect(() => {
//     if (competition && !project) setActiveModeTab('competition');
//     if (project && !competition) setActiveModeTab('project');
//   }, [project, competition]);

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

//   // 🔴 核心改动 1：使用二分图（Bipartite）重构超图数据
//   const graphData = useMemo(() => {
//     if (!hypergraph) return { nodes: [], links: [] };
//     const nodesData = [];
//     const linksData = [];
//     const nodeSet = new Set();
//     const discreteNodes = hypergraph.nodes || [];
//     const edges = hypergraph.edges || {};

//     // 1. 注入实体节点 (Entity Nodes)
//     discreteNodes.forEach((nodeName) => {
//       if (!nodeSet.has(nodeName)) {
//         nodesData.push({ id: nodeName, group: 1, type: 'entity' });
//         nodeSet.add(nodeName);
//       }
//     });

//     // 2. 把“边”提取为关系节点 (Relation Nodes)
//     Object.entries(edges).forEach(([edgeName, linkedNodes]) => {
//       const formattedEdge = formatNodeName(edgeName);
//       const edgeNodeId = `REL_${edgeName}`; // 加前缀防止和实体ID重名

//       // 创建“关系节点”
//       nodesData.push({
//         id: edgeNodeId,
//         label: formattedEdge,
//         group: 3,
//         type: 'relation'
//       });

//       linkedNodes.forEach((nodeRawId) => {
//         if (!nodeSet.has(nodeRawId)) {
//           nodesData.push({ id: nodeRawId, group: 2, type: 'entity' });
//           nodeSet.add(nodeRawId);
//         }
//         // 将实体节点与关系节点相连，不再互相连，极大减少连线数量！
//         linksData.push({
//           source: nodeRawId,
//           target: edgeNodeId,
//         });
//       });
//     });

//     return { nodes: nodesData, links: linksData };
//   }, [hypergraph]);

//   // 🔴 核心改动 2：调整物理引擎参数，适配星型拓扑
//   useEffect(() => {
//     if (open && fgRef.current) {
//       // 斥力适当减小，因为不再有两两相连的紧凑拉力
//       fgRef.current.d3Force('charge').strength(-800);
//       // 连线距离调短，让实体紧紧围绕在“关系节点”周围
//       fgRef.current.d3Force('link').distance(90);
//       fgRef.current.d3VelocityDecay(0.15);
//     }
//   }, [open, graphData]);

//   useEffect(() => {
//     if (!open) return undefined;

//     const previousOverflow = document.body.style.overflow;
//     document.body.style.overflow = 'hidden';

//     const handleKeyDown = (event) => {
//       if (event.key === 'Escape') {
//         onClose?.();
//       }
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
//         <div className="bg-amber-50 border border-amber-100 rounded-xl p-4 shadow-sm">
//           <div className="flex items-start justify-between gap-4 flex-wrap">
//             <div>
//               <div className="text-xs font-bold text-amber-600 mb-1">当前阶段</div>
//               <div className="text-base font-bold text-slate-800">
//                 第{projectStageFlow.current_stage_index}阶段【{projectStageFlow.current_stage_label}】
//               </div>
//               <div className="text-sm text-slate-600 mt-1 leading-relaxed">
//                 {currentStage?.goal || currentStage?.coach_hint || projectStageFlow.current_stage_entry_message || '系统将优先围绕当前阶段推进。'}
//               </div>
//             </div>
//             <div className="rounded-xl bg-white border border-amber-200 px-4 py-3 min-w-[120px] text-right">
//               <div className="text-[11px] text-amber-600 font-semibold">阶段进度</div>
//               <div className="text-2xl font-bold text-amber-700">{currentStage?.progress_pct ?? 0}%</div>
//               <div className="text-[11px] text-slate-500">门槛 {currentStage?.pass_threshold ?? 80}%</div>
//             </div>
//           </div>

//           {projectStageFlow.milestone_message ? (
//             <div className="mt-3 rounded-xl bg-white border border-amber-200 p-3 text-sm text-amber-700">
//               🎉 {projectStageFlow.milestone_message}
//             </div>
//           ) : null}


//           <div className="mt-3 rounded-xl bg-white border border-amber-100 p-3">
//             <div className="text-xs font-bold text-amber-700 mb-1">当前阶段进阶条件</div>
//             <div className="text-xs text-slate-600 leading-relaxed">
//               进度≥{currentStage?.pass_threshold ?? 80}% + 关键高危规则控制在允许范围内 + 结构锚点达到要求
//             </div>
//             {blockers.length > 0 ? (
//               <div className="mt-2 space-y-1.5">
//                 {blockers.map((item, idx) => (
//                   <div key={`${item.code}-${idx}`} className="text-xs text-slate-700 leading-relaxed">
//                     <span className="font-semibold text-amber-700 mr-1">• {item.label}</span>
//                     {item.detail}
//                   </div>
//                 ))}
//               </div>
//             ) : (
//               <div className="mt-2 text-xs text-emerald-700 font-semibold">当前阶段已满足进阶条件，等待系统切换到下一阶段。</div>
//             )}
//           </div>
//         </div>

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

//   const renderAlerts = () => {
//     if (alerts.length === 0) {
//       return (
//         <div className="py-12 text-center text-slate-400 bg-white rounded-b-xl">
//           <ShieldAlert size={36} className="mx-auto mb-3 opacity-20" />
//           <p className="text-sm">太棒了！当前暂无超图预警，或暂未提取到足够要素。</p>
//         </div>
//       );
//     }

//     const severityMap = {
//       critical: { label: '高危', color: 'bg-red-100 text-red-700 border-red-200' },
//       high: { label: '高风险', color: 'bg-orange-100 text-orange-700 border-orange-200' },
//       medium: { label: '中风险', color: 'bg-amber-100 text-amber-700 border-amber-200' },
//       low: { label: '低风险', color: 'bg-blue-100 text-blue-700 border-blue-200' },
//     };

//     return (
//       <div className="space-y-3 p-4 bg-slate-50 max-h-80 overflow-y-auto rounded-b-xl">
//         {stageFocusAlerts.length > 0 && (
//           <div className="bg-orange-50 border border-orange-100 rounded-xl p-3">
//             <div className="text-xs font-bold text-orange-700 mb-2">当前阶段重点预警</div>
//             <div className="flex flex-wrap gap-2">
//               {stageFocusAlerts.map((alert, idx) => (
//                 <span key={`${alert.rule}-${idx}`} className="inline-flex items-center gap-1 rounded-full bg-white border border-orange-200 px-2.5 py-1 text-xs text-orange-700">
//                   {alert.rule} · {alert.name}
//                 </span>
//               ))}
//             </div>
//           </div>
//         )}
//         {alerts.map((alert, idx) => {
//           const ruleId = alert.rule ? alert.rule.replace('R', 'H') : `H${idx + 1}`;
//           const sev = severityMap[alert.severity] || severityMap.medium;
//           return (
//             <div key={`${ruleId}-${idx}`} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-all">
//               <div className="flex items-start justify-between gap-4 mb-2">
//                 <div className="flex items-center gap-2">
//                   <span className="font-mono font-bold text-slate-500 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded text-xs">{ruleId}</span>
//                   <h6 className="font-bold text-slate-800 text-sm">{alert.name}</h6>
//                 </div>
//                 <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${sev.color}`}>{sev.label}</span>
//               </div>
//               <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">{alert.issue}</p>
//             </div>
//           );
//         })}
//       </div>
//     );
//   };

//   const renderHypergraph = () => {
//     if (graphData.nodes.length === 0) {
//       return (
//         <div className="py-12 bg-white rounded-b-xl text-center">
//           <p className="text-sm text-slate-400">暂未提取到有效的商业要素连接。</p>
//         </div>
//       );
//     }

//     return (
//       <div className="w-full bg-white rounded-b-xl overflow-hidden relative">
//         <div className="absolute top-2 left-2 z-10 text-[10px] text-slate-400 font-medium bg-white/80 px-2 py-1 rounded pointer-events-none">
//           支持鼠标滚轮缩放与拖拽
//         </div>
//         <div ref={containerRef} className="w-full h-80 cursor-move">
//           <ForceGraph2D
//             ref={fgRef}
//             width={containerRef.current?.offsetWidth || 800}
//             height={320}
//             graphData={graphData}
//             d3VelocityDecay={0.1}
//             // 🔴 核心改动 3：去除 linkCanvasObject，使用默认线条即可。不需要在线上写字了！
//             linkColor={() => '#cbd5e1'}
//             linkWidth={1.5}

//             // 🔴 核心改动 4：节点渲染区分“实体”和“关系”
//             nodeCanvasObject={(node, ctx, globalScale) => {
//               const isRelation = node.type === 'relation';
//               const label = isRelation ? node.label : getVisualLabel(node.id);

//               const fontSize = isRelation ? 12 / globalScale : 14 / globalScale;
//               ctx.font = `${isRelation ? '700' : '600'} ${fontSize}px Sans-Serif`;
//               const textWidth = ctx.measureText(label).width;

//               const paddingX = isRelation ? 24 : 36;
//               const paddingY = isRelation ? 16 : 24;
//               const w = textWidth + paddingX / globalScale;
//               const h = fontSize + paddingY / globalScale;

//               const x = node.x - w / 2;
//               const y = node.y - h / 2;
//               // 关系节点用全圆角(胶囊形)，实体节点用微圆角
//               const r = isRelation ? h / 2 : 8 / globalScale;

//               // 画路径
//               ctx.beginPath();
//               ctx.moveTo(x + r, y);
//               ctx.lineTo(x + w - r, y);
//               ctx.quadraticCurveTo(x + w, y, x + w, y + r);
//               ctx.lineTo(x + w, y + h - r);
//               ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
//               ctx.lineTo(x + r, y + h);
//               ctx.quadraticCurveTo(x, y + h, x, y + h - r);
//               ctx.lineTo(x, y + r);
//               ctx.quadraticCurveTo(x, y, x + r, y);
//               ctx.closePath();

//               // 填充颜色：关系节点用醒目的暖色，实体用冷色
//               if (isRelation) {
//                 ctx.fillStyle = 'rgba(245, 158, 11, 0.95)'; // Amber
//                 ctx.strokeStyle = '#d97706';
//                 ctx.fillStyleText = '#ffffff';
//               } else {
//                 ctx.fillStyle = node.group === 1 ? 'rgba(241, 245, 249, 0.95)' : 'rgba(239, 246, 255, 0.95)';
//                 ctx.strokeStyle = node.group === 1 ? '#cbd5e1' : '#3b82f6';
//                 ctx.fillStyleText = node.group === 1 ? '#64748b' : '#1e40af';
//               }

//               ctx.fill();
//               ctx.lineWidth = 1.5 / globalScale;
//               ctx.stroke();

//               // 文字
//               ctx.textAlign = 'center';
//               ctx.textBaseline = 'middle';
//               ctx.fillStyle = ctx.fillStyleText;
//               ctx.fillText(label, node.x, node.y);

//               node.__bckgDimensions = [w * globalScale, h * globalScale];
//             }}

//             nodePointerAreaPaint={(node, color, ctx) => {
//               ctx.fillStyle = color;
//               const bckgDimensions = node.__bckgDimensions;
//               if (bckgDimensions) {
//                 ctx.fillRect(
//                   node.x - bckgDimensions[0] / 2,
//                   node.y - bckgDimensions[1] / 2,
//                   bckgDimensions[0],
//                   bckgDimensions[1]
//                 );
//               } else {
//                 ctx.beginPath();
//                 ctx.arc(node.x, node.y, 20, 0, 2 * Math.PI, false);
//                 ctx.fill();
//               }
//             }}
//           />
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
//                     <button
//                       onClick={() => setProjectTab('alerts')}
//                       className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 transition-colors relative ${projectTab === 'alerts' ? 'text-red-600 bg-red-50/50' : 'text-slate-500 hover:bg-slate-50'}`}
//                     >
//                       <AlertTriangle size={16} /> 底层超图预警
//                       {alerts.length > 0 && <span className="bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full absolute right-4">{alerts.length}</span>}
//                       {projectTab === 'alerts' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-red-600" />}
//                     </button>
//                     <button
//                       onClick={() => setProjectTab('topology')}
//                       className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 transition-colors relative ${projectTab === 'topology' ? 'text-blue-600 bg-blue-50/50' : 'text-slate-500 hover:bg-slate-50'}`}
//                     >
//                       <Network size={16} /> 逻辑拓扑结构图
//                       {projectTab === 'topology' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-600" />}
//                     </button>
//                   </div>
//                   <div>{projectTab === 'alerts' ? renderAlerts() : renderHypergraph()}</div>
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
