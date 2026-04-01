// import React, { useState, useEffect } from 'react';
// import { UserCog, ShieldAlert, Activity, Send, CheckCircle, Loader2, Bot, User } from 'lucide-react';
// import { runAgent, fetchAllProjects } from '../api'; // 引入API

// export default function StudentProfileView() {
//   const [allProjects, setAllProjects] = useState([]);
//   const [selectedProjectId, setSelectedProjectId] = useState('');
  
//   const [interventionRule, setInterventionRule] = useState('');
//   const [ruleInjected, setRuleInjected] = useState(false);
  
//   const [evalLoading, setEvalLoading] = useState(false);
//   const [processReport, setProcessReport] = useState('');

//   // 1. 初始化拉取所有项目
//   useEffect(() => {
//     async function loadAllProjects() {
//       const data = await fetchAllProjects();
//       setAllProjects(data);
//     }
//     loadAllProjects();
//   }, []);

//   const activeProject = allProjects.find(p => p.id === selectedProjectId);
//   // 解析存储在后端的 JSON 聊天记录
//   const projectMessages = activeProject?.chat_history ? JSON.parse(activeProject.chat_history) : [];

//   const handleInjectRule = () => {
//     if (!interventionRule.trim()) return;
//     setRuleInjected(true);
//     setTimeout(() => setRuleInjected(false), 3000);
//     setInterventionRule('');
//   };

//   const handleGenerateProcessEval = async () => {
//     if (projectMessages.length === 0) {
//       alert("该项目暂无有效的交互对话记录，无法生成评估。");
//       return;
//     }
//     setEvalLoading(true);
//     try {
//       // 2. 把真实聊天记录喂给 AI 生成报告
//       const rawLogText = projectMessages.map(m => `${m.role === 'user' ? '学生' : 'AI'}: ${m.text || JSON.stringify(m.content)}`).join('\n');
      
//       const prompt = `请根据以下真实对话记录，生成对话过程评估报告，包含：1. 核心能力打分(逻辑、商业等) 2. 行为诊断表现 3. 证据引用。\n记录如下：\n${rawLogText}`;
      
//       const data = await runAgent(prompt, 'instructor', `eval_thread_${selectedProjectId}`);
//       setProcessReport(data.generated_content.teaching_suggestions || JSON.stringify(data.generated_content));
//     } catch(e) {
//       setProcessReport("评估报告生成失败。");
//     } finally {
//       setEvalLoading(false);
//     }
//   };

//   return (
//     <div className="flex-1 overflow-y-auto p-8">
//       <div className="flex justify-between items-end mb-8">
//         <div>
//           <h1 className="text-2xl font-bold text-slate-800">👤 交互画像与反向干预 (Learning Profile)</h1>
//           <p className="text-slate-500 mt-1">查看学生在项目工作台中的真实对话记录，并生成过程性评价</p>
//         </div>
//         <select 
//           value={selectedProjectId} 
//           onChange={e => { setSelectedProjectId(e.target.value); setProcessReport(''); }}
//           className="border border-slate-300 rounded-lg px-4 py-2 bg-white text-sm outline-none focus:ring-2 focus:ring-brand-500"
//         >
//           <option value="">-- 选择目标学生项目 --</option>
//           {allProjects.map(p => (
//             <option key={p.id} value={p.id}>{p.student_id} - {p.name}</option>
//           ))}
//         </select>
//       </div>

//       {activeProject ? (
//         <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
//           <div className="flex flex-col gap-6">
            
//             {/* 真实交互日志查阅 */}
//             <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex-1 flex flex-col">
//               <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4">
//                 <Activity size={18} className="text-blue-500"/> 真实交互日志记录
//               </h3>
//               <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 flex-1 max-h-96 overflow-y-auto text-xs text-slate-600 space-y-4 font-mono">
//                 {projectMessages.length === 0 ? (
//                   <p className="text-slate-400 text-center mt-10">暂无对话记录</p>
//                 ) : (
//                   projectMessages.map((msg, i) => (
//                     <div key={i} className={`flex gap-2 ${msg.role === 'user' ? '' : 'bg-white p-2 border border-slate-100 rounded'}`}>
//                       {msg.role === 'user' ? <User size={14} className="text-brand-600 shrink-0 mt-0.5"/> : <Bot size={14} className="text-slate-800 shrink-0 mt-0.5"/>}
//                       <span className="leading-relaxed break-all">
//                         {msg.text || JSON.stringify(msg.content)}
//                       </span>
//                     </div>
//                   ))
//                 )}
//               </div>
//             </div>

