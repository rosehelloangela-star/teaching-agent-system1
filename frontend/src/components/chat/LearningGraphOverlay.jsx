import React, { useMemo, useEffect, useRef } from 'react';
import { X, Network, Database } from 'lucide-react';
import ForceGraph2D from 'react-force-graph-2d';

export default function LearningGraphOverlay({ open, kgContext, onClose }) {
  const fgRef = useRef(null);

  // 🌟 修复点：把 hitNodesSet 提出来，让全组件都能访问到它！
  const hitNodesSet = useMemo(() => new Set(kgContext?.hit_nodes || []), [kgContext]);

  const graphData = useMemo(() => {
    if (!kgContext || !kgContext.triples) return { nodes: [], links: [] };
    
    const nodes = [];
    const links = [];
    const nodeSet = new Set();
    // (这里去掉了原本定义在里面的 hitNodesSet)

    kgContext.triples.forEach((t) => {
      // 添加源节点
      if (!nodeSet.has(t.source)) {
        nodes.push({ 
          id: t.source, 
          name: t.source, 
          isHit: hitNodesSet.has(t.source) 
        });
        nodeSet.add(t.source);
      }
      // 添加目标节点
      if (!nodeSet.has(t.target)) {
        nodes.push({ 
          id: t.target, 
          name: t.target, 
          isHit: hitNodesSet.has(t.target) 
        });
        nodeSet.add(t.target);
      }
      // 添加关系边
      links.push({
        source: t.source,
        target: t.target,
        label: t.relation
      });
    });

    return { nodes, links };
  }, [kgContext, hitNodesSet]); // 🌟 记得在这里的依赖数组加上 hitNodesSet

  // 设置物理引擎参数，让节点散开
  useEffect(() => {
    if (open && fgRef.current) {
      fgRef.current.d3Force('charge').strength(-400);
      fgRef.current.d3Force('link').distance(80);
    }
  }, [open, graphData]);

  if (!open) return null;

  const hasData = graphData.nodes.length > 0;

  return (
    <div className="fixed inset-0 z-[130]">
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={onClose} />
      <div className="absolute inset-0 flex items-center justify-center p-4 md:p-6">
        <div className="relative w-full max-w-5xl h-[80vh] rounded-2xl bg-white shadow-2xl flex flex-col overflow-hidden">
          
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 bg-slate-50">
            <div className="flex items-center gap-2 text-blue-700">
              <Database size={20} />
              <div>
                <h3 className="font-bold text-slate-800">当前对话的知识图谱拓扑</h3>
                <p className="text-xs text-slate-500">基于你提出的概念，系统从数据库中提取的关联知识网络</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 rounded-lg hover:bg-slate-200 text-slate-500 transition-colors">
              <X size={20} />
            </button>
          </div>

          {!hasData ? (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400">
              <Network size={48} className="mb-4 opacity-20" />
              <p>暂无相关图谱数据。试着向我提问具体的双创概念（如 TAM、MVP、股权分配）吧！</p>
            </div>
          ) : (
            <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
              
              {/* 左侧：可视化图谱 */}
              <div className="flex-1 border-r border-slate-200 bg-slate-50/50 relative overflow-hidden">
                <div className="absolute top-3 left-3 z-10 flex gap-2">
                  <span className="flex items-center gap-1 text-xs bg-white border border-slate-200 px-2 py-1 rounded-md shadow-sm">
                    <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> 命中概念
                  </span>
                  <span className="flex items-center gap-1 text-xs bg-white border border-slate-200 px-2 py-1 rounded-md shadow-sm">
                    <span className="w-2.5 h-2.5 rounded-full bg-slate-400"></span> 关联延伸
                  </span>
                </div>
                <ForceGraph2D
                  ref={fgRef}
                  width={800} // 可视区宽度自适应需在外层监听尺寸，这里简写定宽，建议前端使用 ResizeObserver
                  height={600}
                  graphData={graphData}
                  nodeLabel="name"
                  nodeColor={(node) => (node.isHit ? '#3b82f6' : '#94a3b8')}
                  nodeRelSize={6}
                  linkColor={() => '#cbd5e1'}
                  linkDirectionalArrowLength={3.5}
                  linkDirectionalArrowRelPos={1}
                  linkCanvasObjectMode={() => 'after'}
                  linkCanvasObject={(link, ctx, globalScale) => {
                    const MAX_FONT_SIZE = 4;
                    const LABEL_NODE_MARGIN = 12;
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
                    
                    const fontSize = MAX_FONT_SIZE;
                    ctx.font = `${fontSize}px Sans-Serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#64748b';
                    ctx.save();
                    ctx.translate(textPos.x, textPos.y);
                    ctx.rotate(textAngle);
                    ctx.fillText(link.label, 0, 0);
                    ctx.restore();
                  }}
                />
              </div>

              {/* 右侧：三元组明细表格 */}
              <div className="w-full md:w-96 bg-white overflow-y-auto flex flex-col">
                <div className="p-3 bg-slate-50 border-b border-slate-200 font-bold text-sm text-slate-700">
                  知识推理链路明细
                </div>
                <div className="p-4 space-y-3">
                  {kgContext.triples.map((t, idx) => {
                     const isSourceHit = hitNodesSet.has(t.source);
                     const isTargetHit = hitNodesSet.has(t.target);
                     return (
                      <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-sm">
                        <div className="flex flex-col gap-1">
                          <div className={`font-semibold ${isSourceHit ? 'text-blue-600' : 'text-slate-600'}`}>
                            {t.source}
                          </div>
                          <div className="flex items-center gap-2 text-xs text-amber-600 font-mono pl-2 border-l-2 border-amber-300">
                            —[{t.relation}]→
                          </div>
                          <div className={`font-semibold ${isTargetHit ? 'text-blue-600' : 'text-slate-600'}`}>
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