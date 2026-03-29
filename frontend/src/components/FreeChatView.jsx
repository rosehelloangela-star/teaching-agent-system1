// import React, { useState, useRef, useEffect } from 'react';
// import {
//   Plus,
//   MessageSquare,
//   Paperclip,
//   Send,
//   FileText,
//   BookOpen,
//   Briefcase,
//   Trophy,
//   Bot,
//   User,
//   Trash2,
//   Sparkles,
//   Brain,
//   ChevronDown,
//   ChevronUp,
//   Loader2,
// } from 'lucide-react';
// import { runAgentStream } from '../api';

// const modes = [
//   { id: 'learning', name: '学习模式', icon: <BookOpen size={18} />, color: 'text-blue-600', bg: 'bg-blue-50' },
//   { id: 'project', name: '项目模式', icon: <Briefcase size={18} />, color: 'text-orange-600', bg: 'bg-orange-50' },
//   { id: 'competition', name: '竞赛模式', icon: <Trophy size={18} />, color: 'text-purple-600', bg: 'bg-purple-50' },
// ];

// const suggestedPrompts = [
//   '我不清楚什么是 TAM（目标可达市场），请结合实际例子给我讲一下？',
//   '能给我一个标准的大学生双创项目商业计划书（BP）的结构示例吗？',
//   '路演答辩时，评委最喜欢问的 3 个致命问题是什么？该怎么准备？',
//   '我的项目是关于校园跑腿外卖的，我应该如何进行竞品分析？'
// ];

// export default function FreeChatView() {
//   const [sessions, setSessions] = useState(() => {
//     const saved = localStorage.getItem('freechat_sessions');
//     return saved ? JSON.parse(saved) : [{ id: 1, title: '新商业计划书诊断', messages: [] }];
//   });
//   const [activeSessionId, setActiveSessionId] = useState(() => {
//     const saved = localStorage.getItem('freechat_active_id');
//     return saved ? JSON.parse(saved) : 1;
//   });
//   const [input, setInput] = useState('');
//   const [activeMode, setActiveMode] = useState('learning');
//   const [loading, setLoading] = useState(false);
//   const [attachedFiles, setAttachedFiles] = useState([]);

//   const fileInputRef = useRef(null);
//   const chatEndRef = useRef(null);

//   useEffect(() => {
//     localStorage.setItem('freechat_sessions', JSON.stringify(sessions));
//   }, [sessions]);

//   useEffect(() => {
//     localStorage.setItem('freechat_active_id', JSON.stringify(activeSessionId));
//   }, [activeSessionId]);

//   useEffect(() => {
//     chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   }, [sessions, loading]);

//   const activeSession = sessions.find(s => s.id === activeSessionId) || sessions[0];

//   const handleNewSession = () => {
//     const newId = Date.now();
//     setSessions([{ id: newId, title: '新对话', messages: [] }, ...sessions]);
//     setActiveSessionId(newId);
//   };

//   const handleFileChange = (e) => {
//     if (e.target.files && e.target.files.length > 0) {
//       const newFiles = Array.from(e.target.files).map(file => ({
//         name: file.name,
//         size: `${(file.size / 1024).toFixed(1)} KB`,
//         raw: file,
//       }));
//       setAttachedFiles([...attachedFiles, ...newFiles]);
//     }
//   };

//   const removeFile = (index) => {
//     setAttachedFiles(attachedFiles.filter((_, i) => i !== index));
//   };

//   const updateAssistantMessage = (sessionId, messageId, updater) => {
//     setSessions(prev => prev.map(session => {
//       if (session.id !== sessionId) return session;
//       return {
//         ...session,
//         messages: session.messages.map(msg => (
//           msg.id === messageId ? updater(msg) : msg
//         )),
//       };
//     }));
//   };

//   const appendThinkingLog = (sessionId, messageId, event) => {
//     updateAssistantMessage(sessionId, messageId, msg => ({
//       ...msg,
//       thinking: {
//         ...(msg.thinking || {}),
//         status: 'thinking',
//         logs: [...(msg.thinking?.logs || []), event],
//       },
//     }));
//   };

//   const handleSubmit = async (promptText = null) => {
//     const textToProcess = typeof promptText === 'string' ? promptText : input;
//     if (!textToProcess.trim() && attachedFiles.length === 0) return;

//     const targetSessionId = activeSessionId;
//     const assistantMessageId = `assistant-${Date.now()}`;

//     const userMessage = {
//       id: `user-${Date.now()}`,
//       role: 'user',
//       text: textToProcess,
//       files: [...attachedFiles],
//       mode: activeMode,
//     };

//     const pendingAssistantMessage = {
//       id: assistantMessageId,
//       role: 'assistant',
//       mode: activeMode,
//       content: null,
//       thinking: {
//         role: '',
//         diagnosis: '',
//         tasks: [],
//         logs: [],
//         status: 'thinking',
//       },
//     };

//     setSessions(prev => prev.map(session => session.id === targetSessionId ? {
//       ...session,
//       title: session.messages.length === 0 ? `${textToProcess.slice(0, 15)}...` : session.title,
//       messages: [...session.messages, userMessage, pendingAssistantMessage],
//     } : session));

//     setInput('');
//     setAttachedFiles([]);
//     setLoading(true);

//     try {
//       const data = await runAgentStream(
//         userMessage.text || '请分析我上传的附件',
//         activeMode,
//         targetSessionId.toString(),
//         userMessage.files,
//         (event) => {
//           if (event.type === 'log') {
//             appendThinkingLog(targetSessionId, assistantMessageId, event);
//             return;
//           }

//           if (event.type === 'final') {
//             const finalData = event.data;
//             updateAssistantMessage(targetSessionId, assistantMessageId, msg => ({
//               ...msg,
//               mode: activeMode,
//               content: finalData.generated_content,
//               thinking: {
//                 ...(msg.thinking || {}),
//                 role: finalData.selected_role,
//                 diagnosis: finalData.critic_diagnosis?.raw_analysis || '',
//                 tasks: finalData.planned_tasks || [],
//                 logs: msg.thinking?.logs || [],
//                 status: 'done',
//               },
//             }));
//             return;
//           }

//           if (event.type === 'error') {
//             updateAssistantMessage(targetSessionId, assistantMessageId, msg => ({
//               ...msg,
//               isError: true,
//               text: event.message || '网络请求失败，请检查后端是否运行。',
//               thinking: {
//                 ...(msg.thinking || {}),
//                 status: 'error',
//                 logs: msg.thinking?.logs || [],
//               },
//             }));
//           }
//         }
//       );