//             {/* 干预注入保留... */}
//             <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
//               <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-3">
//                 <ShieldAlert size={18} className="text-red-500"/> 强制教学干预注入
//               </h3>
//               <textarea
//                 value={interventionRule}
//                 onChange={e => setInterventionRule(e.target.value)}
//                 placeholder="在此输入干预规则..."
//                 className="w-full border border-slate-300 rounded-xl p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-red-500 mb-3 bg-red-50/30"
//                 rows={2}
//               />
//               <button
//                 onClick={handleInjectRule}
//                 disabled={!interventionRule.trim()}
//                 className="w-full bg-red-500 hover:bg-red-600 disabled:bg-slate-300 text-white py-2.5 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-colors"
//               >
//                 {ruleInjected ? <><CheckCircle size={16}/> 规则已生效</> : <><Send size={16}/> 注入规则</>}
//               </button>
//             </div>
//           </div>

//           <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
//             <div className="flex items-center justify-between mb-4">
//               <h3 className="font-bold text-slate-800 flex items-center gap-2">
//                 <UserCog size={18} className="text-purple-500"/> 真实过程评估报告 (基于日志)
//               </h3>
//               <button
//                 onClick={handleGenerateProcessEval}
//                 disabled={evalLoading || projectMessages.length === 0}
//                 className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2"
//               >
//                 {evalLoading ? <Loader2 size={16} className="animate-spin"/> : '基于日志生成画像'}
//               </button>
//             </div>
            
//             <div className="flex-1 bg-purple-50/30 border border-purple-100 rounded-xl p-5 overflow-y-auto">
//               {!processReport && !evalLoading && (
//                 <div className="h-full flex flex-col items-center justify-center text-slate-400">
//                   <UserCog size={32} className="opacity-20 mb-2"/>
//                   <p className="text-sm">点击按钮，读取学生的历史对话记录进行分析打分</p>
//                 </div>
//               )}
//               {processReport && (
//                 <pre className="text-sm text-slate-700 whitespace-pre-wrap font-sans leading-relaxed">
//                   {processReport}
//                 </pre>
//               )}
//             </div>
//           </div>
          
//         </div>
//       ) : (
//         <div className="h-64 flex flex-col items-center justify-center border-2 border-dashed border-slate-300 rounded-2xl bg-white text-slate-400">
//           <UserCog size={48} className="opacity-20 mb-4" />
//           <p>请选择一个真实的学生项目以查看交互画像。</p>
//         </div>
//       )}
//     </div>
//   );
// }

import React, { useEffect, useMemo, useState } from 'react';
import { Activity, Bot, CheckCircle, Loader2, Send, ShieldAlert, User, UserCog, Search } from 'lucide-react';
import {
  fetchTeacherConversationDetail,
  fetchTeacherProjectConversations,
  runAgent,
  syncConversationState,
} from '../api';

