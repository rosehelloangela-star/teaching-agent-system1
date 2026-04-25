import React, { useMemo, useEffect, useRef } from 'react';
import { X, Network, Database } from 'lucide-react';
import ForceGraph2D from 'react-force-graph-2d';

export default function LearningGraphOverlay({ open, kgContext, onClose }) {
  const fgRef = useRef(null);

  const rawTriples = kgContext?.triples || [];
  const triples = useMemo(() => (
    rawTriples
      .filter((t) => t?.source && t?.target && t?.relation)
      .map((t) => ({
        ...t,
        relation: String(t.relation || '').toUpperCase()
      }))
  ), [rawTriples]);

  const hitNodes = kgContext?.hit_nodes || [];
  const expandedNodes = kgContext?.expanded_nodes || [];
  const missingPrereqs = kgContext?.missing_prereqs || [];

  const hitNodesSet = useMemo(() => new Set(hitNodes), [hitNodes]);
  const expandedNodesSet = useMemo(() => new Set(expandedNodes), [expandedNodes]);
  const missingPrereqSet = useMemo(() => new Set(missingPrereqs), [missingPrereqs]);

  const hitIndexMap = useMemo(() => {
    const map = new Map();
    hitNodes.forEach((name, idx) => map.set(name, idx));
    return map;
  }, [hitNodes]);

  const COLORS = {
    BLUE: '#3b82f6',
    GREEN: '#10b981',
    RED: '#ef4444',
    AMBER: '#f59e0b',
    DEFAULT: '#94a3b8',
    LINK: '#cbd5e1',
    LINK_TEXT: '#64748b'
  };

  const BLUE_RELATIONS = useMemo(() => new Set([
    'PREREQ'
  ]), []);

  const GREEN_RELATIONS = useMemo(() => new Set([
    'MAPPED_TO',
    'HAS_CASE',
    'HAS_POSITIVE_CASE',
    'HAS_NEGATIVE_CASE'
  ]), []);

  const RED_RELATIONS = useMemo(() => new Set([
    'COMMON_MISTAKE'
  ]), []);

  const getHitRank = (name) => {
    return hitIndexMap.has(name) ? hitIndexMap.get(name) : Number.MAX_SAFE_INTEGER;
  };

  const getNodeColorByName = (nodeName) => {
    // 命中概念永远优先蓝色；缺失前置概念用琥珀色，确保不会被误认为普通节点。
    if (hitNodesSet.has(nodeName)) return COLORS.BLUE;
    if (missingPrereqSet.has(nodeName)) return COLORS.AMBER;

    let hasRed = false;
    let hasGreen = false;
    let hasBlue = expandedNodesSet.has(nodeName);

    for (const t of triples) {
      const involvesNode = t.source === nodeName || t.target === nodeName;
      if (!involvesNode) continue;

      const rel = String(t.relation || '').toUpperCase();
      if (RED_RELATIONS.has(rel)) {
        hasRed = true;
      } else if (GREEN_RELATIONS.has(rel)) {
        hasGreen = true;
      } else if (BLUE_RELATIONS.has(rel)) {
        hasBlue = true;
      }
    }

    if (hasRed) return COLORS.RED;
    if (hasGreen) return COLORS.GREEN;
    if (hasBlue) return COLORS.BLUE;
    return COLORS.DEFAULT;
  };

  const getTextColorClass = (nodeName) => {
    const color = getNodeColorByName(nodeName);
    if (color === COLORS.RED) return 'text-red-500';
    if (color === COLORS.GREEN) return 'text-emerald-600';
    if (color === COLORS.BLUE) return 'text-blue-600';
    if (color === COLORS.AMBER) return 'text-amber-600';
    return 'text-slate-500';
  };

  const graphData = useMemo(() => {
    const nodeMap = new Map();
    const links = [];

    const registerNode = (id) => {
      if (!id || nodeMap.has(id)) return;
      nodeMap.set(id, {
        id,
        name: id,
        isHit: hitNodesSet.has(id),
        isExpanded: expandedNodesSet.has(id),
        isMissingPrereq: missingPrereqSet.has(id)
      });
    };

    hitNodes.forEach(registerNode);
    expandedNodes.forEach(registerNode);
    missingPrereqs.forEach(registerNode);

    triples.forEach((t) => {
      registerNode(t.source);
      registerNode(t.target);
      links.push({
        source: t.source,
        target: t.target,
        label: String(t.relation || '').toUpperCase()
      });
    });

    const nodes = Array.from(nodeMap.values()).map((node) => ({
      ...node,
      color: getNodeColorByName(node.name)
    }));

    return {
      nodes,
      links,
      typeMap: nodeMap
    };
  }, [triples, hitNodes, expandedNodes, missingPrereqs, hitNodesSet, expandedNodesSet, missingPrereqSet]);

  const orderedTriples = useMemo(() => {
    const relationPriority = (relRaw) => {
      const rel = String(relRaw || '').toUpperCase();
      if (BLUE_RELATIONS.has(rel)) return 0;
      if (RED_RELATIONS.has(rel)) return 1;
      if (GREEN_RELATIONS.has(rel)) return 2;
      return 3;
    };

    const nodeRank = (name) => {
      if (hitNodesSet.has(name)) return getHitRank(name);
      if (missingPrereqSet.has(name)) return hitNodes.length + 0.5;
      if (expandedNodesSet.has(name)) return hitNodes.length + 1;
      return Number.MAX_SAFE_INTEGER;
    };

    const triplePriority = (triple) => {
      const sourceRank = nodeRank(triple.source);
      const targetRank = nodeRank(triple.target);
      const bestRank = Math.min(sourceRank, targetRank);

      const sourceHit = hitNodesSet.has(triple.source);
      const targetHit = hitNodesSet.has(triple.target);
      const sourcePrereq = missingPrereqSet.has(triple.source);
      const targetPrereq = missingPrereqSet.has(triple.target);

      let hitTypePriority = 4;
      if (sourcePrereq || targetPrereq) hitTypePriority = 0;
      else if (sourceHit && !targetHit) hitTypePriority = 1;
      else if (!sourceHit && targetHit) hitTypePriority = 2;
      else if (sourceHit && targetHit) hitTypePriority = 3;

      return {
        bestRank,
        hitTypePriority,
        relationPriority: relationPriority(triple.relation),
        source: triple.source,
        target: triple.target
      };
    };

    return [...triples].sort((a, b) => {
      const pa = triplePriority(a);
      const pb = triplePriority(b);
      if (pa.bestRank !== pb.bestRank) return pa.bestRank - pb.bestRank;
      if (pa.hitTypePriority !== pb.hitTypePriority) return pa.hitTypePriority - pb.hitTypePriority;
      if (pa.relationPriority !== pb.relationPriority) return pa.relationPriority - pb.relationPriority;
      if (pa.source !== pb.source) return pa.source.localeCompare(pb.source, 'zh-Hans-CN');
      return pa.target.localeCompare(pb.target, 'zh-Hans-CN');
    });
  }, [triples, hitNodesSet, expandedNodesSet, missingPrereqSet, hitIndexMap, hitNodes.length]);

  const getTripleDisplay = (triple) => {
    const rel = String(triple.relation || '').toUpperCase();
    const sourceHit = hitNodesSet.has(triple.source);
    const targetHit = hitNodesSet.has(triple.target);

    if (!sourceHit && targetHit) {
      return {
        top: triple.target,
        bottom: triple.source,
        relationText: `←[${rel}]—`,
        isMistakeRel: rel === 'COMMON_MISTAKE'
      };
    }

    if (sourceHit && targetHit) {
      const sourceRank = getHitRank(triple.source);
      const targetRank = getHitRank(triple.target);
      if (targetRank < sourceRank) {
        return {
          top: triple.target,
          bottom: triple.source,
          relationText: `←[${rel}]—`,
          isMistakeRel: rel === 'COMMON_MISTAKE'
        };
      }
    }

    return {
      top: triple.source,
      bottom: triple.target,
      relationText: `—[${rel}]→`,
      isMistakeRel: rel === 'COMMON_MISTAKE'
    };
  };

  useEffect(() => {
    if (open && fgRef.current) {
      fgRef.current.d3Force('charge').strength(-520);
      fgRef.current.d3Force('link').distance(120);
    }
  }, [open, graphData]);

  if (!open) return null;

  const hasData = graphData.nodes.length > 0;

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
                <p className="text-xs text-slate-500">学生命中概念优先展示；前置概念、跳跃扩展、案例与错误均来自 kgContext</p>
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
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS.BLUE }}></span>
                    查询命中 / PREREQ / 扩展
                  </span>
                  <span className="flex items-center gap-1.5 text-xs bg-white/90 backdrop-blur border border-slate-200 px-2.5 py-1.5 rounded-md shadow-sm text-slate-700 font-medium">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS.AMBER }}></span>
                    缺失前置概念
                  </span>
                  <span className="flex items-center gap-1.5 text-xs bg-white/90 backdrop-blur border border-slate-200 px-2.5 py-1.5 rounded-md shadow-sm text-slate-700 font-medium">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS.GREEN }}></span>
                    MAPPED / CASE
                  </span>
                  <span className="flex items-center gap-1.5 text-xs bg-white/90 backdrop-blur border border-slate-200 px-2.5 py-1.5 rounded-md shadow-sm text-slate-700 font-medium">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS.RED }}></span>
                    MISTAKE
                  </span>
                </div>

                <ForceGraph2D
                  ref={fgRef}
                  width={800}
                  height={600}
                  graphData={graphData}
                  nodeLabel="name"
                  linkColor={(link) => {
                    const rel = String(link.label || '').toUpperCase();
                    if (RED_RELATIONS.has(rel)) return '#fca5a5';
                    if (GREEN_RELATIONS.has(rel)) return '#86efac';
                    if (BLUE_RELATIONS.has(rel)) return '#93c5fd';
                    return COLORS.LINK;
                  }}
                  linkDirectionalArrowLength={4}
                  linkDirectionalArrowRelPos={1}
                  nodeCanvasObject={(node, ctx, globalScale) => {
                    const label = node.name;
                    const fontSize = 12 / globalScale;
                    ctx.font = `${fontSize}px Sans-Serif`;

                    const nodeRadius = node.isHit ? 8 : node.isMissingPrereq ? 7 : 6;
                    const bgColor = node.color || COLORS.DEFAULT;

                    ctx.beginPath();
                    ctx.arc(node.x, node.y, nodeRadius, 0, 2 * Math.PI, false);
                    ctx.fillStyle = bgColor;
                    ctx.fill();
                    ctx.lineWidth = 1.5 / globalScale;
                    ctx.strokeStyle = '#ffffff';
                    ctx.stroke();

                    const shouldAlwaysShowLabel =
                      node.isHit || node.isExpanded || node.isMissingPrereq ||
                      bgColor === COLORS.BLUE || bgColor === COLORS.GREEN || bgColor === COLORS.RED || bgColor === COLORS.AMBER;

                    if (shouldAlwaysShowLabel) {
                      ctx.textAlign = 'center';
                      ctx.textBaseline = 'top';
                      ctx.fillStyle = node.isHit ? '#1e293b' : '#475569';
                      ctx.fillText(label, node.x, node.y + nodeRadius + (2 / globalScale));
                    }
                  }}
                  linkCanvasObjectMode={() => 'after'}
                  linkCanvasObject={(link, ctx) => {
                    const MAX_FONT_SIZE = 4;
                    const start = link.source;
                    const end = link.target;
                    if (typeof start !== 'object' || typeof end !== 'object') return;

                    const textPos = {
                      x: start.x + (end.x - start.x) / 2,
                      y: start.y + (end.y - start.y) / 2
                    };
                    const relLink = { x: end.x - start.x, y: end.y - start.y };
                    let textAngle = Math.atan2(relLink.y, relLink.x);
                    if (textAngle > Math.PI / 2) textAngle = -(Math.PI - textAngle);
                    if (textAngle < -Math.PI / 2) textAngle = -(Math.PI + textAngle);

                    const label = String(link.label || '').toUpperCase();
                    ctx.font = `${MAX_FONT_SIZE}px Sans-Serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';

                    let textColor = COLORS.LINK_TEXT;
                    let bg = 'rgba(255, 255, 255, 0.85)';
                    if (RED_RELATIONS.has(label)) {
                      textColor = '#ef4444';
                      bg = 'rgba(254, 226, 226, 0.9)';
                    } else if (GREEN_RELATIONS.has(label)) {
                      textColor = '#059669';
                      bg = 'rgba(220, 252, 231, 0.9)';
                    } else if (BLUE_RELATIONS.has(label)) {
                      textColor = '#2563eb';
                      bg = 'rgba(219, 234, 254, 0.9)';
                    }

                    ctx.save();
                    ctx.translate(textPos.x, textPos.y);
                    ctx.rotate(textAngle);

                    const textWidth = ctx.measureText(label).width;
                    ctx.fillStyle = bg;
                    ctx.fillRect(-textWidth / 2 - 2, -MAX_FONT_SIZE / 2 - 1, textWidth + 4, MAX_FONT_SIZE + 2);

                    ctx.fillStyle = textColor;
                    ctx.fillText(label, 0, 0);
                    ctx.restore();
                  }}
                />
              </div>

              <div className="w-full md:w-96 bg-white overflow-y-auto flex flex-col">
                <div className="p-3 bg-slate-50 border-b border-slate-200 font-bold text-sm text-slate-700 sticky top-0 z-10 shadow-sm">
                  知识推理链路明细
                </div>

                {(hitNodes.length > 0 || missingPrereqs.length > 0 || expandedNodes.length > 0) && (
                  <div className="px-4 py-3 border-b border-slate-100 bg-white sticky top-[49px] z-[9] space-y-3">
                    {hitNodes.length > 0 && (
                      <div>
                        <div className="text-xs text-slate-500 mb-2">当前命中概念顺序</div>
                        <div className="flex flex-wrap gap-2">
                          {hitNodes.map((name, idx) => (
                            <span key={`hit-${name}-${idx}`} className="px-2 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
                              {idx + 1}. {name}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {missingPrereqs.length > 0 && (
                      <div>
                        <div className="text-xs text-slate-500 mb-2">缺失前置概念</div>
                        <div className="flex flex-wrap gap-2">
                          {missingPrereqs.map((name, idx) => (
                            <span key={`missing-${name}-${idx}`} className="px-2 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
                              {name}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {expandedNodes.length > 0 && (
                      <div>
                        <div className="text-xs text-slate-500 mb-2">跳跃扩展概念</div>
                        <div className="flex flex-wrap gap-2">
                          {expandedNodes.map((name, idx) => (
                            <span key={`expanded-${name}-${idx}`} className="px-2 py-1 rounded-full text-xs font-medium bg-sky-50 text-sky-700 border border-sky-200">
                              {name}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <div className="p-4 space-y-3">
                  {orderedTriples.map((t, idx) => {
                    const display = getTripleDisplay(t);
                    const topColorClass = getTextColorClass(display.top);
                    const bottomColorClass = getTextColorClass(display.bottom);
                    const rel = String(t.relation || '').toUpperCase();
                    const isMistakeRel = rel === 'COMMON_MISTAKE';
                    const isPrereqRel = rel === 'PREREQ';

                    const relClass = isMistakeRel
                      ? 'text-red-400 border-red-300'
                      : GREEN_RELATIONS.has(rel)
                        ? 'text-emerald-500 border-emerald-300'
                        : BLUE_RELATIONS.has(rel)
                          ? 'text-blue-400 border-blue-300'
                          : 'text-slate-400 border-slate-300';

                    const cardBorder = isMistakeRel
                      ? 'border-red-200'
                      : GREEN_RELATIONS.has(rel)
                        ? 'border-emerald-200'
                        : BLUE_RELATIONS.has(rel)
                          ? 'border-blue-200'
                          : 'border-slate-200';

                    return (
                      <div key={`${t.source}-${rel}-${t.target}-${idx}`} className={`bg-slate-50 border rounded-lg p-3 text-sm hover:shadow-md transition-shadow ${cardBorder}`}>
                        <div className="flex flex-col gap-1.5">
                          <div className={`font-semibold ${topColorClass}`}>
                            {display.top}
                          </div>
                          <div className={`flex items-center gap-2 text-xs font-mono pl-2 border-l-2 ${relClass}`}>
                            {display.relationText}
                            {isPrereqRel && <span className="font-sans text-[10px] text-blue-500">前置链路</span>}
                          </div>
                          <div className={`font-semibold ${bottomColorClass}`}>
                            {display.bottom}
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
