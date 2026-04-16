import React, { useMemo, useEffect, useRef } from 'react';
import { X, Network, Database } from 'lucide-react';
import ForceGraph2D from 'react-force-graph-2d';

export default function LearningGraphOverlay({ open, kgContext, onClose }) {
  const fgRef = useRef(null);

  const hitNodesSet = useMemo(() => new Set(kgContext?.hit_nodes || []), [kgContext]);

  const COLORS = {
    HIT: '#3b82f6',
    ENTITY: '#10b981',
    CASE: '#94a3b8',
    MISTAKE: '#ef4444',
    LINK: '#cbd5e1',
    LINK_TEXT: '#64748b'
  };

  const graphData = useMemo(() => {
    if (!kgContext || !kgContext.triples) return { nodes: [], links: [] };
    
    const nodeMap = new Map();
    const links = [];

    const registerNode = (id, labels = []) => {
      if (!nodeMap.has(id)) {
        let type = 'ENTITY';
        if (labels?.includes('Mistake')) {
          type = 'MISTAKE';
        } else if (labels?.includes('PositiveCase') || labels?.includes('NegativeCase')) {
          type = 'CASE';
        }

        nodeMap.set(id, { 
          id: id, 
          name: id, 
          isHit: hitNodesSet.has(id),
          nodeType: type 
        });
      }
    };

    kgContext.triples.forEach((t) => {
      registerNode(t.source, t.source_labels);
      registerNode(t.target, t.target_labels);

      if (t.relation === 'COMMON_MISTAKE') {
        nodeMap.get(t.target).nodeType = 'MISTAKE';
      } else if (t.relation === 'HAS_POSITIVE_CASE' || t.relation === 'HAS_NEGATIVE_CASE') {
        nodeMap.get(t.target).nodeType = 'CASE';
      }

      links.push({
        source: t.source,
        target: t.target,
        label: t.relation
      });
    });

    return { 
      nodes: Array.from(nodeMap.values()), 
      links,
      typeMap: nodeMap 
    };
  }, [kgContext, hitNodesSet]);

  useEffect(() => {
    if (open && fgRef.current) {
      fgRef.current.d3Force('charge').strength(-500);
      fgRef.current.d3Force('link').distance(110);
    }
  }, [open, graphData]);

  if (!open) return null;

  const hasData = graphData.nodes.length > 0;

  const getNodeColor = (node) => {
    if (node.isHit) return COLORS.HIT;
    if (node.nodeType === 'MISTAKE') return COLORS.MISTAKE;
    if (node.nodeType === 'CASE') return COLORS.CASE;
    return COLORS.ENTITY;
  };

  const getTextColor = (name) => {
    if (hitNodesSet.has(name)) return 'text-blue-600';
    const node = graphData.typeMap.get(name);
    if (node?.nodeType === 'MISTAKE') return 'text-red-500';
    if (node?.nodeType === 'CASE') return 'text-slate-500';
    return 'text-emerald-600';
  };

  return (
    <div className="fixed inset-0 z-[130]">
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={onClose} />
      <div className="absolute inset-0 flex items-center justify-center p-4 md:p-6">
        <div className="relative w-full max-w-5xl h-[80vh] rounded-2xl bg-white shadow-2xl flex flex-col overflow-hidden">
          
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 bg-slate-50">
            <div className="flex items-center gap-2 text-blue-700">
              <Database size={20} />
              <div>
                <h3 className="font-bold text-slate-800">当前对话的知识图谱拓扑</h3>
                <p className="text-xs text-slate-500">命中概念与实体始终标注，案例与误区请悬停查看</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 rounded-lg hover:bg-slate-200 text-slate-500 transition-colors">
              <X size={20} />
            </button>
          </div>

          {!hasData ? (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400">
              <Network size={48} className="mb-4 opacity-20" />
              <p>暂无相关图谱数据。</p>
            </div>
          ) : (
            <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
              
              <div className="flex-1 border-r border-slate-200 bg-slate-50/50 relative overflow-hidden">
                <div className="absolute top-3 left-3 z-10 flex flex-wrap gap-2 max-w-full">
                  <span className="flex items-center gap-1.5 text-xs bg-white/90 backdrop-blur border border-slate-200 px-2.5 py-1.5 rounded-md shadow-sm text-slate-700 font-medium">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS.HIT }}></span> 命中概念 (常显)
                  </span>
                  <span className="flex items-center gap-1.5 text-xs bg-white/90 backdrop-blur border border-slate-200 px-2.5 py-1.5 rounded-md shadow-sm text-slate-700 font-medium">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS.ENTITY }}></span> 实体 (常显)
                  </span>
                  <span className="flex items-center gap-1.5 text-xs bg-white/90 backdrop-blur border border-slate-200 px-2.5 py-1.5 rounded-md shadow-sm text-slate-700 font-medium">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS.MISTAKE }}></span> 误区 (悬停可见)
                  </span>
                  <span className="flex items-center gap-1.5 text-xs bg-white/90 backdrop-blur border border-slate-200 px-2.5 py-1.5 rounded-md shadow-sm text-slate-700 font-medium">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS.CASE }}></span> 案例 (悬停可见)
                  </span>
                </div>

                <ForceGraph2D
                  ref={fgRef}
                  width={800}
                  height={600}
                  graphData={graphData}
                  nodeLabel="name" // 🌟 确保这个属性存在，用于悬浮时的 Tooltip
                  linkColor={(link) => link.label === 'COMMON_MISTAKE' ? '#fca5a5' : COLORS.LINK}
                  linkDirectionalArrowLength={4}
                  linkDirectionalArrowRelPos={1}
                  nodeCanvasObject={(node, ctx, globalScale) => {
                    const label = node.name;
                    const fontSize = 12 / globalScale;
                    ctx.font = `${fontSize}px Sans-Serif`;
                    
                    const nodeRadius = node.isHit ? 8 : (node.nodeType === 'CASE' ? 5 : 6);
                    const bgColor = getNodeColor(node);

                    // 1. 绘制节点圆形
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, nodeRadius, 0, 2 * Math.PI, false);
                    ctx.fillStyle = bgColor;
                    ctx.fill();
                    ctx.lineWidth = 1.5 / globalScale;
                    ctx.strokeStyle = '#ffffff';
                    ctx.stroke();

                    // 2. 🌟 逻辑判断：仅当是“命中”或“实体”时，才在画布上永久绘制文字
                    if (node.isHit || node.nodeType === 'ENTITY') {
                      ctx.textAlign = 'center';
                      ctx.textBaseline = 'top';
                      ctx.fillStyle = node.isHit ? '#1e293b' : '#475569'; 
                      ctx.fillText(label, node.x, node.y + nodeRadius + (2 / globalScale));
                    }
                  }}
                  linkCanvasObjectMode={() => 'after'}
                  linkCanvasObject={(link, ctx, globalScale) => {
                    const MAX_FONT_SIZE = 4;
                    const start = link.source;
                    const end = link.target;
                    if (typeof start !== 'object' || typeof end !== 'object') return;
                    
                    const textPos = Object.assign(...['x', 'y'].map(c => ({
                      [c]: start[c] + (end[c] - start[c]) / 2 
                    })));
                    const relLink = { x: end.x - start.x, y: end.y - start.y };
                    let textAngle = Math.atan2(relLink.y, relLink.x);
                    if (textAngle > Math.PI / 2) textAngle = -(Math.PI - textAngle);
                    if (textAngle < -Math.PI / 2) textAngle = -(Math.PI + textAngle);
                    
                    ctx.font = `${MAX_FONT_SIZE}px Sans-Serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    
                    const isMistake = link.label === 'COMMON_MISTAKE';
                    const textColor = isMistake ? '#ef4444' : COLORS.LINK_TEXT;

                    ctx.save();
                    ctx.translate(textPos.x, textPos.y);
                    ctx.rotate(textAngle);
                    const textWidth = ctx.measureText(link.label).width;
                    
                    ctx.fillStyle = isMistake ? 'rgba(254, 226, 226, 0.8)' : 'rgba(255, 255, 255, 0.8)';
                    ctx.fillRect(-textWidth/2 - 1, -MAX_FONT_SIZE/2 - 1, textWidth + 2, MAX_FONT_SIZE + 2);
                    
                    ctx.fillStyle = textColor;
                    ctx.fillText(link.label, 0, 0);
                    ctx.restore();
                  }}
                />
              </div>

              <div className="w-full md:w-96 bg-white overflow-y-auto flex flex-col">
                <div className="p-3 bg-slate-50 border-b border-slate-200 font-bold text-sm text-slate-700 sticky top-0 z-10 shadow-sm">
                  知识推理链路明细
                </div>
                <div className="p-4 space-y-3">
                  {kgContext.triples.map((t, idx) => {
                     const isMistakeRel = t.relation === 'COMMON_MISTAKE';
                     return (
                      <div key={idx} className={`bg-slate-50 border rounded-lg p-3 text-sm hover:shadow-md transition-shadow ${isMistakeRel ? 'border-red-200' : 'border-slate-200'}`}>
                        <div className="flex flex-col gap-1.5">
                          <div className={`font-semibold ${getTextColor(t.source)}`}>
                            {t.source}
                          </div>
                          <div className={`flex items-center gap-2 text-xs font-mono pl-2 border-l-2 ${isMistakeRel ? 'text-red-400 border-red-300' : 'text-slate-400 border-slate-300'}`}>
                            —[{t.relation}]→
                          </div>
                          <div className={`font-semibold ${getTextColor(t.target)}`}>
                            {t.target}
                          </div>
                        </div>
                      </div>
                     );
                  })}
                </div>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  );
}