function safeParseJSON(raw, fallback) {
  if (!raw) return fallback;
  if (typeof raw === 'object') return raw;
  try {
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function formatDateTime(raw) {
  if (!raw) return '未知时间';
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return raw;
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function StudentProfileView({ currentUser }) {
  const [items, setItems] = useState([]);
  const [loadingList, setLoadingList] = useState(true);
  const [search, setSearch] = useState('');

  const [activeId, setActiveId] = useState('');
  const [detail, setDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const [interventionType, setInterventionType] = useState('rule');
  const [interventionRule, setInterventionRule] = useState('');
  const [ruleInjected, setRuleInjected] = useState(false);

  const [evalLoading, setEvalLoading] = useState(false);
  const [processReport, setProcessReport] = useState('');

  const messages = useMemo(() => safeParseJSON(detail?.chat_history, []), [detail?.chat_history]);
  const snapshot = useMemo(() => safeParseJSON(detail?.analysis_snapshot, {}), [detail?.analysis_snapshot]);
  const interventions = snapshot.teacher_interventions || [];

  useEffect(() => {
    async function loadList() {
      if (!currentUser?.id) return;
      setLoadingList(true);
      try {
        const data = await fetchTeacherProjectConversations(currentUser.id, search);
        setItems(data || []);
        if (!activeId && data?.length) {
          setActiveId(data[0].id);
        }
      } catch (error) {
        console.error('加载教师项目会话失败', error);
      } finally {
        setLoadingList(false);
      }
    }
    loadList();
  }, [currentUser?.id, search]);

  useEffect(() => {
    async function loadDetail() {
      if (!activeId || !currentUser?.id) return;
      setLoadingDetail(true);
      try {
        const data = await fetchTeacherConversationDetail(activeId, currentUser.id);
        setDetail(data);
        setProcessReport('');
      } catch (error) {
        console.error('加载教师项目会话详情失败', error);
      } finally {
        setLoadingDetail(false);
      }
    }
    loadDetail();
  }, [activeId, currentUser?.id]);

  const persistFullConversation = async (nextMessages, nextSnapshot) => {
    if (!detail?.id) return;
    const updated = await syncConversationState(
      detail.id,
      nextMessages,
      nextSnapshot,
      detail.title,
      detail.last_mode || 'project'
    );
    setDetail((prev) => ({
      ...prev,
      chat_history: updated.chat_history,
      analysis_snapshot: updated.analysis_snapshot,
      title: updated.title,
      last_mode: updated.last_mode,
      updated_at: updated.updated_at,
    }));
  };

  const handleInjectRule = async () => {
    if (!detail?.id || !interventionRule.trim()) return;

    const intervention = {
      id: `intervention-${Date.now()}`,
      type: interventionType,
      content: interventionRule.trim(),
      created_at: new Date().toISOString(),
      created_by: currentUser?.id || '',
      active: true,
    };

    const teacherMessage = {
      id: `teacher-intervention-${Date.now()}`,
      role: 'teacher',
      mode: 'teacher_intervention',
      text: `【教师${interventionType === 'case' ? '案例注入' : '干预规则'}】${interventionRule.trim()}`,
      unreadByStudent: true,
      createdAt: new Date().toISOString(),
    };

    const nextSnapshot = {
      ...snapshot,
      teacher_interventions: [...interventions, intervention],
    };
    const nextMessages = [...messages, teacherMessage];

    await persistFullConversation(nextMessages, nextSnapshot);
    setRuleInjected(true);
    setTimeout(() => setRuleInjected(false), 3000);
    setInterventionRule('');
  };

  const handleGenerateProcessEval = async () => {
    if (!detail?.id || messages.length === 0) {
      alert('该项目暂无有效交互记录，无法生成过程评估。');
      return;
    }

    setEvalLoading(true);
    try {
      const rawLogText = messages
        .map((m) => {
          const label = m.role === 'user' ? '学生' : m.role === 'teacher' ? '教师' : 'AI';
          return `${label}: ${m.text || m.content?.reply || JSON.stringify(m.content || {})}`;
        })
        .join('\n');

      const prompt = `请根据以下真实对话记录，生成对话过程评估报告，包含：1. 核心能力打分(逻辑、商业等) 2. 行为诊断表现 3. 证据引用。\n记录如下：\n${rawLogText}`;
      const data = await runAgent(prompt, 'instructor', `eval_thread_${detail.id}`, [], detail.id);
      setProcessReport(data.generated_content.teaching_suggestions || JSON.stringify(data.generated_content, null, 2));
    } catch (error) {
      setProcessReport('评估报告生成失败。');
    } finally {
      setEvalLoading(false);
    }
  };

  return (
    <div className="flex-1 min-h-0 flex overflow-hidden">
      <div className="w-80 shrink-0 border-r border-slate-200 bg-white flex flex-col">
        <div className="p-5 border-b border-slate-200">
          <h1 className="text-xl font-bold text-slate-800">👤 交互画像与反向干预</h1>
          <p className="text-slate-500 mt-1 text-sm">查看真实日志、注入规则/案例，并验证教师可控性</p>
          <div className="mt-4 relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="检索项目名称 / 学生名称 / 文档名"
              className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-300 text-sm outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
        </div>

        <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-2">
          {loadingList ? (
            <div className="flex items-center gap-2 text-sm text-slate-500 p-3">
              <Loader2 size={16} className="animate-spin" />
              正在加载项目会话...
            </div>
          ) : items.length === 0 ? (
            <div className="text-sm text-slate-400 p-4 text-center">暂无可查看项目</div>
          ) : (
            items.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveId(item.id)}
                className={`w-full text-left border rounded-2xl p-4 transition-all ${
                  activeId === item.id
                    ? 'border-brand-300 bg-brand-50'
                    : 'border-slate-200 bg-white hover:border-brand-200'
                }`}
              >
                <div className="font-bold text-slate-800 text-sm leading-relaxed line-clamp-2">
                  {item.bound_file_name || item.title}
                </div>
                <div className="text-xs text-slate-500 mt-2">
                  {item.student_name} · {item.class_name}
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  {formatDateTime(item.bound_file_uploaded_at)}
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-2 gap-0 bg-slate-50">
        <div className="min-h-0 p-6 border-r border-slate-200 overflow-y-auto">
          {loadingDetail ? (
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Loader2 size={16} className="animate-spin" />
              正在加载会话详情...
            </div>
          ) : !detail ? (
            <div className="text-sm text-slate-400">请选择项目会话</div>
          ) : (
            <div className="space-y-6">
              <div>
                <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-2">
                  <Activity size={18} className="text-blue-500" /> 真实交互日志记录
                </h3>
                <div className="bg-white border border-slate-200 rounded-2xl p-4 max-h-[360px] overflow-y-auto text-xs text-slate-600 space-y-4 font-mono">
                  {messages.length === 0 ? (
                    <p className="text-slate-400 text-center mt-10">暂无对话记录</p>
                  ) : (
                    messages.map((msg, i) => {
                      const isUser = msg.role === 'user';
                      const isTeacher = msg.role === 'teacher';
                      return (
                        <div
                          key={i}
                          className={`flex gap-2 ${isUser ? '' : isTeacher ? 'bg-emerald-50 p-2 border border-emerald-100 rounded' : 'bg-white p-2 border border-slate-100 rounded'}`}
                        >
                          {isUser ? (
                            <User size={14} className="text-brand-600 shrink-0 mt-0.5" />
                          ) : isTeacher ? (
                            <UserCog size={14} className="text-emerald-700 shrink-0 mt-0.5" />
                          ) : (
                            <Bot size={14} className="text-slate-800 shrink-0 mt-0.5" />
                          )}
                          <span className="leading-relaxed break-all">
                            {msg.text || msg.content?.reply || JSON.stringify(msg.content)}
                          </span>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>

              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-3">
                  <ShieldAlert size={18} className="text-red-500" /> 强制教学干预注入
                </h3>

                <select
                  value={interventionType}
                  onChange={(e) => setInterventionType(e.target.value)}
                  className="w-full border border-slate-300 rounded-xl p-3 text-sm mb-3 bg-white focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                  <option value="rule">规则干预</option>
                  <option value="case">案例注入</option>
                </select>

                <textarea
                  value={interventionRule}
                  onChange={(e) => setInterventionRule(e.target.value)}
                  placeholder="例如：针对商业模式问题，强制要求学生先阅读某案例；或回答时必须优先讨论单位经济。"
                  className="w-full border border-slate-300 rounded-xl p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-red-500 mb-3 bg-red-50/30"
                  rows={4}
                />
                <button
                  onClick={handleInjectRule}
                  disabled={!interventionRule.trim()}
                  className="w-full bg-red-500 hover:bg-red-600 disabled:bg-slate-300 text-white py-2.5 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-colors"
                >
                  {ruleInjected ? <><CheckCircle size={16} /> 规则已生效</> : <><Send size={16} /> 注入规则</>}
                </button>

                {interventions.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <div className="text-xs font-bold text-slate-500">当前有效干预</div>
                    {interventions.map((item) => (
                      <div key={item.id} className="rounded-xl bg-red-50 border border-red-100 p-3">
                        <div className="text-xs text-red-600 font-bold">
                          {item.type === 'case' ? '案例注入' : '规则干预'}
                        </div>
                        <div className="text-sm text-red-700 mt-1 whitespace-pre-wrap">{item.content}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="min-h-0 p-6 overflow-y-auto">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
            <div className="flex items-center justify-between mb-4 gap-4">
              <h3 className="font-bold text-slate-800 flex items-center gap-2">
                <UserCog size={18} className="text-purple-500" /> 真实过程评估报告
              </h3>
              <button
                onClick={handleGenerateProcessEval}
                disabled={!detail?.id || evalLoading}
                className="bg-slate-800 hover:bg-slate-900 disabled:opacity-50 text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2"
              >
                {evalLoading ? <Loader2 size={16} className="animate-spin" /> : null}
                生成过程评估
              </button>
            </div>

            <div className="text-sm text-slate-500 mb-4">
              当前项目：{detail?.bound_file_name || detail?.title || '未选择'} {detail?.student_name ? `· ${detail.student_name}` : ''}
            </div>

            <div className="min-h-[320px] bg-slate-50 border border-slate-200 rounded-2xl p-4 whitespace-pre-wrap text-sm text-slate-700 leading-relaxed">
              {processReport || '点击右上角按钮，基于该项目的真实对话日志生成过程性评价。'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}