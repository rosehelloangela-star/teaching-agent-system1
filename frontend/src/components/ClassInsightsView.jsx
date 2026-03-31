// import React, { useState, useEffect } from 'react';
// import { BarChart3, AlertTriangle, Lightbulb, Loader2, Send, Users, Trophy, Target, ShieldAlert, Bot } from 'lucide-react';
// import { runAgent, fetchClassInsights } from '../api';

// export default function ClassInsightsView({ currentUser }) {
//   const [selectedClass, setSelectedClass] = useState('');
//   const [insightsLoading, setInsightsLoading] = useState(false);
//   // 初始给个空对象兜底，防止初始渲染时闪烁
//   const [insightsData, setInsightsData] = useState(null); 
  
//   const [interventionLoading, setInterventionLoading] = useState(false);
//   const [agentResult, setAgentResult] = useState(null);
  
//   const [activeCompTab, setActiveCompTab] = useState('互联网+');

//   const assignedClasses = currentUser?.class_name 
//     ? currentUser.class_name.split(',').map(c => c.trim()).filter(c => c) 
//     : [];

//   useEffect(() => {
//     if (assignedClasses.length === 1 && !selectedClass) setSelectedClass(assignedClasses[0]);
//   }, [assignedClasses]);

//   const handleGenerateInsights = async () => {
//     if (!selectedClass) return;
//     setInsightsLoading(true);
//     setAgentResult(null);
//     try {
//       const data = await fetchClassInsights(selectedClass);
//       setInsightsData(data);
//       const compKeys = Object.keys(data.competitions || {});
//       if (compKeys.length > 0) setActiveCompTab(compKeys[0]);
//     } catch (e) {
//       // 优雅的弹窗报错，而不是白屏
//       alert(e.response?.data?.detail || "获取班级数据失败，请检查网络或后端运行状态。");
//     } finally {
//       setInsightsLoading(false);
//     }
//   };

//   const handleGenerateIntervention = async () => {
//     if (!insightsData) {
//       alert("请先拉取班级快照数据，再生成教学规划！");
//       return;
//     }
//     setInterventionLoading(true);
//     try {
//       const alertsStr = (insightsData?.hypergraph_alerts || []).map(a => `${a.rule}(${a.count}次)`).join('，') || "无明显断层";
//       const riskStr = (insightsData?.high_risk_projects || []).map(p => `${p.project_name}(触发${p.alert_count}条危险)`).join('，') || "无";
      
//       const summaryText = `当前班级【${selectedClass}】共${insightsData?.total_projects || 0}个项目。超图高发逻辑断层为：${alertsStr}。高危项目列表：${riskStr}。请作为教学助手，严格输出 JSON 格式对全班进行综合评价。`;
      
//       const data = await runAgent(summaryText, 'instructor', `class_eval_${selectedClass}`);
//       setAgentResult(data.generated_content); 
//     } catch (e) {
//       alert("AI 生成失败，请稍后重试。");
//     } finally {
//       setInterventionLoading(false);
//     }
//   };

//   return (
//     <div className="flex-1 overflow-y-auto p-8 flex flex-col bg-slate-50/50">
//       <div className="flex justify-between items-end mb-6">
//         <div>
//           <h1 className="text-2xl font-bold text-slate-800">📊 班级学情洞察</h1>
//           <p className="text-slate-500 mt-1">全局掌握班级超图缺陷、竞赛模拟得分与高危项目</p>
//         </div>
//         <div className="flex gap-2">
//           <select value={selectedClass} onChange={e => setSelectedClass(e.target.value)} className="border border-slate-300 rounded-lg px-4 py-2 bg-white text-sm outline-none focus:ring-2 focus:ring-brand-500">
//             <option value="">-- 选择管辖班级 --</option>
//             {assignedClasses.map((c, i) => <option key={i} value={c}>{c}</option>)}
//           </select>
//           <button onClick={handleGenerateInsights} disabled={!selectedClass || insightsLoading} className="bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-slate-900 disabled:opacity-50 flex items-center gap-2">
//             {insightsLoading ? <Loader2 size={16} className="animate-spin" /> : <BarChart3 size={16}/>}
//             拉取全班快照
//           </button>
//         </div>
//       </div>

