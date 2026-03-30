import React, { useMemo, useRef, useEffect, useState } from 'react';
import { Briefcase, Trophy, Network, AlertTriangle, ShieldAlert } from 'lucide-react';
import ForceGraph2D from 'react-force-graph-2d';

export default function SnapshotOverlay({ open, snapshot }) {
  const containerRef = useRef(null);
  const fgRef = useRef(null);
  
  // 【新增】Tab 切换状态，默认为预警条目
  const [activeTab, setActiveTab] = useState('alerts'); 

  const project = snapshot?.project?.generated_content;
  const hypergraph = snapshot?.project?.hypergraph_data || snapshot?.hypergraph_data; 
  const competition = snapshot?.competition?.generated_content;
  
  // 【新增】从后端数据中安全提取 alerts
  const alerts = hypergraph?.alerts || [];

  const formatNodeName = (name) => {
    // 中英文映射字典，将后端的抽象 Key 转为可读中文
    const map = {
      Target_Customer: "目标客群", Value_Proposition: "价值主张", Marketing_Channel: "营销渠道", 
      Revenue_Model: "收入模型", Cost_Structure: "成本结构", Core_Pain_Point: "核心痛点", 
      Price: "产品定价", LTV: "客户终身价值", CAC: "获客成本", Startup_Capital: "启动资金", 
      Account_Period: "账期", Seed_Users: "种子用户", Tech_Route: "技术路线", 
      Team_Background: "团队背景", Competitor_Pool: "竞争对手", IP: "知识产权", 
      Fulfill_Cost: "履约成本", Supplier_Network: "供应链", Control_Experiment: "对照实验", 
      TAM: "总潜在市场", SAM: "可服务市场", SOM: "可获得市场", Usage_Frequency: "使用频次", 
      Milestone_Plan: "里程碑", Policy_Constraints: "政策约束",
      
      Core_Business_Loop: "商业核心闭环", Customer_Value_Misalignment: "客群与价值错位",
      Channel_Physical_Access: "渠道物理触达", Willingness_To_Pay: "支付意愿支撑",
      Market_Reachability: "市场规模漏斗", Frequency_Mismatch: "频次与收入错配",
      Unit_Economics: "单位经济模型", Pricing_Space: "定价与利润空间",
      Cash_Flow_Health: "现金流健康度", Financial_Reasonableness: "财务预测合理性",
      Supply_Chain_Sync: "供应链履约交付", Cold_Start_Engine: "冷启动引擎",
      R_D_Team_Match: "研发团队匹配", Resource_Feasibility: "资源方案可行性",
      Tech_Barrier: "技术护城河", Real_Competition: "真实竞争格局",
      Narrative_Causality: "叙事因果逻辑", Innovation_Verification: "创新差异化验证",
      Compliance_Ethics: "合规与伦理限制", Social_Value_Translation: "社会价值转化"
    };
    return map[name] || name;
  };

  // 【新增函数】专门用来清洗供视觉展示的文本
  // 清洗供视觉展示的文本，支持中英文冒号，并截断长文本
  const getVisualLabel = (rawId) => {
    if (!rawId) return '';
    let text = String(rawId);
    
    if (text.includes(': ')) {
      text = text.split(': ')[1];
    } else if (text.includes(':')) {
      text = text.split(':')[1];
    } else if (text.includes('：')) {
      // 【核心增加】：兼容大模型常用的中文冒号
      text = text.split('：')[1];
    } else {
      text = formatNodeName(text);
    }
    
    // 限制画布上的文字长度，最多显示14个字符
    if (text.length > 14) {
      return text.substring(0, 14) + '...';
    }
    return text;
  };

  const graphData = useMemo(() => {
    if (!hypergraph) return { nodes: [], links: [] };
    const nodesData = [];
    const linksData = [];
    const nodeSet = new Set(); 
    
    const discreteNodes = hypergraph.nodes || [];
    const edges = hypergraph.edges || {};

    // 1. 离散节点
    discreteNodes.forEach(nodeName => {
      // 保持原始 ID 进行数据存储
      if (!nodeSet.has(nodeName)) {
        nodesData.push({ id: nodeName, group: 1 });
        nodeSet.add(nodeName);
      }
    });

    // 2. 超边展开逻辑
    Object.entries(edges).forEach(([edgeName, linkedNodes]) => {
      const formattedEdge = formatNodeName(edgeName);
      
      // 注意：不要清洗 ID，保持带前缀的状态以维持全网图谱的连通唯一性
      linkedNodes.forEach(nodeRawId => {
        if (!nodeSet.has(nodeRawId)) {
          nodesData.push({ id: nodeRawId, group: 2 }); 
          nodeSet.add(nodeRawId);
        }
      });

      for (let i = 0; i < linkedNodes.length; i++) {
        for (let j = i + 1; j < linkedNodes.length; j++) {
          linksData.push({
            source: linkedNodes[i],
            target: linkedNodes[j],
            label: formattedEdge
          });
        }
      }
    });

    return { nodes: nodesData, links: linksData };
  }, [hypergraph]);

  // 【新增】调整物理引擎参数，让节点散开
  useEffect(() => {
    if (open && fgRef.current) {
      // strength(-400) 代表极强的电荷斥力，默认只有 -30
      fgRef.current.d3Force('charge').strength(-400);
      // distance(80) 拉长连线距离，默认只有 30
      fgRef.current.d3Force('link').distance(80);
    }
  }, [open, graphData]);

  if (!open) return null;

  // 【新增】渲染超图预警列表
  const renderAlerts = () => {
    if (alerts.length === 0) {
      return (
        <div className="py-12 text-center text-slate-400 bg-white rounded-b-xl">
          <ShieldAlert size={36} className="mx-auto mb-3 opacity-20" />
          <p className="text-sm">太棒了！当前暂无超图预警，或暂未提取到足够要素。</p>
        </div>
      );
    }

    // 映射后端 severity 到 前端的 高/中/低 视觉样式
    const severityMap = {
      critical: { label: '高危', color: 'bg-red-100 text-red-700 border-red-200' },
      high: { label: '高风险', color: 'bg-orange-100 text-orange-700 border-orange-200' },
      medium: { label: '中风险', color: 'bg-amber-100 text-amber-700 border-amber-200' },
      low: { label: '低风险', color: 'bg-blue-100 text-blue-700 border-blue-200' }
    };

    return (
      <div className="space-y-3 p-4 bg-slate-50 max-h-80 overflow-y-auto custom-scrollbar rounded-b-xl">
        {alerts.map((alert, idx) => {
          // 将后端的 R1-R20 映射为面板显示的 H1-H20
          const ruleId = alert.rule ? alert.rule.replace('R', 'H') : `H${idx + 1}`;
          const sev = severityMap[alert.severity] || severityMap.medium;

          return (
            <div key={idx} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-all">
              <div className="flex items-start justify-between gap-4 mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-slate-500 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded text-xs">
                    {ruleId}
                  </span>
                  <h6 className="font-bold text-slate-800 text-sm">{alert.name}</h6>
                </div>
                <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${sev.color}`}>
                  {sev.label}
                </span>
              </div>
              <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
                {alert.issue}
              </p>
            </div>
          );
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
         <div className="absolute top-2 left-2 z-10 text-[10px] text-slate-400 font-medium bg-white/80 px-2 py-1 rounded pointer-events-none">
           支持鼠标滚轮缩放与拖拽
         </div>
         <div ref={containerRef} className="w-full h-80 cursor-move">
           {/* 这里原封不动保留你上一轮写好的定制 <ForceGraph2D /> 代码 */}
           <ForceGraph2D
             ref={fgRef}
             width={containerRef.current?.offsetWidth || 800}
             height={320}
             graphData={graphData}
             d3VelocityDecay={0.1}
             linkCanvasObject={(link, ctx, globalScale) => {
               const start = link.source;
               const end = link.target;
               if (!start || !end || typeof start.x !== 'number') return;
               ctx.beginPath();
               ctx.moveTo(start.x, start.y);
               ctx.lineTo(end.x, end.y);
               ctx.strokeStyle = 'rgba(203, 213, 225, 0.4)';
               ctx.lineWidth = 1.5 / globalScale;
               ctx.stroke();
               if (link.label) {
                 const midX = start.x + (end.x - start.x) / 2;
                 const midY = start.y + (end.y - start.y) / 2;
                 const fontSize = 10 / globalScale;
                 ctx.font = `${fontSize}px Sans-Serif`;
                 const textWidth = ctx.measureText(link.label).width;
                 ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
                 ctx.fillRect(midX - textWidth / 2 - 2/globalScale, midY - fontSize / 2 - 2/globalScale, textWidth + 4/globalScale, fontSize + 4/globalScale);
                 ctx.fillStyle = '#94a3b8';
                 ctx.textAlign = 'center';
                 ctx.textBaseline = 'middle';
                 ctx.fillText(link.label, midX, midY);
               }
             }}
             nodeCanvasObject={(node, ctx, globalScale) => {
              // 【关键修改】：调用洗去前缀的标签
               const label = getVisualLabel(node.id); 
               
               const fontSize = 12 / globalScale;
               ctx.font = `${fontSize}px Sans-Serif`;
               const textWidth = ctx.measureText(label).width; // 根据洗净后的文字计算宽度
               
               const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 1.2); 
               const x = node.x - bckgDimensions[0] / 2;

               
               const y = node.y - bckgDimensions[1] / 2;
               const w = bckgDimensions[0];
               const h = bckgDimensions[1];
               const r = 4 / globalScale;
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
               ctx.fillStyle = node.group === 1 ? 'rgba(241, 245, 249, 0.95)' : 'rgba(239, 246, 255, 0.95)';
               ctx.fill();
               ctx.strokeStyle = node.group === 1 ? '#cbd5e1' : '#3b82f6';
               ctx.lineWidth = 1 / globalScale;
               ctx.stroke();
               ctx.textAlign = 'center';
               ctx.textBaseline = 'middle';
               ctx.fillStyle = node.group === 1 ? '#64748b' : '#1e40af';
               ctx.fillText(label, node.x, node.y);
               node.__bckgDimensions = bckgDimensions;
             }}
             nodePointerAreaPaint={(node, color, ctx) => {
               ctx.fillStyle = color;
               const bckgDimensions = node.__bckgDimensions;
               if (bckgDimensions) {
                 ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, bckgDimensions[0], bckgDimensions[1]);
               } else {
                 ctx.beginPath();
                 ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
                 ctx.fill();
               }
             }}
           />
         </div>
      </div>
    );
  };

  return (
    <div className="absolute left-0 right-0 top-full z-30 mt-2 px-4">
      <div className="mx-auto max-w-5xl rounded-2xl border border-amber-200 bg-white shadow-2xl p-4 max-h-[75vh] overflow-y-auto">
        {!project && !competition && (
          <div className="text-sm text-amber-700">
            当前已绑定文档，但还没有项目模式/竞赛模式的快照数据。先运行一次对应模式，这里就会自动更新。
          </div>
        )}
        
        {project && (
          <div className="space-y-4 mb-5">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
              <Briefcase size={18} className="text-orange-600" />
              <h4 className="font-bold text-slate-800 text-base">项目模式快照</h4>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-orange-50 border border-orange-100 rounded-xl p-3 shadow-sm hover:shadow-md transition-shadow">
                <div className="text-sm font-semibold text-orange-800 mb-1">逻辑缺陷</div>
                <div className="text-sm text-orange-700 leading-relaxed">{project.logic_flaw || '暂无'}</div>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 shadow-sm hover:shadow-md transition-shadow">
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

            {/* 【核心增加】：双标签页区域 */}
            <div className="mt-6 border border-slate-200 rounded-xl overflow-hidden shadow-sm">
              <div className="flex border-b border-slate-200 bg-white">
                <button
                  onClick={() => setActiveTab('alerts')}
                  className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 transition-colors relative ${
                    activeTab === 'alerts' ? 'text-red-600 bg-red-50/50' : 'text-slate-500 hover:bg-slate-50'
                  }`}
                >
                  <AlertTriangle size={16} /> 
                  底层超图预警
                  {alerts.length > 0 && (
                    <span className="bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full absolute right-4">
                      {alerts.length}
                    </span>
                  )}
                  {activeTab === 'alerts' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-red-600" />}
                </button>

                <button
                  onClick={() => setActiveTab('topology')}
                  className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 transition-colors relative ${
                    activeTab === 'topology' ? 'text-blue-600 bg-blue-50/50' : 'text-slate-500 hover:bg-slate-50'
                  }`}
                >
                  <Network size={16} /> 
                  逻辑拓扑结构图
                  {activeTab === 'topology' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-600" />}
                </button>
              </div>

              {/* 内容渲染区 */}
              <div>
                {activeTab === 'alerts' ? renderAlerts() : renderHypergraph()}
              </div>
            </div>

          </div>
        )}

        {competition && (
           <div className="space-y-4 pt-2">
           <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
             <Trophy size={18} className="text-purple-600" />
             <h4 className="font-bold text-slate-800 text-base">竞赛模式快照</h4>
           </div>
           
           <div className="bg-purple-50 border border-purple-100 rounded-xl p-4 shadow-sm">
             <div className="text-sm font-bold text-purple-800 mb-2">Rubric 评分分布</div>
             <div className="text-sm text-purple-700 whitespace-pre-wrap leading-relaxed">{competition.rubric_scores || '暂无'}</div>
           </div>
           <div className="bg-red-50 border border-red-100 rounded-xl p-4 shadow-sm">
             <div className="text-sm font-bold text-red-800 mb-2">扣分实证追踪</div>
             <div className="text-sm text-red-700 whitespace-pre-wrap leading-relaxed">{competition.deduction_evidence || '暂无'}</div>
           </div>
           
           {Array.isArray(competition.top_tasks) && competition.top_tasks.length > 0 && (
             <div className="space-y-3 mt-4">
               <div className="text-sm font-bold text-slate-800">Top 提分规划 (ROI驱动)</div>
               {competition.top_tasks.map((task, idx) => (
                 <div key={`${task.task_desc}-${idx}`} className="bg-slate-50 border border-slate-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
                   <div className="font-bold text-purple-700 text-sm mb-2">{task.task_desc}</div>
                   <div className="text-xs font-semibold text-slate-600 mb-2 flex items-center gap-2 bg-white px-2 py-1 rounded border border-slate-100 w-fit">
                     <span>⏱ {task.timeframe}</span> 
                     <span className="text-slate-300">|</span> 
                     <span>💡 {task.roi_reason}</span>
                   </div>
                   <div className="text-xs text-slate-600 bg-white rounded-lg border border-slate-200 p-3 shadow-inner leading-relaxed">
                     {task.template_example}
                   </div>
                 </div>
               ))}
             </div>
           )}
         </div>
        )}
      </div>
    </div>
  );
}