//       if (!data) {
//         throw new Error('未收到最终结果');
//       }
//     } catch (e) {
//       updateAssistantMessage(targetSessionId, assistantMessageId, msg => ({
//         ...msg,
//         isError: true,
//         text: e.message || '网络请求失败，请检查后端是否运行。',
//         thinking: {
//           ...(msg.thinking || {}),
//           status: 'error',
//           logs: msg.thinking?.logs || [],
//         },
//       }));
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="flex-1 flex overflow-hidden">
//       <div className="w-64 bg-slate-50 border-r border-slate-200 flex flex-col hidden md:flex shrink-0">
//         <div className="p-4">
//           <button onClick={handleNewSession} className="w-full flex items-center gap-2 bg-white border border-slate-200 hover:border-brand-500 hover:text-brand-600 text-slate-700 font-medium py-2 px-4 rounded-lg shadow-sm transition-all">
//             <Plus size={18} /> 新建诊断对话
//           </button>
//         </div>
//         <div className="flex-1 overflow-y-auto px-3 pb-4 space-y-1">
//           <p className="text-xs font-bold text-slate-400 mb-2 px-2 mt-4">最近对话</p>
//           {sessions.map(session => (
//             <button key={session.id} onClick={() => setActiveSessionId(session.id)} className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg text-sm transition-all truncate ${activeSessionId === session.id ? 'bg-brand-50 text-brand-700 font-medium' : 'text-slate-600 hover:bg-slate-100'}`}>
//               <MessageSquare size={16} className={activeSessionId === session.id ? 'text-brand-500' : 'text-slate-400'} />
//               <span className="truncate">{session.title}</span>
//             </button>
//           ))}
//         </div>
//       </div>

//       <div className="flex-1 flex flex-col relative bg-white">
//         <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 bg-slate-50/50">
//           {activeSession?.messages.length === 0 ? (
//             <div className="h-full flex flex-col items-center justify-center text-slate-700 space-y-10 px-4">
//               <div className="flex flex-col items-center space-y-4">
//                 <div className="w-16 h-16 bg-gradient-to-tr from-brand-100 to-brand-50 rounded-2xl flex items-center justify-center shadow-sm border border-brand-100">
//                   <Bot size={36} className="text-brand-600" />
//                 </div>
//                 <h2 className="text-2xl font-semibold tracking-tight">今天我能帮你的项目做些什么？</h2>
//                 <p className="text-slate-500 text-sm">选择下方模式，上传BP/路演稿，或直接点击下方问题开始探索。</p>
//               </div>
//               <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-3xl">
//                 {suggestedPrompts.map((prompt, index) => (
//                   <button key={index} onClick={() => handleSubmit(prompt)} className="text-left bg-white border border-slate-200 hover:border-brand-400 hover:shadow-md transition-all p-4 rounded-xl flex items-start gap-3 group">
//                     <Sparkles size={18} className="text-brand-400 group-hover:text-brand-500 shrink-0 mt-0.5" />
//                     <span className="text-sm text-slate-600 group-hover:text-slate-800 leading-relaxed">{prompt}</span>
//                   </button>
//                 ))}
//               </div>
//             </div>
//           ) : (
//             activeSession?.messages.map((msg, index) => (
//               <div key={msg.id || index} className={`flex gap-4 max-w-4xl mx-auto ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
//                 <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${msg.role === 'user' ? 'bg-brand-100 text-brand-600' : 'bg-slate-800 text-white'}`}>
//                   {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
//                 </div>
//                 <div className={`flex flex-col gap-2 max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
//                   {msg.role === 'user' ? (
//                     <>
//                       {msg.files?.length > 0 && (
//                         <div className="flex flex-wrap gap-2 justify-end">
//                           {msg.files.map((file, i) => (
//                             <div key={i} className="flex items-center gap-2 bg-white border border-slate-200 px-3 py-2 rounded-lg shadow-sm text-sm">
//                               <FileText size={16} className="text-brand-500" />
//                               <span className="text-slate-700">{file.name}</span>
//                             </div>
//                           ))}
//                         </div>
//                       )}
//                       {msg.text && (
//                         <div className="bg-brand-600 text-white px-5 py-3 rounded-2xl rounded-tr-sm shadow-sm whitespace-pre-wrap">{msg.text}</div>
//                       )}
//                     </>
//                   ) : (
//                     <div className="bg-white border border-slate-200 px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full">
//                       {msg.isError ? (
//                         <>
//                           <ThinkingProcess thinking={msg.thinking} />
//                           <p className="text-red-500 whitespace-pre-wrap">{msg.text}</p>
//                         </>
//                       ) : (
//                         <>
//                           <ThinkingProcess thinking={msg.thinking} />
//                           {msg.mode && msg.content ? (
//                             <StructuredResponseRenderer mode={msg.mode} content={msg.content} />
//                           ) : msg.text ? (
//                             <p className="text-slate-700 whitespace-pre-wrap">{msg.text}</p>
//                           ) : null}
//                         </>
//                       )}
//                     </div>
//                   )}
//                 </div>
//               </div>
//             ))
//           )}
//           <div ref={chatEndRef} />
//         </div>

//         <div className="bg-white border-t border-slate-200 p-4 shrink-0">
//           <div className="max-w-4xl mx-auto">
//             <div className="flex items-center justify-between mb-3">
//               <div className="flex gap-3">
//                 {modes.map(mode => (
//                   <button key={mode.id} onClick={() => setActiveMode(mode.id)} className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${activeMode === mode.id ? `${mode.bg} ${mode.color} border border-${mode.color.split('-')[1]}-200 shadow-sm ring-2 ring-white` : 'text-slate-500 hover:bg-slate-100 border border-transparent'}`}>
//                     {mode.icon} {mode.name}
//                   </button>
//                 ))}
//               </div>
//               {attachedFiles.length > 0 && (
//                 <div className="flex gap-2 overflow-x-auto py-1">
//                   {attachedFiles.map((file, i) => (
//                     <span key={i} className="flex items-center gap-1 bg-slate-100 text-slate-600 px-2 py-1 rounded text-xs border border-slate-200">
//                       <FileText size={12} /> {file.name}
//                       <button onClick={() => removeFile(i)} className="text-red-400 hover:text-red-600 ml-1"><Trash2 size={12} /></button>
//                     </span>
//                   ))}
//                 </div>
//               )}
//             </div>
//             <div className="relative flex items-end bg-white border border-slate-300 focus-within:border-brand-500 focus-within:ring-1 focus-within:ring-brand-500 rounded-xl shadow-sm transition-all overflow-hidden">
//               <input type="file" multiple className="hidden" ref={fileInputRef} onChange={handleFileChange} accept=".pdf,.doc,.docx,.txt" />
//               <button onClick={() => fileInputRef.current?.click()} className="p-3 text-slate-400 hover:text-brand-500 transition-colors" title="上传文件"><Paperclip size={20} /></button>
//               <textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(); } }} placeholder="在此输入你的项目思路或问题，按 Enter 发送 (Shift+Enter 换行)..." className="flex-1 max-h-48 p-3 bg-transparent resize-none focus:outline-none text-slate-700 text-sm" rows={1} style={{ minHeight: '52px' }} />
//               <button onClick={() => handleSubmit()} disabled={loading || (!input.trim() && attachedFiles.length === 0)} className="m-2 p-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 disabled:hover:bg-brand-600 transition-colors">
//                 {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
//               </button>
//             </div>
//             <p className="text-center text-xs text-slate-400 mt-2">AI 生成内容可能存在逻辑偏差，请结合指导教师建议使用。</p>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }

// export function StructuredResponseRenderer({ mode, content }) {
//   if (!content) return null;
//   if (mode === 'learning') {
//     return (
//       <div className="space-y-4">
//         <div><h4 className="font-bold text-slate-800 text-sm mb-1">📖 概念定义</h4><p className="text-sm text-slate-600">{content.concept_definition}</p></div>
//         <div className="bg-slate-50 p-3 rounded-lg border border-slate-100"><h4 className="font-bold text-slate-800 text-sm mb-1">💡 案例解析</h4><p className="text-sm text-slate-600">{content.examples}</p></div>
//         {content.common_mistakes && (
//           <div className="bg-red-50 p-3 rounded-lg border border-red-100"><h4 className="font-bold text-red-800 text-sm mb-1">⚠️ 常见错误</h4><ul className="list-disc list-inside text-sm text-red-700">{content.common_mistakes.map((m, i) => <li key={i}>{m}</li>)}</ul></div>
//         )}
//         <div className="bg-blue-50 p-3 rounded-lg border border-blue-100"><h4 className="font-bold text-blue-800 text-sm mb-1">➡️ 下一步任务</h4><p className="text-sm text-blue-700">{content.next_task}</p></div>
//       </div>
//     );
//   }
//   if (mode === 'project') {
//     return (
//       <div className="space-y-4">
//         <div className="bg-orange-50 p-3 rounded-lg border border-orange-100"><h4 className="font-bold text-orange-800 text-sm mb-1">🔍 逻辑一致性缺陷</h4><p className="text-sm text-orange-700">{content.logic_flaw}</p></div>
//         <div><h4 className="font-bold text-slate-800 text-sm mb-1">📑 证据缺口</h4><p className="text-sm text-slate-600">{content.evidence_gap}</p></div>
//         <div className="bg-emerald-50 p-3 rounded-lg border border-emerald-100">
//           <h4 className="font-bold text-emerald-800 text-sm mb-1">🎯 唯一核心修复任务</h4><p className="text-sm text-emerald-700 mb-2">{content.only_one_task}</p>
//           <div className="bg-white/60 p-2 rounded text-xs text-emerald-800"><strong>验收标准：</strong>{content.acceptance_criteria}</div>
//         </div>
//       </div>
//     );
//   }
//   if (mode === 'competition') {
//     return (
//       <div className="space-y-4">
//         <div><h4 className="font-bold text-slate-800 text-sm mb-1">📊 Rubric 对标评分</h4><p className="text-sm text-slate-600">{content.rubric_scores}</p></div>
//         <div className="bg-red-50 p-3 rounded-lg border border-red-100"><h4 className="font-bold text-red-800 text-sm mb-1">📉 扣分点证据追踪</h4><p className="text-sm text-red-700">{content.deduction_evidence}</p></div>
//         <div>
//           <h4 className="font-bold text-slate-800 text-sm mb-2">🚀 高性价比提分策略 (Top Tasks)</h4>
//           <div className="space-y-2">
//             {content.top_tasks?.map((task, i) => (
//               <div key={i} className="bg-slate-50 border border-slate-200 p-3 rounded-lg">
//                 <p className="font-bold text-sm text-purple-700 mb-1">{task.task_desc}</p>
//                 <p className="text-xs text-slate-500 mb-2">⏱ {task.timeframe} | 💡 {task.roi_reason}</p>
//                 <div className="bg-white p-2 rounded border border-slate-100 text-xs text-slate-600 font-mono">{task.template_example}</div>
//               </div>
//             ))}
//           </div>
//         </div>
//       </div>
//     );
//   }
//   return <pre className="text-xs text-slate-600 whitespace-pre-wrap">{JSON.stringify(content, null, 2)}</pre>;
// }

// export function ThinkingProcess({ thinking }) {
//   const [isOpen, setIsOpen] = useState(false);

//   if (!thinking) return null;

//   const logs = Array.isArray(thinking.logs) ? thinking.logs : [];
//   const status = thinking.status || 'done';
//   const isThinking = status === 'thinking';
//   const isError = status === 'error';

//   return (
//     <div className="mb-4 bg-slate-50 border border-slate-200 rounded-xl overflow-hidden transition-all duration-300">
//       <button
//         onClick={() => setIsOpen(!isOpen)}
//         className="w-full flex items-center justify-between p-3 text-sm text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors"
//       >
//         <div className="flex items-center gap-2">
//           <Brain size={16} className="text-brand-500" />
//           <span className="font-medium">{isThinking ? 'Agent 正在思考中...' : 'Agent 思考过程'}</span>
//           {isThinking && <Loader2 size={14} className="animate-spin text-brand-500" />}
//         </div>
//         <div className="flex items-center gap-2">
//           {isError && <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-600">失败</span>}
//           {isThinking && <span className="text-[10px] px-2 py-0.5 rounded-full bg-brand-100 text-brand-600">进行中</span>}
//           {!isThinking && !isError && <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-600">已完成</span>}
//           {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
//         </div>
//       </button>

//       {isOpen && (
//         <div className="p-4 border-t border-slate-200 text-xs text-slate-600 space-y-4 bg-slate-100/50">
//           {logs.length === 0 && (
//             <div className="text-slate-400">正在等待后端返回执行日志...</div>
//           )}

//           {logs.length > 0 && (
//             <div>
//               <span className="font-bold text-slate-700 flex items-center gap-1 mb-2">
//                 <Brain size={12} /> 实时执行日志
//               </span>
//               <div className="space-y-2 bg-white p-3 rounded border border-slate-200">
//                 {logs.map((log, idx) => (
//                   <div key={`${log.timestamp || 't'}-${idx}`} className="flex items-start gap-2 leading-relaxed">
//                     <span className="text-[10px] text-slate-400 font-mono shrink-0 mt-0.5">{log.timestamp || '--:--:--'}</span>
//                     <span className="px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded font-mono text-[10px] shrink-0">{log.node || 'agent'}</span>
//                     <span className={`${log.level === 'error' ? 'text-red-600' : log.level === 'warning' ? 'text-orange-600' : 'text-slate-700'}`}>{log.message}</span>
//                   </div>
//                 ))}
//               </div>
//             </div>
//           )}

//           {thinking.role && (
//             <div className="flex items-center gap-2">
//               <span className="font-bold text-slate-700">调用角色：</span>
//               <span className="px-2 py-0.5 bg-slate-200 text-slate-700 rounded-full font-mono">{thinking.role}</span>
//             </div>
//           )}

//           {thinking.diagnosis && (
//             <div>
//               <span className="font-bold text-slate-700 flex items-center gap-1 mb-1">
//                 <Brain size={12} /> 结构化诊断
//               </span>
//               <pre className="whitespace-pre-wrap font-sans bg-white p-2 rounded border border-slate-200 leading-relaxed text-[11px]">
//                 {thinking.diagnosis}
//               </pre>
//             </div>
//           )}