//       {/* 【核心修改】：移除整个外层的条件判断，让面板框架永远存在 */}
//       <div className="space-y-6 animate-in fade-in duration-300">
        
//         <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
//           {/* 看板1：超图规则危险分布 */}
//           <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col max-h-80">
//             <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4 border-b border-slate-100 pb-2">
//               <Target size={18} className="text-red-500"/> 超图规则触发分布
//             </h3>
//             <div className="overflow-y-auto pr-2 space-y-3 flex-1">
//               {(!insightsData || (insightsData?.hypergraph_alerts || []).length === 0) ? (
//                 <div className="flex flex-col items-center justify-center h-full text-slate-400 py-10">
//                   <span className="text-sm">暂无触发记录或尚未拉取数据</span>
//                 </div>
//               ) : 
//                 (insightsData.hypergraph_alerts || []).map((a, i) => (
//                   <div key={i} className="flex flex-col gap-1">
//                     <div className="flex justify-between text-xs">
//                       <span className="font-semibold text-slate-700 truncate pr-2" title={a.rule}>{a.rule}</span>
//                       <span className="text-red-600 font-bold shrink-0">{a.count}次 ({a.percentage}%)</span>
//                     </div>
//                     <div className="w-full bg-slate-100 rounded-full h-1.5"><div className="bg-red-400 h-1.5 rounded-full" style={{width: `${a.percentage}%`}}></div></div>
//                   </div>
//                 ))
//               }
//             </div>
//           </div>

//           {/* 看板2：班级竞赛得分情况 */}
//           <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col max-h-80 col-span-1 lg:col-span-2">
//             <div className="flex justify-between items-center mb-4 border-b border-slate-100 pb-2">
//               <h3 className="font-bold text-slate-800 flex items-center gap-2">
//                 <Trophy size={18} className="text-amber-500"/> 竞赛模拟得分排行榜
//               </h3>
//               <div className="flex gap-2">
//                 {Object.keys(insightsData?.competitions || {}).length === 0 ? <span className="text-xs text-slate-400">暂无竞赛数据</span> : 
//                   Object.keys(insightsData.competitions).map(comp => (
//                     <button key={comp} onClick={() => setActiveCompTab(comp)} className={`px-3 py-1 text-xs font-bold rounded-full transition-colors ${activeCompTab === comp ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'}`}>
//                       {comp}
//                     </button>
//                   ))
//                 }
//               </div>
//             </div>
//             <div className="overflow-y-auto pr-2 flex-1">
//               {(!insightsData || Object.keys(insightsData?.competitions || {}).length === 0) ? (
//                  <div className="h-full flex items-center justify-center text-sm text-slate-400 py-10">点击右上角拉取数据，或学生暂未运行任何竞赛模式</div>
//               ) : (
//                 <table className="w-full text-left text-sm">
//                   <thead className="sticky top-0 bg-white shadow-sm text-slate-500">
//                     <tr><th className="py-2">学生</th><th className="py-2">项目名称</th><th className="py-2 text-right">预估得分</th></tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-100">
//                     {((insightsData.competitions || {})[activeCompTab] || []).map((p, i) => (
//                       <tr key={i} className="hover:bg-slate-50">
//                         <td className="py-2.5 font-medium text-slate-800 w-24">{p.student_name}</td>
//                         <td className="py-2.5 text-slate-600 truncate max-w-[200px]" title={p.project_name}>{p.project_name}</td>
//                         <td className="py-2.5 text-right font-bold text-amber-600">{p.score}</td>
//                       </tr>
//                     ))}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>
//         </div>

//         {/* 高风险项目简报 */}
//         <div className="bg-red-50/50 p-5 rounded-2xl border border-red-100 shadow-sm">
//           <h3 className="font-bold text-red-800 flex items-center gap-2 mb-4">
//             <ShieldAlert size={18}/> 高风险项目预警 (触发 ≥2 条超图断层)
//           </h3>
//           <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
//             {(!insightsData || (insightsData?.high_risk_projects || []).length === 0) ? (
//               <p className="text-sm text-red-400 col-span-3 py-4">当前班级暂无高风险项目，或尚未拉取数据</p>
//             ) : 
//               (insightsData.high_risk_projects || []).map((p, i) => (
//                 <div key={i} className="bg-white border border-red-200 p-4 rounded-xl shadow-sm">
//                   <div className="flex justify-between items-start mb-1">
//                     <span className="font-bold text-sm text-slate-800 truncate" title={p.project_name}>{p.student_name}</span>
//                     <span className="text-[10px] bg-red-100 text-red-700 px-2 py-0.5 rounded font-bold">{p.alert_count} 条隐患</span>
//                   </div>
//                   <div className="text-xs font-semibold text-slate-600 mb-2 truncate">{p.project_name}</div>
//                   <p className="text-xs text-red-600 leading-relaxed bg-red-50 p-2 rounded">核心问题：{p.issues}</p>
//                 </div>
//               ))
//             }
//           </div>
//         </div>

//         {/* Agent 智能评估报告 */}
//         <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
//           <div className="flex items-center justify-between mb-6">
//             <h3 className="font-bold text-slate-800 flex items-center gap-2">
//               <Lightbulb size={20} className="text-brand-500"/> Agent 班级学情综合诊断
//             </h3>
//             <button onClick={handleGenerateIntervention} disabled={interventionLoading || !insightsData} className="bg-brand-600 hover:bg-brand-700 text-white px-5 py-2 rounded-lg text-sm font-bold flex items-center gap-2 disabled:opacity-50 transition-colors">
//               {interventionLoading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
//               注入班级痛点，一键生成下周教案
//             </button>
//           </div>
          
//           <div className="bg-slate-50 border border-slate-200 rounded-xl min-h-[150px] overflow-hidden">
//             {!agentResult && !interventionLoading && (
//               <div className="h-full flex flex-col items-center justify-center p-12 text-slate-400">
//                 <Bot size={40} className="opacity-20 mb-3" />
//                 <p className="text-sm">点击右上角按钮，调用 Instructor Assistant 生成包含知识覆盖率与干预建议的结构化报告</p>
//               </div>
//             )}
            
//             {agentResult && (
//               <div className="p-6 space-y-6">
//                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//                   <div className="bg-white p-4 border border-slate-200 rounded-xl">
//                     <h4 className="text-xs font-bold text-slate-400 mb-1 uppercase tracking-wider">知识覆盖情况</h4>
//                     <p className="text-sm text-slate-700 leading-relaxed">{agentResult.knowledge_coverage}</p>
//                   </div>
//                   <div className="bg-white p-4 border border-slate-200 rounded-xl">
//                     <h4 className="text-xs font-bold text-slate-400 mb-1 uppercase tracking-wider">Rubric 能力分布</h4>
//                     <p className="text-sm text-slate-700 leading-relaxed">{agentResult.rubric_distribution}</p>
//                   </div>
//                 </div>
                
//                 <div>
//                   <h4 className="text-sm font-bold text-slate-800 mb-3">⚠️ Agent 判定的重点关注名单</h4>
//                   <div className="space-y-2">
//                     {(agentResult.risk_list || []).map((risk, idx) => (
//                       <div key={idx} className="bg-white p-3 border border-slate-200 rounded-lg flex items-start gap-4">
//                         <span className={`px-2 py-1 rounded text-xs font-bold shrink-0 ${risk.risk_score === '高' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>
//                           {risk.risk_score}风险
//                         </span>
//                         <div>
//                           <span className="font-bold text-sm text-slate-800">{risk.project_name}</span>
//                           <ul className="mt-1 space-y-1 list-disc pl-4">
//                             {(risk.primary_issues || []).map((issue, i) => (
//                               <li key={i} className="text-xs text-slate-600">{issue}</li>
//                             ))}
//                           </ul>
//                         </div>
//                       </div>
//                     ))}
//                   </div>
//                 </div>