//           {thinking.tasks && thinking.tasks.length > 0 && (
//             <div>
//               <span className="font-bold text-slate-700 flex items-center gap-1 mb-1">
//                 <Sparkles size={12} /> 任务规划
//               </span>
//               <ul className="list-decimal list-inside space-y-1 bg-white p-2 rounded border border-slate-200 text-[11px]">
//                 {thinking.tasks.map((t, i) => (
//                   <li key={i}>
//                     {t.task_desc} <span className="text-slate-400 font-mono ml-1">(Pri: {t.priority})</span>
//                   </li>
//                 ))}
//               </ul>
//             </div>
//           )}
//         </div>
//       )}
//     </div>
//   );
// }



import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Plus,
  MessageSquare,
  Send,
  FileText,
  BookOpen,
  Briefcase,
  Trophy,
  Bot,
  User,
  Sparkles,
  Brain,
  ChevronDown,
  ChevronUp,
  Loader2,
  Paperclip,
  AlertCircle,
  RefreshCcw,
} from 'lucide-react';
import {
  bindConversationFile,
  createConversation,
  fetchConversations,
  runAgentStream,
  syncConversationState,
} from '../api';

const modes = [
  {
    id: 'learning',
    name: '学习模式',
    icon: <BookOpen size={18} />,
    color: 'text-blue-600',
    bg: 'bg-blue-50',
  },
  {
    id: 'project',
    name: '项目模式',
    icon: <Briefcase size={18} />,
    color: 'text-orange-600',
    bg: 'bg-orange-50',
  },
  {
    id: 'competition',
    name: '竞赛模式',
    icon: <Trophy size={18} />,
    color: 'text-purple-600',
    bg: 'bg-purple-50',
  },
];

const suggestedPrompts = [
  '我不清楚什么是 TAM（目标可达市场），请结合实际例子给我讲一下？',
  '能给我一个标准的大学生双创项目商业计划书（BP）的结构示例吗？',
  '路演答辩时，评委最喜欢问的 3 个致命问题是什么？该怎么准备？',
  '我的项目是关于校园跑腿外卖的，我应该如何进行竞品分析？',
];

function safeParseJSON(raw, fallback) {
  if (!raw) return fallback;
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

function deriveConversationTitle(text) {
  const cleaned = (text || '').trim();
  if (!cleaned) return '新对话';
  return cleaned.length > 18 ? `${cleaned.slice(0, 18)}...` : cleaned;
}

function mapConversationFromApi(item) {
  return {
    id: item.id,
    studentId: item.student_id,
    title: item.title || '新对话',
    messages: safeParseJSON(item.chat_history, []),
    documentStatus: item.document_status || 'none',
    boundFileName: item.bound_file_name || '',
    boundFileUploadedAt: item.bound_file_uploaded_at || '',
    analysisSnapshot: safeParseJSON(item.analysis_snapshot, {}),
    lastMode: item.last_mode || 'learning',
    createdAt: item.created_at || '',
    updatedAt: item.updated_at || '',
    threadId: item.id,
  };
}

function sanitizeMessagesForSave(messages = []) {
  return messages.map((msg) => ({
    id: msg.id,
    role: msg.role,
    text: msg.text || '',
    mode: msg.mode || '',
    content: msg.content ?? null,
    isError: !!msg.isError,
    thinking: msg.thinking
      ? {
        role: msg.thinking.role || '',
        diagnosis: msg.thinking.diagnosis || '',
        tasks: Array.isArray(msg.thinking.tasks) ? msg.thinking.tasks : [],
        logs: Array.isArray(msg.thinking.logs) ? msg.thinking.logs : [],
        status: msg.thinking.status || 'done',
      }
      : null,
  }));
}

function SnapshotOverlay({ open, snapshot }) {
  if (!open) return null;

  const project = snapshot?.project?.generated_content;
  const competition = snapshot?.competition?.generated_content;

  return (
    <div className="absolute left-0 right-0 top-full z-30 mt-2 px-4">
      <div className="mx-auto max-w-5xl rounded-2xl border border-amber-200 bg-white shadow-2xl p-4 max-h-[45vh] overflow-y-auto">
        {!project && !competition && (
          <div className="text-sm text-amber-700">
            当前已绑定文档，但还没有项目模式/竞赛模式的快照数据。先运行一次对应模式，这里就会自动更新。
          </div>
        )}

        {project && (
          <div className="space-y-3 mb-5">
            <div className="flex items-center gap-2">
              <Briefcase size={16} className="text-orange-600" />
              <h4 className="font-bold text-slate-800">项目模式快照</h4>
            </div>

            <div className="bg-orange-50 border border-orange-100 rounded-xl p-3">
              <div className="text-sm font-semibold text-orange-800 mb-1">逻辑缺陷</div>
              <div className="text-sm text-orange-700">{project.logic_flaw || '暂无'}</div>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3">
              <div className="text-sm font-semibold text-slate-800 mb-1">证据缺口</div>
              <div className="text-sm text-slate-600">{project.evidence_gap || '暂无'}</div>
            </div>

            <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-3">
              <div className="text-sm font-semibold text-emerald-800 mb-1">唯一核心任务</div>
              <div className="text-sm text-emerald-700 mb-2">{project.only_one_task || '暂无'}</div>
              <div className="text-xs text-emerald-800 bg-white/70 rounded-lg p-2 border border-emerald-100">
                <strong>验收标准：</strong>
                {project.acceptance_criteria || '暂无'}
              </div>
            </div>
          </div>
        )}

        {competition && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Trophy size={16} className="text-purple-600" />
              <h4 className="font-bold text-slate-800">竞赛模式快照</h4>
            </div>

            <div className="bg-purple-50 border border-purple-100 rounded-xl p-3">
              <div className="text-sm font-semibold text-purple-800 mb-1">Rubric 评分</div>
              <div className="text-sm text-purple-700 whitespace-pre-wrap">
                {competition.rubric_scores || '暂无'}
              </div>
            </div>

            <div className="bg-red-50 border border-red-100 rounded-xl p-3">
              <div className="text-sm font-semibold text-red-800 mb-1">扣分证据</div>
              <div className="text-sm text-red-700 whitespace-pre-wrap">
                {competition.deduction_evidence || '暂无'}
              </div>
            </div>

            {Array.isArray(competition.top_tasks) && competition.top_tasks.length > 0 && (
              <div className="space-y-2">
                <div className="text-sm font-semibold text-slate-800">Top 提分任务</div>
                {competition.top_tasks.map((task, idx) => (
                  <div
                    key={`${task.task_desc}-${idx}`}
                    className="bg-slate-50 border border-slate-200 rounded-xl p-3"
                  >
                    <div className="font-semibold text-purple-700 text-sm mb-1">
                      {task.task_desc}
                    </div>
                    <div className="text-xs text-slate-500 mb-2">
                      ⏱ {task.timeframe} ｜ 💡 {task.roi_reason}
                    </div>
                    <div className="text-xs text-slate-600 bg-white rounded-lg border border-slate-100 p-2">
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

export default function FreeChatView({ currentUser }) {
  const [conversations, setConversations] = useState([]);
  const conversationsRef = useRef([]);
  const [activeConversationId, setActiveConversationId] = useState(null);

  const [input, setInput] = useState('');
  const [activeMode, setActiveMode] = useState('learning');

  const [loadingConversations, setLoadingConversations] = useState(true);
  const [creatingConversation, setCreatingConversation] = useState(false);
  const [bindingFile, setBindingFile] = useState(false);
  const [loadingReply, setLoadingReply] = useState(false);
  const [snapshotOpen, setSnapshotOpen] = useState(false);

  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    conversationsRef.current = conversations;
  }, [conversations]);

  const activeConversation = useMemo(
    () => conversations.find((item) => item.id === activeConversationId) || null,
    [conversations, activeConversationId]
  );

  const hasBoundDocument = activeConversation?.documentStatus === 'bound';

  const applyConversationUpdate = (conversationId, updater) => {
    const nextList = conversationsRef.current.map((conv) => {
      if (conv.id !== conversationId) return conv;
      return updater(conv);
    });
    conversationsRef.current = nextList;
    setConversations(nextList);
    return nextList.find((conv) => conv.id === conversationId) || null;
  };

  useEffect(() => {
    async function loadConversationList() {
      if (!currentUser?.id) {
        setLoadingConversations(false);
        return;
      }

      try {
        const data = await fetchConversations(currentUser.id);
        const mapped = data.map(mapConversationFromApi);
        conversationsRef.current = mapped;
        setConversations(mapped);
        if (mapped.length > 0) {
          setActiveConversationId(mapped[0].id);
        }
      } catch (e) {
        console.error('会话初始化失败', e);
      } finally {
        setLoadingConversations(false);
      }
    }

    loadConversationList();
  }, [currentUser?.id]);

  useEffect(() => {
    if (!hasBoundDocument && activeMode !== 'learning') {
      setActiveMode('learning');
    }
  }, [hasBoundDocument, activeMode]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [conversations, loadingReply]);

  const ensureConversation = async () => {
    if (activeConversationId) return activeConversationId;

    setCreatingConversation(true);
    try {
      const created = await createConversation(currentUser.id, '新对话');
      const mapped = mapConversationFromApi(created);
      const nextList = [mapped, ...conversationsRef.current];
      conversationsRef.current = nextList;
      setConversations(nextList);
      setActiveConversationId(mapped.id);
      return mapped.id;
    } finally {
      setCreatingConversation(false);
    }
  };

  const handleNewConversation = async () => {
    if (!currentUser?.id) return;

    setCreatingConversation(true);
    try {
      const created = await createConversation(currentUser.id, '新对话');
      const mapped = mapConversationFromApi(created);
      const nextList = [mapped, ...conversationsRef.current];
      conversationsRef.current = nextList;
      setConversations(nextList);
      setActiveConversationId(mapped.id);
      setInput('');
      setActiveMode('learning');
      setSnapshotOpen(false);
    } catch (e) {
      alert(e?.response?.data?.detail || e.message || '创建新对话失败');
    } finally {
      setCreatingConversation(false);
    }
  };

  const persistConversation = async (
    conversationId,
    messages,
    analysisSnapshot,
    title,
    lastMode
  ) => {
    try {
      await syncConversationState(
        conversationId,
        sanitizeMessagesForSave(messages),
        analysisSnapshot,
        title,
        lastMode
      );
    } catch (e) {
      console.error('会话持久化失败:', e);
    }
  };

  const handleBindFileChange = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;

    try {
      const conversationId = await ensureConversation();
      setBindingFile(true);

      const response = await bindConversationFile(conversationId, file);

      const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
        ...conv,
        documentStatus: response.document_status || 'bound',
        boundFileName: response.bound_file_name || '',
        boundFileUploadedAt: response.bound_file_uploaded_at || '',
        analysisSnapshot: safeParseJSON(response.analysis_snapshot, conv.analysisSnapshot || {}),
        messages: [
          ...conv.messages,
          {
            id: `assistant-bind-${Date.now()}`,
            role: 'assistant',
            text: `✅ 已成功绑定文档《${response.bound_file_name}》。从现在起，这个聊天框内的项目模式和竞赛模式都会默认基于该文档内容进行分析。`,
          },
        ],
      }));

      if (updatedConversation) {
        await persistConversation(
          conversationId,
          updatedConversation.messages,
          updatedConversation.analysisSnapshot,
          updatedConversation.title,
          'learning'
        );
      }

      setActiveConversationId(conversationId);
      setActiveMode('project');
    } catch (e) {
      alert(e?.response?.data?.detail || e.message || '绑定文档失败');
    } finally {
      setBindingFile(false);
    }
  };

  const updateAssistantMessage = (conversationId, messageId, updater) => {
    applyConversationUpdate(conversationId, (conv) => ({
      ...conv,
      messages: conv.messages.map((msg) => (msg.id === messageId ? updater(msg) : msg)),
    }));
  };

  const appendThinkingLog = (conversationId, messageId, event) => {
    updateAssistantMessage(conversationId, messageId, (msg) => ({
      ...msg,
      thinking: {
        ...(msg.thinking || {}),
        status: 'thinking',
        logs: [...(msg.thinking?.logs || []), event],
      },
    }));
  };

  const handleSubmit = async (presetText = null) => {
    const textToProcess = typeof presetText === 'string' ? presetText : input;
    if (!textToProcess.trim()) return;

    if ((activeMode === 'project' || activeMode === 'competition') && !hasBoundDocument) {
      alert('请先在当前聊天框绑定商业计划书文档，再使用项目模式或竞赛模式。');
      return;
    }

    const conversationId = await ensureConversation();
    const currentConv =
      conversationsRef.current.find((conv) => conv.id === conversationId) || null;

    const assistantMessageId = `assistant-${Date.now()}`;
    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      text: textToProcess,
      mode: activeMode,
    };

    const pendingAssistantMessage = {
      id: assistantMessageId,
      role: 'assistant',
      mode: activeMode,
      content: null,
      thinking: {
        role: '',
        diagnosis: '',
        tasks: [],
        logs: [],
        status: 'thinking',
      },
    };

    const nextTitle =
      currentConv && currentConv.messages.length > 0
        ? currentConv.title
        : deriveConversationTitle(textToProcess);

    const draftConversation = applyConversationUpdate(conversationId, (conv) => ({
      ...conv,
      title: nextTitle,
      lastMode: activeMode,
      messages: [...conv.messages, userMessage, pendingAssistantMessage],
    }));

    if (draftConversation) {
      await persistConversation(
        conversationId,
        draftConversation.messages,
        draftConversation.analysisSnapshot || {},
        draftConversation.title,
        activeMode
      );
    }

    setInput('');
    setLoadingReply(true);

    try {
      const data = await runAgentStream(
        userMessage.text,
        activeMode,
        currentConv?.threadId || conversationId,
        [],
        async (event) => {
          if (event.type === 'log') {
            appendThinkingLog(conversationId, assistantMessageId, event);
            return;
          }

          if (event.type === 'final') {
            const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
              ...conv,
              documentStatus: event.data.document_status || conv.documentStatus,
              boundFileName: event.data.bound_file_name || conv.boundFileName,
              boundFileUploadedAt: event.data.bound_file_uploaded_at || conv.boundFileUploadedAt,
              analysisSnapshot: event.data.analysis_snapshot || conv.analysisSnapshot,
              lastMode: activeMode,
              threadId: event.data.thread_id || conv.threadId,
              messages: conv.messages.map((msg) =>
                msg.id === assistantMessageId
                  ? {
                    ...msg,
                    mode: activeMode,
                    content: event.data.generated_content,
                    thinking: {
                      ...(msg.thinking || {}),
                      role: event.data.selected_role,
                      diagnosis: event.data.critic_diagnosis?.raw_analysis || '',
                      tasks: event.data.planned_tasks || [],
                      logs: msg.thinking?.logs || [],
                      status: 'done',
                    },
                  }
                  : msg
              ),
            }));

            if (updatedConversation) {
              await persistConversation(
                conversationId,
                updatedConversation.messages,
                updatedConversation.analysisSnapshot,
                updatedConversation.title,
                activeMode
              );
            }
            return;
          }

          if (event.type === 'error') {
            const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
              ...conv,
              messages: conv.messages.map((msg) =>
                msg.id === assistantMessageId
                  ? {
                    ...msg,
                    isError: true,
                    text: event.message || '网络请求失败，请检查后端是否运行。',
                    thinking: {
                      ...(msg.thinking || {}),
                      status: 'error',
                      logs: msg.thinking?.logs || [],
                    },
                  }
                  : msg
              ),
            }));

            if (updatedConversation) {
              await persistConversation(
                conversationId,
                updatedConversation.messages,
                updatedConversation.analysisSnapshot || {},
                updatedConversation.title,
                activeMode
              );
            }
          }
        },
        conversationId
      );

      if (!data) {
        throw new Error('未收到最终结果');
      }
    } catch (e) {
      const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
        ...conv,
        messages: conv.messages.map((msg) =>
          msg.id === assistantMessageId
            ? {
              ...msg,
              isError: true,
              text: e.message || '网络请求失败，请检查后端是否运行。',
              thinking: {
                ...(msg.thinking || {}),
                status: 'error',
                logs: msg.thinking?.logs || [],
              },
            }
            : msg
        ),
      }));

      if (updatedConversation) {
        await persistConversation(
          conversationId,
          updatedConversation.messages,
          updatedConversation.analysisSnapshot || {},
          updatedConversation.title,
          activeMode
        );
      }
    } finally {
      setLoadingReply(false);
    }
  };

  const renderModeButton = (mode) => {
    const disabled = !hasBoundDocument && (mode.id === 'project' || mode.id === 'competition');

    return (
      <button
        key={mode.id}
        onClick={() => {
          if (!disabled) setActiveMode(mode.id);
        }}
        disabled={disabled}
        className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 border ${activeMode === mode.id && !disabled
            ? `${mode.bg} ${mode.color} shadow-sm`
            : disabled
              ? 'text-slate-300 bg-slate-100 border-slate-200 cursor-not-allowed'
              : 'text-slate-500 hover:bg-slate-100 border-transparent'
          }`}
      >
        {mode.icon}
        {mode.name}
      </button>
    );
  };

  return (
    <div className="h-full min-h-0 flex overflow-hidden bg-white">
      <div className="w-72 shrink-0 h-full min-h-0 bg-slate-50 border-r border-slate-200 flex flex-col">
        <div className="p-4 shrink-0 border-b border-slate-200 space-y-3">
          <button
            onClick={handleNewConversation}
            disabled={creatingConversation}
            className="w-full flex items-center justify-center gap-2 bg-white border border-slate-200 hover:border-brand-500 hover:text-brand-600 text-slate-700 font-medium py-2.5 px-4 rounded-xl shadow-sm transition-all disabled:opacity-60"
          >
            {creatingConversation ? <Loader2 size={18} className="animate-spin" /> : <Plus size={18} />}
            新建对话
          </button>

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={bindingFile || creatingConversation}
            className="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-medium py-2.5 px-4 rounded-xl transition-colors disabled:opacity-60"
          >
            {bindingFile ? <Loader2 size={18} className="animate-spin" /> : <Paperclip size={18} />}
            上传 / 更新绑定文档
          </button>

          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".pdf,.doc,.docx,.txt,.md"
            onChange={handleBindFileChange}
          />
        </div>

        <div className="flex-1 min-h-0 overflow-y-auto px-3 py-4 space-y-2">
          <div className="text-xs font-bold text-slate-400 px-2">我的对话</div>

          {loadingConversations && (
            <div className="flex items-center gap-2 text-sm text-slate-500 px-2 py-3">
              <Loader2 size={16} className="animate-spin" />
              正在加载会话...
            </div>
          )}

          {!loadingConversations && conversations.length === 0 && (
            <div className="px-3 py-8 text-sm text-slate-400 text-center">
              还没有会话。点击上方“新建对话”开始使用。
            </div>
          )}

          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              onClick={() => {
                setActiveConversationId(conversation.id);
                setSnapshotOpen(false);
              }}
              className={`w-full text-left px-3 py-3 rounded-xl transition-all border ${activeConversationId === conversation.id
                  ? 'bg-brand-50 border-brand-200'
                  : 'bg-white border-slate-200 hover:border-brand-200'
                }`}
            >
              <div className="flex items-start justify-between gap-2 mb-1">
                <div className="flex items-center gap-2 min-w-0">
                  <MessageSquare
                    size={15}
                    className={
                      activeConversationId === conversation.id ? 'text-brand-500' : 'text-slate-400'
                    }
                  />
                  <span className="text-sm font-medium text-slate-700 truncate">
                    {conversation.title}
                  </span>
                </div>

                {conversation.documentStatus === 'bound' && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-700 shrink-0">
                    已绑文档
                  </span>
                )}
              </div>

              <div className="text-xs text-slate-400 truncate">
                {conversation.boundFileName
                  ? conversation.boundFileName
                  : conversation.messages.length > 0
                    ? conversation.messages[conversation.messages.length - 1]?.text || '暂无文本'
                    : '未绑定文档'}
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 min-w-0 h-full min-h-0 flex flex-col overflow-hidden bg-white">
        {!activeConversation ? (
          <div className="flex-1 min-h-0 flex flex-col items-center justify-center text-center px-6">
            <div className="w-16 h-16 bg-gradient-to-tr from-brand-100 to-brand-50 rounded-2xl flex items-center justify-center shadow-sm border border-brand-100 mb-5">
              <Bot size={36} className="text-brand-600" />
            </div>
            <h2 className="text-2xl font-semibold tracking-tight text-slate-800 mb-2">
              欢迎使用创新创业教学智能体
            </h2>
            <p className="text-slate-500 text-sm max-w-xl leading-relaxed">
              新建一个对话后，你可以先用学习模式提问；也可以给这个对话绑定一份 BP，让它升级为围绕该文档持续分析的工作会话。
            </p>
          </div>
        ) : (
          <>
            <div className="relative shrink-0 border-b border-slate-200 bg-white">
              <div className="px-5 py-3 border-b border-slate-100">
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-[11px] font-bold text-slate-400 mb-0.5">当前对话</div>
                    <div className="text-lg font-bold text-slate-800 truncate">
                      {activeConversation.title}
                    </div>
                  </div>

                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={bindingFile}
                    className="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-200 bg-white hover:border-brand-300 hover:text-brand-600 text-slate-600 transition-colors disabled:opacity-60 shrink-0"
                  >
                    {bindingFile ? <Loader2 size={16} className="animate-spin" /> : <RefreshCcw size={16} />}
                    {activeConversation.documentStatus === 'bound' ? '更新文档' : '绑定文档'}
                  </button>
                </div>
              </div>

              <div className="px-5 py-2 bg-red-50 border-b border-red-100">
                {hasBoundDocument ? (
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0 flex items-center gap-2">
                      <FileText size={15} className="text-red-600 shrink-0" />
                      <span className="text-sm text-red-800 truncate font-medium">
                        {activeConversation.boundFileName}
                      </span>
                      <span className="text-xs text-red-500 shrink-0">
                        {formatDateTime(activeConversation.boundFileUploadedAt)}
                      </span>
                    </div>

                    <button
                      onClick={() => setSnapshotOpen((v) => !v)}
                      className="shrink-0 inline-flex items-center gap-1 text-xs text-amber-700 bg-white border border-amber-200 rounded-full px-3 py-1 hover:bg-amber-50"
                    >
                      文档分析面板
                      {snapshotOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2 min-w-0">
                      <AlertCircle size={15} className="text-red-500 shrink-0" />
                      <span className="text-sm text-red-700 truncate">
                        当前对话尚未绑定商业计划书，仅学习模式可用
                      </span>
                    </div>

                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="shrink-0 text-xs text-red-700 bg-white border border-red-200 rounded-full px-3 py-1 hover:bg-red-50"
                    >
                      去绑定
                    </button>
                  </div>
                )}
              </div>

              <SnapshotOverlay open={snapshotOpen} snapshot={activeConversation.analysisSnapshot} />
            </div>

            <div className="flex-1 min-h-0 overflow-y-auto p-4 md:p-6 bg-slate-50/50">
              <div className="max-w-4xl mx-auto space-y-6">
                {activeConversation.messages.length === 0 ? (
                  <div className="min-h-full flex flex-col items-center justify-center text-slate-700 space-y-8 px-4">
                    <div className="flex flex-col items-center space-y-4 text-center">
                      <div className="w-16 h-16 bg-gradient-to-tr from-brand-100 to-brand-50 rounded-2xl flex items-center justify-center shadow-sm border border-brand-100">
                        <Bot size={36} className="text-brand-600" />
                      </div>
                      <h2 className="text-2xl font-semibold tracking-tight">
                        {hasBoundDocument
                          ? '文档已绑定，可以开始基于 BP 深度分析'
                          : '先学习概念，或先绑定一份商业计划书'}
                      </h2>
                      <p className="text-slate-500 text-sm text-center max-w-2xl">
                        {hasBoundDocument
                          ? '现在你可以在项目模式和竞赛模式之间切换，系统会持续基于当前绑定文档进行诊断与迭代。'
                          : '你可以先用学习模式提问基础概念；准备好后再给这个对话绑定一份 BP。'}
                      </p>
                    </div>

                    {!hasBoundDocument && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-3xl">
                        {suggestedPrompts.map((prompt, index) => (
                          <button
                            key={index}
                            onClick={() => handleSubmit(prompt)}
                            className="text-left bg-white border border-slate-200 hover:border-brand-400 hover:shadow-md transition-all p-4 rounded-xl flex items-start gap-3 group"
                          >
                            <Sparkles
                              size={18}
                              className="text-brand-400 group-hover:text-brand-500 shrink-0 mt-0.5"
                            />
                            <span className="text-sm text-slate-600 group-hover:text-slate-800 leading-relaxed">
                              {prompt}
                            </span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  activeConversation.messages.map((msg, index) => (
                    <div
                      key={msg.id || index}
                      className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                    >
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${msg.role === 'user'
                            ? 'bg-brand-100 text-brand-600'
                            : 'bg-slate-800 text-white'
                          }`}
                      >
                        {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                      </div>

                      <div
                        className={`flex flex-col gap-2 max-w-[82%] ${msg.role === 'user' ? 'items-end' : 'items-start'
                          }`}
                      >
                        {msg.role === 'user' ? (
                          <div className="bg-brand-600 text-white px-5 py-3 rounded-2xl rounded-tr-sm shadow-sm whitespace-pre-wrap">
                            {msg.text}
                          </div>
                        ) : (
                          <div className="bg-white border border-slate-200 px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full">
                            {msg.isError ? (
                              <>
                                <ThinkingProcess thinking={msg.thinking} />
                                <p className="text-red-500 whitespace-pre-wrap">{msg.text}</p>
                              </>
                            ) : (
                              <>
                                <ThinkingProcess thinking={msg.thinking} />
                                {msg.mode && msg.content ? (
                                  <StructuredResponseRenderer mode={msg.mode} content={msg.content} />
                                ) : msg.text ? (
                                  <p className="text-slate-700 whitespace-pre-wrap">{msg.text}</p>
                                ) : null}
                              </>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}

                <div ref={chatEndRef} />
              </div>
            </div>

            <div className="shrink-0 bg-white border-t border-slate-200 p-4">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-center justify-between mb-3 gap-4 flex-wrap">
                  <div className="flex gap-3 flex-wrap">{modes.map(renderModeButton)}</div>

                  {!hasBoundDocument && (
                    <div className="text-xs text-amber-600 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-full">
                      当前仅学习模式可用
                    </div>
                  )}
                </div>

                <div className="relative flex items-end bg-white border border-slate-300 focus-within:border-brand-500 focus-within:ring-1 focus-within:ring-brand-500 rounded-xl shadow-sm transition-all overflow-hidden">
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="p-3 text-slate-400 hover:text-brand-500 transition-colors"
                    title="上传并绑定文档"
                  >
                    <Paperclip size={20} />
                  </button>

                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit();
                      }
                    }}
                    placeholder={
                      hasBoundDocument
                        ? '在此继续基于当前绑定文档提问，按 Enter 发送（Shift+Enter 换行）...'
                        : '先用学习模式提问，或点击左上 / 顶部按钮绑定商业计划书文档...'
                    }
                    className="flex-1 max-h-40 p-3 bg-transparent resize-none focus:outline-none text-slate-700 text-sm"
                    rows={1}
                    style={{ minHeight: '52px' }}
                  />

                  <button
                    onClick={() => handleSubmit()}
                    disabled={loadingReply || !input.trim()}
                    className="m-2 p-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 disabled:hover:bg-brand-600 transition-colors"
                  >
                    {loadingReply ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                  </button>
                </div>

                <p className="text-center text-xs text-slate-400 mt-2">
                  AI 输出仅作为教学辅助，请结合指导教师意见使用。
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export function StructuredResponseRenderer({ mode, content }) {
  if (!content) return null;

  if (mode === 'learning') {
    return (
      <div className="space-y-4">
        <div>
          <h4 className="font-bold text-slate-800 text-sm mb-1">📖 概念定义</h4>
          <p className="text-sm text-slate-600">{content.concept_definition}</p>
        </div>

        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <h4 className="font-bold text-slate-800 text-sm mb-1">💡 案例解析</h4>
          <p className="text-sm text-slate-600">{content.examples}</p>
        </div>

        {content.common_mistakes && (
          <div className="bg-red-50 p-3 rounded-lg border border-red-100">
            <h4 className="font-bold text-red-800 text-sm mb-1">⚠️ 常见错误</h4>
            <ul className="list-disc list-inside text-sm text-red-700">
              {content.common_mistakes.map((m, i) => (
                <li key={i}>{m}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="bg-blue-50 p-3 rounded-lg border border-blue-100">
          <h4 className="font-bold text-blue-800 text-sm mb-1">➡️ 下一步任务</h4>
          <p className="text-sm text-blue-700">{content.next_task}</p>
        </div>
      </div>
    );
  }

  if (mode === 'project') {
    return (
      <div className="space-y-4">
        <div className="bg-orange-50 p-3 rounded-lg border border-orange-100">
          <h4 className="font-bold text-orange-800 text-sm mb-1">🔍 逻辑一致性缺陷</h4>
          <p className="text-sm text-orange-700">{content.logic_flaw}</p>
        </div>

        <div>
          <h4 className="font-bold text-slate-800 text-sm mb-1">📑 证据缺口</h4>
          <p className="text-sm text-slate-600">{content.evidence_gap}</p>
        </div>

        <div className="bg-emerald-50 p-3 rounded-lg border border-emerald-100">
          <h4 className="font-bold text-emerald-800 text-sm mb-1">🎯 唯一核心修复任务</h4>
          <p className="text-sm text-emerald-700 mb-2">{content.only_one_task}</p>
          <div className="bg-white/60 p-2 rounded text-xs text-emerald-800">
            <strong>验收标准：</strong>
            {content.acceptance_criteria}
          </div>
        </div>
      </div>
    );
  }

  if (mode === 'competition') {
    return (
      <div className="space-y-4">
        <div>
          <h4 className="font-bold text-slate-800 text-sm mb-1">📊 Rubric 对标评分</h4>
          <p className="text-sm text-slate-600 whitespace-pre-wrap">{content.rubric_scores}</p>
        </div>

        <div className="bg-red-50 p-3 rounded-lg border border-red-100">
          <h4 className="font-bold text-red-800 text-sm mb-1">📉 扣分点证据追踪</h4>
          <p className="text-sm text-red-700 whitespace-pre-wrap">{content.deduction_evidence}</p>
        </div>

        <div>
          <h4 className="font-bold text-slate-800 text-sm mb-2">🚀 高性价比提分策略 (Top Tasks)</h4>
          <div className="space-y-2">
            {content.top_tasks?.map((task, i) => (
              <div key={i} className="bg-slate-50 border border-slate-200 p-3 rounded-lg">
                <p className="font-bold text-sm text-purple-700 mb-1">{task.task_desc}</p>
                <p className="text-xs text-slate-500 mb-2">
                  ⏱ {task.timeframe} | 💡 {task.roi_reason}
                </p>
                <div className="bg-white p-2 rounded border border-slate-100 text-xs text-slate-600">
                  {task.template_example}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return <pre className="text-xs text-slate-600 whitespace-pre-wrap">{JSON.stringify(content, null, 2)}</pre>;
}

export function ThinkingProcess({ thinking }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!thinking) return null;

  const logs = Array.isArray(thinking.logs) ? thinking.logs : [];
  const status = thinking.status || 'done';
  const isThinking = status === 'thinking';
  const isError = status === 'error';

  return (
    <div className="mb-4 bg-slate-50 border border-slate-200 rounded-xl overflow-hidden transition-all duration-300">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 text-sm text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Brain size={16} className="text-brand-500" />
          <span className="font-medium">{isThinking ? 'Agent 正在思考中...' : 'Agent 思考过程'}</span>
          {isThinking && <Loader2 size={14} className="animate-spin text-brand-500" />}
        </div>

        <div className="flex items-center gap-2">
          {isError && <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-600">失败</span>}
          {isThinking && <span className="text-[10px] px-2 py-0.5 rounded-full bg-brand-100 text-brand-600">进行中</span>}
          {!isThinking && !isError && <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-600">已完成</span>}
          {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </button>

      {isOpen && (
        <div className="p-4 border-t border-slate-200 text-xs text-slate-600 space-y-4 bg-slate-100/50">
          {logs.length === 0 && <div className="text-slate-400">正在等待后端返回执行日志...</div>}

          {logs.length > 0 && (
            <div>
              <span className="font-bold text-slate-700 flex items-center gap-1 mb-2">
                <Brain size={12} /> 实时执行日志
              </span>
              <div className="space-y-2 bg-white p-3 rounded border border-slate-200">
                {logs.map((log, idx) => (
                  <div key={`${log.timestamp || 't'}-${idx}`} className="flex items-start gap-2 leading-relaxed">
                    <span className="text-[10px] text-slate-400 font-mono shrink-0 mt-0.5">{log.timestamp || '--:--:--'}</span>
                    <span className="px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded font-mono text-[10px] shrink-0">
                      {log.node || 'agent'}
                    </span>
                    <span className={log.level === 'error' ? 'text-red-600' : log.level === 'warning' ? 'text-orange-600' : 'text-slate-700'}>
                      {log.message}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {thinking.role && (
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-700">调用角色：</span>
              <span className="px-2 py-0.5 bg-slate-200 text-slate-700 rounded-full font-mono">{thinking.role}</span>
            </div>
          )}

          {thinking.diagnosis && (
            <div>
              <span className="font-bold text-slate-700 flex items-center gap-1 mb-1">
                <Brain size={12} /> 结构化诊断
              </span>
              <pre className="whitespace-pre-wrap font-sans bg-white p-2 rounded border border-slate-200 leading-relaxed text-[11px]">
                {thinking.diagnosis}
              </pre>
            </div>
          )}

          {thinking.tasks && thinking.tasks.length > 0 && (
            <div>
              <span className="font-bold text-slate-700 flex items-center gap-1 mb-1">
                <Sparkles size={12} /> 任务规划
              </span>
              <ul className="list-decimal list-inside space-y-1 bg-white p-2 rounded border border-slate-200 text-[11px]">
                {thinking.tasks.map((t, i) => (
                  <li key={i}>
                    {t.task_desc} <span className="text-slate-400 font-mono ml-1">(Pri: {t.priority})</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}