//                 <div className="bg-blue-50 p-4 border border-blue-100 rounded-xl">
//                   <h4 className="text-sm font-bold text-blue-800 mb-2">💡 教学干预建议 (Teaching Suggestions)</h4>
//                   <p className="text-sm text-blue-700 whitespace-pre-wrap leading-relaxed">{agentResult.teaching_suggestions}</p>
//                 </div>
//               </div>
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }



import React, { useState, useEffect, useMemo } from 'react';
import { BarChart3, Lightbulb, Loader2, Send, Users, Trophy, Target, ShieldAlert, Bot, BookOpen, AlertTriangle } from 'lucide-react';
import { runAgent, fetchClassInsights } from '../api';

export default function ClassInsightsView({ currentUser }) {
  const [selectedClass, setSelectedClass] = useState('');
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [insightsData, setInsightsData] = useState(null);

  const [interventionLoading, setInterventionLoading] = useState(false);
  const [agentResult, setAgentResult] = useState(null);

  const [activeCompTab, setActiveCompTab] = useState('');

  const assignedClasses = currentUser?.class_name
    ? currentUser.class_name.split(',').map(c => c.trim()).filter(c => c)
    : [];

  useEffect(() => {
    if (assignedClasses.length === 1 && !selectedClass) setSelectedClass(assignedClasses[0]);
  }, [assignedClasses, selectedClass]);

  const activeCompetitionList = useMemo(() => {
    if (!insightsData?.competitions || !activeCompTab) return [];
    return insightsData.competitions[activeCompTab] || [];
  }, [insightsData, activeCompTab]);

  const handleGenerateInsights = async () => {
    if (!selectedClass) return;
    setInsightsLoading(true);
    setAgentResult(null);
    try {
      const data = await fetchClassInsights(selectedClass);
      setInsightsData(data);
      const compKeys = Object.keys(data.competitions || {});
      setActiveCompTab(compKeys.length > 0 ? compKeys[0] : '');
    } catch (e) {
      alert(e.response?.data?.detail || '获取班级数据失败，请检查网络或后端运行状态。');
    } finally {
      setInsightsLoading(false);
    }
  };

  const handleGenerateIntervention = async () => {
    if (!insightsData) {
      alert('请先拉取班级快照数据，再生成教学规划！');
      return;
    }
    setInterventionLoading(true);
    try {
      const coverageStr = (insightsData?.coverage_summary || [])
        .slice(0, 5)
        .map(i => `${i.dimension_name}${i.mastery_rate}%`)
        .join('，') || '暂无';
      const mistakesStr = (insightsData?.top_mistakes || [])
        .map(m => `${m.mistake}(${m.count}次)`)
        .join('，') || '无';
      const riskStr = (insightsData?.high_risk_projects || [])
        .slice(0, 5)
        .map(p => `${p.student_name}-${p.project_name}(${p.issues})`)
        .join('；') || '无';

      const summaryText = `当前班级【${selectedClass}】共有 ${insightsData?.total_projects || 0} 个项目，平均竞赛模拟得分 ${insightsData?.average_competition_score_pct || 0}/100，平均单项 Rubric ${insightsData?.average_rubric_score || 0}/5。知识覆盖摘要：${coverageStr}。共性错误 Top5：${mistakesStr}。高风险项目：${riskStr}。请作为教师助手，输出 Coverage Summary、Top 5 Mistakes、High-risk Projects、Teaching Interventions 四项结构化结果。`;

      const data = await runAgent(summaryText, 'instructor', `class_eval_${selectedClass}`);
      setAgentResult(data.generated_content);
    } catch (e) {
      alert('AI 生成失败，请稍后重试。');
    } finally {
      setInterventionLoading(false);
    }
  };

  return (
    <div className="h-full min-h-0 overflow-y-auto p-6 lg:p-8 flex flex-col bg-slate-50/50">
      <div className="flex flex-col gap-4 lg:flex-row lg:justify-between lg:items-end mb-6 shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">📊 班级学情洞察</h1>
          <p className="text-slate-500 mt-1">全局掌握班级知识覆盖、共性错误、高风险项目与教学干预重点</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-2 lg:justify-end">
          <select value={selectedClass} onChange={e => setSelectedClass(e.target.value)} className="border border-slate-300 rounded-lg px-4 py-2 bg-white text-sm outline-none focus:ring-2 focus:ring-brand-500">
            <option value="">-- 选择管辖班级 --</option>
            {assignedClasses.map((c, i) => <option key={i} value={c}>{c}</option>)}
          </select>
          <button onClick={handleGenerateInsights} disabled={!selectedClass || insightsLoading} className="bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-slate-900 disabled:opacity-50 flex items-center gap-2">
            {insightsLoading ? <Loader2 size={16} className="animate-spin" /> : <BarChart3 size={16} />}
            拉取全班快照
          </button>
        </div>
      </div>

      <div className="space-y-6 animate-in fade-in duration-300">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <div className="text-xs text-slate-400 mb-1">班级项目总数</div>
            <div className="text-3xl font-extrabold text-slate-800">{insightsData?.total_projects ?? 0}</div>
            <div className="text-xs text-slate-500 mt-2">已绑定文档并沉淀快照的项目数</div>
          </div>
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <div className="text-xs text-slate-400 mb-1">平均竞赛模拟得分</div>
            <div className="text-3xl font-extrabold text-amber-600">{insightsData?.average_competition_score_pct ?? 0}<span className="text-base">/100</span></div>
            <div className="text-xs text-slate-500 mt-2">来自学生端 competition 模式真实快照</div>
          </div>
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <div className="text-xs text-slate-400 mb-1">平均 Rubric 单项分</div>
            <div className="text-3xl font-extrabold text-blue-600">{insightsData?.average_rubric_score ?? 0}<span className="text-base">/5</span></div>
            <div className="text-xs text-slate-500 mt-2">按各赛事 rubric_items 聚合</div>
          </div>
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <div className="text-xs text-slate-400 mb-1">高风险项目数</div>
            <div className="text-3xl font-extrabold text-red-600">{(insightsData?.high_risk_projects || []).length}</div>
            <div className="text-xs text-slate-500 mt-2">高危项目需要优先约谈或课堂点名辅导</div>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col max-h-96">
            <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4 border-b border-slate-100 pb-2">
              <Target size={18} className="text-red-500" /> 超图规则触发分布
            </h3>
            <div className="overflow-y-auto pr-2 space-y-3 flex-1">
              {(!insightsData || (insightsData?.hypergraph_alerts || []).length === 0) ? (
                <div className="flex flex-col items-center justify-center h-full text-slate-400 py-10">
                  <span className="text-sm">暂无触发记录或尚未拉取数据</span>
                </div>
              ) :
                (insightsData.hypergraph_alerts || []).map((a, i) => (
                  <div key={i} className="flex flex-col gap-1">
                    <div className="flex justify-between text-xs gap-3">
                      <span className="font-semibold text-slate-700 truncate" title={a.rule}>{a.rule}</span>
                      <span className="text-red-600 font-bold shrink-0">{a.count}次 ({a.percentage}%)</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5"><div className="bg-red-400 h-1.5 rounded-full" style={{ width: `${a.percentage}%` }} /></div>
                  </div>
                ))
              }
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col max-h-96">
            <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4 border-b border-slate-100 pb-2">
              <BookOpen size={18} className="text-blue-500" /> Class Knowledge Coverage Summary
            </h3>
            <div className="overflow-y-auto pr-2 space-y-3 flex-1">
              {(!insightsData || (insightsData?.coverage_summary || []).length === 0) ? (
                <div className="flex items-center justify-center h-full text-slate-400 py-10 text-sm">暂无知识覆盖数据</div>
              ) : (insightsData.coverage_summary || []).slice(0, 8).map((item, idx) => (
                <div key={`${item.dimension_id}-${idx}`} className="space-y-1">
                  <div className="flex justify-between text-xs gap-2">
                    <span className="font-semibold text-slate-700 truncate" title={item.dimension_name}>{item.dimension_name}</span>
                    <span className="text-blue-600 font-bold shrink-0">{item.mastery_rate}%</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-1.5"><div className="bg-blue-400 h-1.5 rounded-full" style={{ width: `${item.mastery_rate}%` }} /></div>
                  <div className="text-[11px] text-slate-400">平均单项分：{item.average_score}/5</div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col max-h-96">
            <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4 border-b border-slate-100 pb-2">
              <AlertTriangle size={18} className="text-amber-500" /> Top 5 Common Mistakes
            </h3>
            <div className="overflow-y-auto pr-2 space-y-3 flex-1">
              {(!insightsData || (insightsData?.top_mistakes || []).length === 0) ? (
                <div className="flex items-center justify-center h-full text-slate-400 py-10 text-sm">暂无共性错误数据</div>
              ) : (insightsData.top_mistakes || []).map((item, idx) => (
                <div key={`${item.mistake}-${idx}`} className="bg-slate-50 border border-slate-200 rounded-xl p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-semibold text-slate-800 text-sm">{item.mistake}</div>
                      <div className="text-xs text-slate-500 mt-1">来源：{item.source === 'competition' ? '竞赛评分低分项' : '项目模式超图预警'}</div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-amber-600 font-bold text-sm">{item.count} 次</div>
                      <div className="text-[11px] text-slate-400">{item.percentage}%</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col max-h-96 lg:col-span-2">
            <div className="flex justify-between items-center mb-4 border-b border-slate-100 pb-2">
              <h3 className="font-bold text-slate-800 flex items-center gap-2">
                <Trophy size={18} className="text-amber-500" /> 竞赛模拟得分排行榜
              </h3>
              <div className="flex gap-2 flex-wrap justify-end">
                {Object.keys(insightsData?.competitions || {}).length === 0 ? <span className="text-xs text-slate-400">暂无竞赛数据</span> :
                  Object.keys(insightsData.competitions).map(comp => (
                    <button key={comp} onClick={() => setActiveCompTab(comp)} className={`px-3 py-1 text-xs font-bold rounded-full transition-colors ${activeCompTab === comp ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'}`}>
                      {comp}
                    </button>
                  ))
                }
              </div>
            </div>
            <div className="overflow-y-auto pr-2 flex-1">
              {(!insightsData || Object.keys(insightsData?.competitions || {}).length === 0) ? (
                <div className="h-full flex items-center justify-center text-sm text-slate-400 py-10">点击右上角拉取数据，或学生暂未运行任何竞赛模式</div>
              ) : (
                <table className="w-full text-left text-sm">
                  <thead className="sticky top-0 bg-white shadow-sm text-slate-500">
                    <tr><th className="py-2">学生</th><th className="py-2">项目名称</th><th className="py-2 text-right">预估得分</th></tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {activeCompetitionList.map((p, i) => (
                      <tr key={i} className="hover:bg-slate-50">
                        <td className="py-2.5 font-medium text-slate-800 w-24">{p.student_name}</td>
                        <td className="py-2.5 text-slate-600 truncate max-w-[260px]" title={p.project_name}>{p.project_name}</td>
                        <td className="py-2.5 text-right font-bold text-amber-600">{p.score}/100</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          <div className="bg-red-50/50 p-5 rounded-2xl border border-red-100 shadow-sm">
            <h3 className="font-bold text-red-800 flex items-center gap-2 mb-4">
              <ShieldAlert size={18} /> High-risk Projects
            </h3>
            <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
              {(!insightsData || (insightsData?.high_risk_projects || []).length === 0) ? (
                <p className="text-sm text-red-400 py-4">当前班级暂无高风险项目，或尚未拉取数据</p>
              ) :
                (insightsData.high_risk_projects || []).map((p, i) => (
                  <div key={i} className="bg-white border border-red-200 p-4 rounded-xl shadow-sm">
                    <div className="flex justify-between items-start mb-1 gap-3">
                      <span className="font-bold text-sm text-slate-800 truncate" title={p.project_name}>{p.student_name}</span>
                      <span className="text-[10px] bg-red-100 text-red-700 px-2 py-0.5 rounded font-bold shrink-0">{p.alert_count} 条隐患</span>
                    </div>
                    <div className="text-xs font-semibold text-slate-600 mb-2 truncate">{p.project_name}</div>
                    <p className="text-xs text-red-600 leading-relaxed bg-red-50 p-2 rounded">核心问题：{p.issues}</p>
                  </div>
                ))
              }
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb size={20} className="text-brand-500" />
              <h3 className="font-bold text-slate-800">Suggested Teaching Interventions（规则版草案）</h3>
            </div>
            {(!insightsData || (insightsData?.teaching_interventions || []).length === 0) ? (
              <div className="text-sm text-slate-400">暂无教学建议，请先拉取快照。</div>
            ) : (
              <div className="space-y-4">
                {(insightsData.teaching_interventions || []).map((item, idx) => (
                  <div key={`${item.title}-${idx}`} className="bg-slate-50 border border-slate-200 rounded-xl p-4">
                    <div className="font-bold text-slate-800 text-sm mb-1">{item.title}</div>
                    <div className="text-xs text-slate-500 mb-2">原因：{item.why}</div>
                    <ul className="list-disc pl-5 space-y-1 text-sm text-slate-700">
                      {(item.plan || []).map((step, i) => <li key={i}>{step}</li>)}
                    </ul>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-bold text-slate-800 flex items-center gap-2">
                <Lightbulb size={20} className="text-brand-500" /> Agent 班级学情综合诊断
              </h3>
              <button onClick={handleGenerateIntervention} disabled={interventionLoading || !insightsData} className="bg-brand-600 hover:bg-brand-700 text-white px-5 py-2 rounded-lg text-sm font-bold flex items-center gap-2 disabled:opacity-50 transition-colors">
                {interventionLoading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                一键生成下周教案
              </button>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-xl min-h-[280px] overflow-hidden flex-1">
              {!agentResult && !interventionLoading && (
                <div className="h-full flex flex-col items-center justify-center p-12 text-slate-400">
                  <Bot size={40} className="opacity-20 mb-3" />
                  <p className="text-sm text-center">点击右上角按钮，调用 Instructor Assistant 生成包含 Coverage Summary、Top 5 Mistakes、High-risk Projects、Teaching Interventions 的结构化报告</p>
                </div>
              )}

              {agentResult && (
                <div className="p-6 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-white p-4 border border-slate-200 rounded-xl">
                      <h4 className="text-xs font-bold text-slate-400 mb-1 uppercase tracking-wider">Coverage Summary</h4>
                      <p className="text-sm text-slate-700 leading-relaxed">{agentResult.knowledge_coverage}</p>
                    </div>
                    <div className="bg-white p-4 border border-slate-200 rounded-xl">
                      <h4 className="text-xs font-bold text-slate-400 mb-1 uppercase tracking-wider">Rubric Distribution</h4>
                      <p className="text-sm text-slate-700 leading-relaxed">{agentResult.rubric_distribution}</p>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-bold text-slate-800 mb-3">⚠️ High-risk Projects List</h4>
                    <div className="space-y-2">
                      {(agentResult.risk_list || []).map((risk, idx) => (
                        <div key={idx} className="bg-white p-3 border border-slate-200 rounded-lg flex items-start gap-4">
                          <span className={`px-2 py-1 rounded text-xs font-bold shrink-0 ${risk.risk_score === '高' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>
                            {risk.risk_score}风险
                          </span>
                          <div>
                            <span className="font-bold text-sm text-slate-800">{risk.project_name}</span>
                            <ul className="mt-1 space-y-1 list-disc pl-4">
                              {(risk.primary_issues || []).map((issue, i) => (
                                <li key={i} className="text-xs text-slate-600">{issue}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-blue-50 p-4 border border-blue-100 rounded-xl">
                    <h4 className="text-sm font-bold text-blue-800 mb-2">💡 Teaching Interventions</h4>
                    <p className="text-sm text-blue-700 whitespace-pre-wrap leading-relaxed">{agentResult.teaching_suggestions}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
