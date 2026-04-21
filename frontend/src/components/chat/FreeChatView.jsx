// import React, { useEffect, useMemo, useRef, useState } from 'react';
// import {
//   Plus, MessageSquare, Send, FileText, BookOpen, Briefcase, Trophy,
//   Bot, User, Sparkles, ChevronDown, ChevronUp, Loader2, Paperclip, AlertCircle, RefreshCcw, CheckCircle2, Lock, Maximize, Minimize, Network, X, Tag, Target, Lightbulb, ShieldAlert, Trash2
// } from 'lucide-react';
// import {
//   API_BASE_URL, bindConversationFile, createConversation, deleteConversation, fetchConversationDetail, fetchConversations,
//   generateProjectStageDraft, runAgentStream, syncConversationState
// } from '../../api';

// import SnapshotOverlay from './SnapshotOverlay';
// import ThinkingProcess from './ThinkingProcess';
// import StructuredResponseRenderer from './StructuredResponseRenderer';
// import LearningGraphOverlay from './LearningGraphOverlay';

// // --- 工具函数区 ---
// function safeParseJSON(raw, fallback) {
//   if (!raw) return fallback;
//   try {
//     return JSON.parse(raw);
//   } catch {
//     return fallback;
//   }
// }

// function formatDateTime(raw) {
//   if (!raw) return '未知时间';
//   const date = new Date(raw);
//   if (Number.isNaN(date.getTime())) return raw;
//   return date.toLocaleString('zh-CN', {
//     year: 'numeric',
//     month: '2-digit',
//     day: '2-digit',
//     hour: '2-digit',
//     minute: '2-digit',
//   });
// }

// function deriveConversationTitle(text) {
//   const cleaned = (text || '').trim();
//   if (!cleaned) return '新对话';
//   return cleaned.length > 18 ? `${cleaned.slice(0, 18)}...` : cleaned;
// }

// function mapConversationFromApi(item) {
//   const analysisSnapshot = safeParseJSON(item.analysis_snapshot, {});
//   const detailsLoaded =
//     Object.prototype.hasOwnProperty.call(item, 'chat_history') ||
//     Object.prototype.hasOwnProperty.call(item, 'bound_document_text') ||
//     Object.prototype.hasOwnProperty.call(item, 'analysis_snapshot') ||
//     Object.prototype.hasOwnProperty.call(item, 'kg_context');

//   return {
//     id: item.id,
//     studentId: item.student_id,
//     title: item.title || '新对话',
//     messages: safeParseJSON(item.chat_history, []),
//     documentStatus: item.document_status || 'none',
//     boundFileName: item.bound_file_name || '',
//     boundDocumentText: item.bound_document_text || '',
//     boundFileUploadedAt: item.bound_file_uploaded_at || '',
//     analysisSnapshot,
//     lastMode: item.last_mode || 'learning',
//     createdAt: item.created_at || '',
//     updatedAt: item.updated_at || '',
//     threadId: item.id,
//     detailsLoaded,

//     // ✅ 核心修复：彻底抛弃旧版的嵌套逻辑覆盖，直接读取从数据库拿出来的真实字段！
//     kgContext: safeParseJSON(item.kg_context, null),
//   };
// }

// function sanitizeMessagesForSave(messages = []) {
//   return messages.map((msg) => ({
//     ...msg,
//     id: msg.id,
//     role: msg.role,
//     text: msg.text || '',
//     mode: msg.mode || '',
//     content: msg.content ?? null,
//     isError: !!msg.isError,
//     thinking: msg.thinking
//       ? {
//         role: msg.thinking.role || '',
//         diagnosis: msg.thinking.diagnosis || '',
//         tasks: Array.isArray(msg.thinking.tasks) ? msg.thinking.tasks : [],
//         logs: Array.isArray(msg.thinking.logs) ? msg.thinking.logs : [],
//         status: msg.thinking.status || 'done',
//       }
//       : null,
//   }));
// }

// function hasUnreadTeacherMessages(messages = []) {
//   return messages.some((msg) => msg.role === 'teacher' && msg.unreadByStudent);
// }

// function getMessagePreview(msg) {
//   if (!msg) return '暂无文本';
//   if (msg.kind === 'assessment_report') return '老师下发了评估复核报告';
//   if (msg.text) return msg.text;
//   if (msg.content?.stage_draft?.title) return msg.content.stage_draft.title;
//   if (msg.content?.reply) return msg.content.reply;
//   return '暂无文本';
// }

// function buildAttachmentDownloadUrl(file) {
//   if (!file) return '#';
//   if (file.download_url?.startsWith('http')) return file.download_url;
//   return `${API_BASE_URL.replace(/\/api\/v1$/, '')}${file.download_url || ''}`;
// }
// // --- 工具函数区结束 ---

// const modes = [
//   { id: 'learning', name: '学习模式', icon: <BookOpen size={18} />, color: 'text-blue-600', bg: 'bg-blue-50' },
//   { id: 'project', name: '项目模式', icon: <Briefcase size={18} />, color: 'text-orange-600', bg: 'bg-orange-50' },
//   { id: 'competition', name: '竞赛模式', icon: <Trophy size={18} />, color: 'text-purple-600', bg: 'bg-purple-50' },
// ];

// const suggestedPrompts = [
//   '我不清楚什么是 TAM（目标可达市场），请结合实际例子给我讲一下？',
//   '能给我一个标准的大学生双创项目商业计划书（BP）的结构示例吗？',
//   '路演答辩时，评委最喜欢问的 3 个致命问题是什么？该怎么准备？',
//   '我的项目是关于校园跑腿外卖的，我应该如何进行竞品分析？',
// ];

// function getProjectStageFlow(conversation) {
//   return conversation?.analysisSnapshot?.project?.stage_flow || null;
// }

// function StageChip({ label, status }) {
//   const statusClass =
//     status === 'passed'
//       ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
//       : status === 'current'
//         ? 'bg-orange-50 border-orange-200 text-orange-700'
//         : 'bg-slate-50 border-slate-200 text-slate-400';

//   return (
//     <div className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-xs font-semibold ${statusClass}`}>
//       {status === 'passed' ? <CheckCircle2 size={14} /> : status === 'current' ? <Sparkles size={14} /> : <Lock size={14} />}
//       <span>{label}</span>
//     </div>
//   );
// }

// function ProjectStageBanner({ stageFlow, stageArtifacts = {}, onGenerateStageDraft, generatingStageId = "" }) {
//   const [expanded, setExpanded] = useState(false);
//   if (!stageFlow) return null;

//   const stages = Object.values(stageFlow.stages || {}).sort((a, b) => (a.index || 0) - (b.index || 0));
//   const currentStage = stages.find((item) => item.id === stageFlow.current_stage_id) || stages[0];
//   const passedStages = stages.filter((item) => item.status === 'passed');
//   const followups = stageFlow.current_followup_questions || [];
//   const summary = stageFlow.stage_progress_summary || {};
//   const gate = stageFlow.current_stage_gate || {};
//   const blockers = gate.blocked_reasons || [];
//   const blockerSummary = blockers.map((item) => item.label).join('、');
//   const compactStatusText = gate.ready
//     ? '已满足当前阶段进阶条件'
//     : (blockerSummary || '仍有条件未满足');

//   return (
//     <div className="px-4 py-2.5 bg-amber-50/60 border-b border-amber-100">
//       <div className="flex items-center justify-between gap-3 flex-wrap">
//         <div className="min-w-0 flex-1">
//           <div className="text-[11px] font-bold text-amber-500 mb-1">项目模式 · 三阶段推进</div>
//           <div className="flex items-center gap-2 flex-wrap">
//             <div className="text-sm font-bold text-slate-800">
//               第{stageFlow.current_stage_index}阶段【{stageFlow.current_stage_label}】
//             </div>
//             <span className="inline-flex items-center gap-1 rounded-full bg-white border border-amber-200 px-2 py-0.5 text-[11px] font-semibold text-amber-700">
//               进度 {currentStage?.progress_pct ?? 0}%
//             </span>
//             <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold border ${gate.ready ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-white border-slate-200 text-slate-600'}`}>
//               {compactStatusText}
//             </span>
//           </div>
//           <div className="text-[11px] text-slate-500 mt-1 leading-relaxed">
//             通关条件：进度≥{currentStage?.pass_threshold ?? 80}% + 关键高危规则控制在允许范围内 + 结构锚点达到要求
//           </div>
//         </div>

//         <button
//           type="button"
//           onClick={() => setExpanded((prev) => !prev)}
//           className="inline-flex items-center gap-1 rounded-lg bg-white border border-amber-200 px-2.5 py-1.5 text-xs font-semibold text-amber-700 hover:bg-amber-50 shrink-0"
//         >
//           {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
//           {expanded ? '收起详情' : '展开详情'}
//         </button>
//       </div>

//       {expanded && (
//         <div className="mt-3 space-y-3">
//           <div className="flex items-start justify-between gap-4 flex-wrap">
//             <div className="min-w-0">
//               <div className="text-xs text-slate-600 leading-relaxed">
//                 {currentStage?.coach_hint || stageFlow.current_stage_entry_message || '系统会优先围绕当前阶段问题做追问和推进。'}
//               </div>
//             </div>
//             <div className="rounded-xl bg-white border border-amber-200 px-3 py-2 text-right shadow-sm">
//               <div className="text-[11px] text-amber-600 font-semibold">当前阶段进度</div>
//               <div className="text-lg font-bold text-amber-700">{currentStage?.progress_pct ?? 0}%</div>
//               <div className="text-[11px] text-slate-500">门槛 {currentStage?.pass_threshold ?? 80}%</div>
//             </div>
//           </div>

//           <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
//             {stages.map((stage) => (
//               <StageChip key={stage.id} label={stage.label} status={stage.status} />
//             ))}
//           </div>

//           <div className="flex items-center gap-3 flex-wrap text-xs text-slate-600">
//             <span className="inline-flex items-center gap-1 rounded-full bg-white border border-slate-200 px-2.5 py-1">
//               已解 {summary.resolved_rules ?? 0}/{summary.total_rules ?? 0} 条本轮规则
//             </span>
//             <span className="inline-flex items-center gap-1 rounded-full bg-white border border-slate-200 px-2.5 py-1">
//               关键高危剩余 {summary.critical_remaining ?? 0} 条
//             </span>
//             {(summary.sticky_watchlist ?? 0) > 0 && (
//               <span className="inline-flex items-center gap-1 rounded-full bg-white border border-slate-200 px-2.5 py-1">
//                 待观察回摆 {summary.sticky_watchlist ?? 0} 条
//               </span>
//             )}
//           </div>



//           {passedStages.length > 0 && (
//             <div className="rounded-xl bg-white border border-amber-100 p-3">
//               <div className="text-xs font-bold text-amber-700 mb-2">阶段优化稿整理</div>
//               <div className="flex flex-wrap gap-2">
//                 {passedStages.map((stage) => {
//                   const hasArtifact = !!stageArtifacts?.[stage.id];
//                   const isGenerating = generatingStageId === stage.id;
//                   return (
//                     <button
//                       key={stage.id}
//                       type="button"
//                       onClick={() => onGenerateStageDraft?.(stage)}
//                       disabled={isGenerating}
//                       className="inline-flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-800 hover:bg-amber-100 disabled:opacity-60"
//                     >
//                       {isGenerating ? <Loader2 size={14} className="animate-spin" /> : <FileText size={14} />}
//                       {hasArtifact ? `重新生成${stage.short_label || stage.label}优化稿` : `生成${stage.short_label || stage.label}优化稿`}
//                     </button>
//                   );
//                 })}
//               </div>
//               <div className="text-[11px] text-slate-500 mt-2">该功能只整理已通关阶段的正式稿增量内容，不会改动原有教练回复与防代写护栏。</div>
//             </div>
//           )}

//           {blockers.length > 0 && (
//             <div className="rounded-xl bg-white border border-amber-100 p-3">
//               <div className="text-xs font-bold text-amber-700 mb-2">当前未进阶原因</div>
//               <ul className="space-y-1.5">
//                 {blockers.map((item, idx) => (
//                   <li key={`${item.code}-${idx}`} className="text-xs text-slate-700 leading-relaxed">
//                     <span className="font-semibold text-amber-700 mr-1">• {item.label}</span>
//                     {item.detail}
//                   </li>
//                 ))}
//               </ul>
//             </div>
//           )}

//           {followups.length > 0 && (
//             <div className="rounded-xl bg-white border border-amber-100 p-3">
//               <div className="text-xs font-bold text-amber-700 mb-2">本轮建议优先追问</div>
//               <ul className="space-y-1.5">
//                 {followups.slice(0, 2).map((item, idx) => (
//                   <li key={`${item.rule_id}-${idx}`} className="text-xs text-slate-700 leading-relaxed">
//                     <span className="font-semibold text-amber-700 mr-1">[{item.rule_id}]</span>
//                     {item.question}
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

// function TeacherAssessmentMessageCard({ msg }) {
//   const report = msg?.report || {};
//   const items = report.rubric_table || [];
//   return (
//     <div className="rounded-2xl border border-emerald-200 bg-white overflow-hidden shadow-sm w-full">
//       <div className="px-4 py-3 bg-emerald-50 border-b border-emerald-100 flex items-center gap-2 text-emerald-800 font-bold text-sm">
//         <Sparkles size={16} /> 教师复核评估报告
//       </div>
//       <div className="p-4 space-y-4">
//         {msg.text ? (
//           <div className="rounded-xl bg-slate-50 border border-slate-200 p-3 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
//             {msg.text}
//           </div>
//         ) : null}
//         <div className="rounded-xl border border-slate-200 overflow-hidden">
//           <div className="px-3 py-2 bg-slate-50 border-b border-slate-200 font-bold text-slate-800 text-sm">Rubric Table</div>
//           <div className="divide-y divide-slate-100">
//             {items.map((row, idx) => (
//               <div key={idx} className="p-3 space-y-2">
//                 <div className="flex items-center justify-between gap-3">
//                   <div className="font-semibold text-slate-800 text-sm">{row.dimension}</div>
//                   <div className="text-xs rounded-full px-2 py-1 bg-emerald-100 text-emerald-700 font-bold">
//                     教师评分 {row.teacher_score ?? row.score ?? 0} 分
//                   </div>
//                 </div>
//                 {row.evidence_trace ? (
//                   <div className="text-xs text-slate-600 bg-blue-50 border border-blue-100 rounded-lg p-3 leading-relaxed">
//                     <strong>Evidence Trace：</strong> {row.evidence_trace}
//                   </div>
//                 ) : null}
//               </div>
//             ))}
//           </div>
//         </div>
//         {report.revision_suggestions ? (
//           <div className="rounded-xl bg-blue-50 border border-blue-100 p-3">
//             <div className="font-bold text-blue-800 text-sm mb-2">Revision Suggestions</div>
//             <div className="text-sm text-blue-700 whitespace-pre-wrap leading-relaxed">{report.revision_suggestions}</div>
//           </div>
//         ) : null}
//         {report.instructor_review_notes ? (
//           <div className="rounded-xl bg-slate-50 border border-slate-200 p-3">
//             <div className="font-bold text-slate-800 text-sm mb-2">Instructor Review Notes</div>
//             <div className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{report.instructor_review_notes}</div>
//           </div>
//         ) : null}
//         {Array.isArray(msg.attachments) && msg.attachments.length > 0 ? (
//           <div className="flex flex-wrap gap-2">
//             {msg.attachments.map((file, idx) => (
//               <a
//                 key={idx}
//                 href={buildAttachmentDownloadUrl(file)}
//                 target="_blank"
//                 rel="noreferrer"
//                 className="text-xs px-2 py-1 rounded-full bg-white border border-emerald-200 text-emerald-700 inline-flex items-center gap-1 hover:bg-emerald-50"
//               >
//                 <Paperclip size={12} /> {file.name}
//               </a>
//             ))}
//           </div>
//         ) : null}
//       </div>
//     </div>
//   );
// }

// // --- 新增：文档预览抽屉组件 ---
// function DocumentViewerDrawer({ isOpen, onClose, title, content }) {
//   if (!isOpen) return null;

//   return (
//     <div className="fixed inset-0 z-50 flex justify-end">
//       {/* 遮罩层，点击可关闭 */}
//       <div
//         className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm transition-opacity"
//         onClick={onClose}
//       />
//       {/* 右侧滑出面板 */}
//       <div className="relative w-full max-w-lg h-full bg-white shadow-2xl flex flex-col border-l border-slate-200 animate-in slide-in-from-right duration-300">
//         <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 bg-slate-50">
//           <div className="flex items-center gap-2 min-w-0">
//             <FileText size={18} className="text-blue-600 shrink-0" />
//             <h3 className="font-bold text-slate-800 truncate text-sm">
//               {title || '文档预览'}
//             </h3>
//           </div>
//           <button
//             onClick={onClose}
//             className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-200 rounded-md transition-colors"
//           >
//             <X size={18} />
//           </button>
//         </div>
//         <div className="flex-1 overflow-y-auto p-6 bg-white">
//           {content ? (
//             <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap font-serif">
//               {content}
//             </div>
//           ) : (
//             <div className="h-full flex flex-col items-center justify-center text-slate-400 gap-2">
//               <FileText size={32} className="opacity-20" />
//               <p>暂无文档内容</p>
//             </div>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

// export default function FreeChatView({ currentUser }) {
//   const [conversations, setConversations] = useState([]);
//   const conversationsRef = useRef([]);
//   const [activeConversationId, setActiveConversationId] = useState(null);

//   const [input, setInput] = useState('');
//   const [isInputExpanded, setIsInputExpanded] = useState(false);
//   const [activeMode, setActiveMode] = useState('learning');

//   const [loadingConversations, setLoadingConversations] = useState(true);
//   const [creatingConversation, setCreatingConversation] = useState(false);
//   const [bindingFile, setBindingFile] = useState(false);
//   const [loadingReply, setLoadingReply] = useState(false);
//   const [generatingStageId, setGeneratingStageId] = useState('');
//   const [snapshotOpen, setSnapshotOpen] = useState(false);    // 项目/竞赛分析面板
//   const [kgOverlayOpen, setKgOverlayOpen] = useState(false);  // 学习模式知识图谱面板
//   const [docViewerOpen, setDocViewerOpen] = useState(false);  // <--- 新增：控制文档抽屉状态

//   const fileInputRef = useRef(null);
//   const chatEndRef = useRef(null);

//   useEffect(() => {
//     conversationsRef.current = conversations;
//   }, [conversations]);

//   const activeConversation = useMemo(
//     () => conversations.find((item) => item.id === activeConversationId) || null,
//     [conversations, activeConversationId]
//   );

//   const hasBoundDocument = activeConversation?.documentStatus === 'bound';

//   const applyConversationUpdate = (conversationId, updater) => {
//     const nextList = conversationsRef.current.map((conv) => {
//       if (conv.id !== conversationId) return conv;
//       return updater(conv);
//     });
//     conversationsRef.current = nextList;
//     setConversations(nextList);
//     return nextList.find((conv) => conv.id === conversationId) || null;
//   };

//   const loadConversationDetail = async (conversationId) => {
//     const targetConversation = conversationsRef.current.find((conv) => conv.id === conversationId);
//     if (!targetConversation || targetConversation.detailsLoaded) {
//       return targetConversation || null;
//     }

//     const detail = await fetchConversationDetail(conversationId);
//     const mappedDetail = mapConversationFromApi(detail);
//     return applyConversationUpdate(conversationId, (conv) => ({
//       ...conv,
//       ...mappedDetail,
//       detailsLoaded: true,
//     }));
//   };

//   const markConversationTeacherMessagesRead = async (conversationId) => {
//     const targetConversation = conversationsRef.current.find((conv) => conv.id === conversationId);
//     if (!targetConversation || !hasUnreadTeacherMessages(targetConversation.messages || [])) return;

//     const nextConversation = applyConversationUpdate(conversationId, (conv) => ({
//       ...conv,
//       messages: conv.messages.map((msg) =>
//         msg.role === 'teacher' && msg.unreadByStudent ? { ...msg, unreadByStudent: false } : msg
//       ),
//     }));

//     if (nextConversation) {
//       await persistConversation(
//         nextConversation.id,
//         nextConversation.messages,
//         nextConversation.analysisSnapshot || {},
//         nextConversation.title,
//         nextConversation.lastMode || activeMode,
//         nextConversation.kgContext || null
//       );
//     }
//   };

//   const handleSelectConversation = async (conversationId) => {
//     setActiveConversationId(conversationId);
//     setSnapshotOpen(false);
//     await loadConversationDetail(conversationId);
//     await markConversationTeacherMessagesRead(conversationId);
//   };

//   useEffect(() => {
//     async function loadConversationList() {
//       if (!currentUser?.id) {
//         setLoadingConversations(false);
//         return;
//       }
//       try {
//         const data = await fetchConversations(currentUser.id);
//         const mapped = data.map(mapConversationFromApi);
//         conversationsRef.current = mapped;
//         setConversations(mapped);
//         if (mapped.length > 0) {
//           setActiveConversationId(mapped[0].id);
//         }
//       } catch (e) {
//         console.error('会话初始化失败', e);
//       } finally {
//         setLoadingConversations(false);
//       }
//     }
//     loadConversationList();
//   }, [currentUser?.id]);

//   useEffect(() => {
//     if (!activeConversationId) return;
//     const active = conversationsRef.current.find((conv) => conv.id === activeConversationId);
//     if (active?.detailsLoaded) return;

//     loadConversationDetail(activeConversationId).catch((e) => {
//       console.error('加载会话详情失败', e);
//     });
//   }, [activeConversationId]);

//   useEffect(() => {
//     if (!hasBoundDocument && activeMode !== 'learning') {
//       setActiveMode('learning');
//     }
//   }, [hasBoundDocument, activeMode]);

//   useEffect(() => {
//     chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
//   }, [conversations, loadingReply]);

//   const ensureConversation = async () => {
//     if (activeConversationId) return activeConversationId;
//     setCreatingConversation(true);
//     try {
//       const created = await createConversation(currentUser.id, '新对话');
//       const mapped = mapConversationFromApi(created);
//       const nextList = [mapped, ...conversationsRef.current];
//       conversationsRef.current = nextList;
//       setConversations(nextList);
//       setActiveConversationId(mapped.id);
//       return mapped.id;
//     } finally {
//       setCreatingConversation(false);
//     }
//   };
  
//   const handleDeleteConversation = async (conversationId) => {
//   if (!currentUser?.id || !conversationId) return;

//   const targetConversation = conversationsRef.current.find((conv) => conv.id === conversationId);
//   const title = targetConversation?.title || '该对话';

//   if (!window.confirm(`确定删除“${title}”吗？删除后不可恢复。`)) return;

//   try {
//     await deleteConversation(conversationId, currentUser.id);

//     const nextList = conversationsRef.current.filter((conv) => conv.id !== conversationId);
//     conversationsRef.current = nextList;
//     setConversations(nextList);

//     if (activeConversationId === conversationId) {
//       const nextActiveId = nextList[0]?.id || null;
//       setActiveConversationId(nextActiveId);
//       setSnapshotOpen(false);
//       setKgOverlayOpen(false);
//       setDocViewerOpen(false);

//       if (!nextActiveId) {
//         setInput('');
//         setActiveMode('learning');
//       }
//     }
//   } catch (e) {
//     alert(e?.response?.data?.detail || e.message || '删除会话失败');
//   }
// };


//   const handleNewConversation = async () => {
//     if (!currentUser?.id) return;
//     setCreatingConversation(true);
//     try {
//       const created = await createConversation(currentUser.id, '新对话');
//       const mapped = mapConversationFromApi(created);
//       const nextList = [mapped, ...conversationsRef.current];
//       conversationsRef.current = nextList;
//       setConversations(nextList);
//       setActiveConversationId(mapped.id);
//       setInput('');
//       setActiveMode('learning');
//       setSnapshotOpen(false);
//     } catch (e) {
//       alert(e?.response?.data?.detail || e.message || '创建新对话失败');
//     } finally {
//       setCreatingConversation(false);
//     }
//   };

//   const persistConversation = async (conversationId, messages, analysisSnapshot, title, lastMode, kgContext) => {
//     try {
//       await syncConversationState(
//         conversationId,
//         sanitizeMessagesForSave(messages),
//         analysisSnapshot,
//         title,
//         lastMode,
//         kgContext
//       );
//     } catch (e) {
//       console.error('会话持久化失败:', e);
//     }
//   };

//   const handleBindFileChange = async (e) => {
//     const file = e.target.files?.[0];
//     e.target.value = '';
//     if (!file) return;

//     try {
//       const conversationId = await ensureConversation();
//       setBindingFile(true);

//       const response = await bindConversationFile(conversationId, file);

//       const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
//         ...conv,
//         documentStatus: response.document_status || 'bound',
//         boundFileName: response.bound_file_name || '',
//         boundFileUploadedAt: response.bound_file_uploaded_at || '',
//         boundDocumentText: response.bound_document_text || '', // <--- 新增这一行
//         analysisSnapshot: safeParseJSON(response.analysis_snapshot, conv.analysisSnapshot || {}),
//         messages: [
//           ...conv.messages,
//           {
//             id: `assistant-bind-${Date.now()}`,
//             role: 'assistant',
//             text: `✅ 已成功绑定文档《${response.bound_file_name}》。从现在起，这个聊天框内的项目模式和竞赛模式都会默认基于该文档内容进行分析。`,
//           },
//         ],
//       }));

//       if (updatedConversation) {
//         await persistConversation(
//           conversationId,
//           updatedConversation.messages,
//           updatedConversation.analysisSnapshot,
//           updatedConversation.title,
//           'learning',
//           updatedConversation.kgContext || null
//         );
//       }

//       setActiveConversationId(conversationId);
//       setActiveMode('project');
//     } catch (e) {
//       alert(e?.response?.data?.detail || e.message || '绑定文档失败');
//     } finally {
//       setBindingFile(false);
//     }
//   };

//   const updateAssistantMessage = (conversationId, messageId, updater) => {
//     applyConversationUpdate(conversationId, (conv) => ({
//       ...conv,
//       messages: conv.messages.map((msg) => (msg.id === messageId ? updater(msg) : msg)),
//     }));
//   };

//   const appendThinkingLog = (conversationId, messageId, event) => {
//     updateAssistantMessage(conversationId, messageId, (msg) => ({
//       ...msg,
//       thinking: {
//         ...(msg.thinking || {}),
//         status: 'thinking',
//         logs: [...(msg.thinking?.logs || []), event],
//       },
//     }));
//   };

//   const handleSubmit = async (presetText = null) => {
//     const textToProcess = typeof presetText === 'string' ? presetText : input;
//     if (!textToProcess.trim()) return;

//     if ((activeMode === 'project' || activeMode === 'competition') && !hasBoundDocument) {
//       alert('请先在当前聊天框绑定商业计划书文档，再使用项目模式或竞赛模式。');
//       return;
//     }

//     const conversationId = await ensureConversation();
//     const currentConv =
//       conversationsRef.current.find((conv) => conv.id === conversationId) || null;
//     const activeTeacherInterventions = (currentConv?.analysisSnapshot?.teacher_interventions || [])
//       .filter((item) => item && item.active !== false);
//     const interventionPrefix = activeTeacherInterventions.length > 0
//       ? [
//         '【教师反向干预要求】（请在本轮回答中优先执行）',
//         ...activeTeacherInterventions.map((item, idx) => `- 干预${idx + 1}：${item.content}`),
//         '',
//       ].join('\n')
//       : '';

//     const assistantMessageId = `assistant-${Date.now()}`;
//     const userMessage = {
//       id: `user-${Date.now()}`,
//       role: 'user',
//       text: textToProcess,
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

//     const nextTitle =
//       currentConv && currentConv.title && currentConv.title !== '新对话'
//         ? currentConv.title
//         : deriveConversationTitle(textToProcess);

//     const draftConversation = applyConversationUpdate(conversationId, (conv) => ({
//       ...conv,
//       title: nextTitle,
//       lastMode: activeMode,
//       messages: [...conv.messages, userMessage, pendingAssistantMessage],
//     }));

//     if (draftConversation) {
//       await persistConversation(
//         conversationId,
//         draftConversation.messages,
//         draftConversation.analysisSnapshot || {},
//         draftConversation.title,
//         activeMode,
//         draftConversation.kgContext || null
//       );
//     }

//     setInput('');
//     setLoadingReply(true);

//     try {
//       const data = await runAgentStream(
//         interventionPrefix
//           ? `${interventionPrefix}\n【学生本轮真实问题】\n${userMessage.text}`
//           : userMessage.text,
//         activeMode,
//         currentConv?.threadId || conversationId,
//         [],
//         async (event) => {
//           if (event.type === 'log') {

//             // 🌟 绝招：拦截后端的思考日志，实时提取图谱数据更新前端！
//             if (event.meta) {
//               if (event.meta.phase === 'kg_subgraph_result') {
//                 console.log("🎯 成功拦截到知识图谱数据包:", event.meta);
//                 // 如果命中，直接把 meta 里的三元组画出来
//                 const nextConversation = applyConversationUpdate(conversationId, (conv) => ({
//                   ...conv,
//                   kgContext: {
//                     hit_nodes: event.meta.hit_nodes || [],
//                     triples: event.meta.triples || []
//                   }
//                 }));
//               } else if (event.meta.phase === 'kg_no_hit') {
//                 console.log("🎯 本轮未命中图谱，清空旧数据");
//                 // 如果本轮没命中，清空上一轮的图谱
//                 const nextConversation = applyConversationUpdate(conversationId, (conv) => ({
//                   ...conv,
//                   kgContext: { hit_nodes: [], triples: [] }
//                 }));
//                 if (nextConversation) {
//                   await persistConversation(
//                     conversationId,
//                     nextConversation.messages,
//                     nextConversation.analysisSnapshot || {},
//                     nextConversation.title,
//                     nextConversation.lastMode || activeMode,
//                     nextConversation.kgContext || null
//                   );
//                 }
//               }
//             }

//             appendThinkingLog(conversationId, assistantMessageId, event);
//             return;
//           }

//           if (event.type === 'final') {
//             const updatedConversation = applyConversationUpdate(conversationId, (conv) => {
//               const nextSnapshot = event.data.analysis_snapshot || conv.analysisSnapshot;
//               const incomingKg = event.data.kg_context;
//               const nextKgContext = (incomingKg && incomingKg.hit_nodes && incomingKg.hit_nodes.length > 0)
//                 ? incomingKg
//                 : conv.kgContext;

//               const nextStageFlow = nextSnapshot?.project?.stage_flow || null;
//               const shouldAppendMilestone =
//                 activeMode === 'project' &&
//                 nextStageFlow?.just_upgraded &&
//                 nextStageFlow?.milestone_message;

//               const nextMessages = conv.messages.map((msg) =>
//                 msg.id === assistantMessageId
//                   ? {
//                     ...msg,
//                     mode: activeMode,
//                     content: event.data.generated_content,
//                     thinking: {
//                       ...(msg.thinking || {}),
//                       role: event.data.selected_role,
//                       diagnosis: event.data.critic_diagnosis?.raw_analysis || '',
//                       tasks: event.data.planned_tasks || [],
//                       logs: msg.thinking?.logs || [],
//                       status: 'done',
//                     },
//                   }
//                   : msg
//               );

//               if (shouldAppendMilestone) {
//                 nextMessages.push({
//                   id: `assistant-stage-${Date.now()}`,
//                   role: 'assistant',
//                   text: `🎉 ${nextStageFlow.milestone_message}`,
//                 });
//               }

//               return {
//                 ...conv,
//                 documentStatus: event.data.document_status || conv.documentStatus,
//                 boundFileName: event.data.bound_file_name || conv.boundFileName,
//                 boundFileUploadedAt: event.data.bound_file_uploaded_at || conv.boundFileUploadedAt,
//                 analysisSnapshot: nextSnapshot,
//                 kgContext: nextKgContext,
//                 lastMode: activeMode,
//                 threadId: event.data.thread_id || conv.threadId,
//                 messages: nextMessages,
//               };
//             });

//             if (updatedConversation) {
//               await persistConversation(
//                 conversationId,
//                 updatedConversation.messages,
//                 updatedConversation.analysisSnapshot,
//                 updatedConversation.title,
//                 activeMode,
//                 updatedConversation.kgContext || null
//               );
//             }
//             if (activeMode === 'project' || activeMode === 'competition') {
//               setSnapshotOpen(true);
//             }
//             return;
//           }

//           if (event.type === 'error') {
//             const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
//               ...conv,
//               messages: conv.messages.map((msg) =>
//                 msg.id === assistantMessageId
//                   ? {
//                     ...msg,
//                     isError: true,
//                     text: event.message || '网络请求失败，请检查后端是否运行。',
//                     thinking: {
//                       ...(msg.thinking || {}),
//                       status: 'error',
//                       logs: msg.thinking?.logs || [],
//                     },
//                   }
//                   : msg
//               ),
//             }));

//             if (updatedConversation) {
//               await persistConversation(
//                 conversationId,
//                 updatedConversation.messages,
//                 updatedConversation.analysisSnapshot || {},
//                 updatedConversation.title,
//                 activeMode,
//                 updatedConversation.kgContext || null
//               );
//             }
//           }
//         },
//         conversationId
//       );

//       if (!data) {
//         throw new Error('未收到最终结果');
//       }
//     } catch (e) {
//       const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
//         ...conv,
//         messages: conv.messages.map((msg) =>
//           msg.id === assistantMessageId
//             ? {
//               ...msg,
//               isError: true,
//               text: e.message || '网络请求失败，请检查后端是否运行。',
//               thinking: {
//                 ...(msg.thinking || {}),
//                 status: 'error',
//                 logs: msg.thinking?.logs || [],
//               },
//             }
//             : msg
//         ),
//       }));

//       if (updatedConversation) {
//         await persistConversation(
//           conversationId,
//           updatedConversation.messages,
//           updatedConversation.analysisSnapshot || {},
//           updatedConversation.title,
//           activeMode,
//           updatedConversation.kgContext || null
//         );
//       }
//     } finally {
//       setLoadingReply(false);
//     }
//   };


//   const handleGenerateStageDraft = async (stage) => {
//     if (!stage?.id) return;
//     const conversationId = activeConversationId || activeConversation?.id;
//     if (!conversationId) return;

//     setGeneratingStageId(stage.id);
//     const messageId = `stage-draft-${stage.id}-${Date.now()}`;

//     const draftConversation = applyConversationUpdate(conversationId, (conv) => ({
//       ...conv,
//       messages: [
//         ...conv.messages,
//         {
//           id: messageId,
//           role: 'assistant',
//           mode: 'project_stage_draft',
//           text: `📝 正在生成${stage.label}的优化项目书增量稿...`,
//         },
//       ],
//     }));

//     if (draftConversation) {
//       await persistConversation(
//         conversationId,
//         draftConversation.messages,
//         draftConversation.analysisSnapshot || {},
//         draftConversation.title,
//         draftConversation.lastMode || activeMode,
//         draftConversation.kgContext || null
//       );
//     }

//     try {
//       const response = await generateProjectStageDraft(conversationId, stage.id);
//       const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
//         ...conv,
//         analysisSnapshot: response.analysis_snapshot || conv.analysisSnapshot,
//         messages: conv.messages.map((msg) =>
//           msg.id === messageId
//             ? {
//               ...msg,
//               text: '',
//               mode: 'project_stage_draft',
//               content: { stage_draft: response.artifact },
//             }
//             : msg
//         ),
//       }));

//       if (updatedConversation) {
//         await persistConversation(
//           conversationId,
//           updatedConversation.messages,
//           updatedConversation.analysisSnapshot || {},
//           updatedConversation.title,
//           updatedConversation.lastMode || activeMode,
//           updatedConversation.kgContext || null
//         );
//       }
//     } catch (e) {
//       const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
//         ...conv,
//         messages: conv.messages.map((msg) =>
//           msg.id === messageId
//             ? {
//               ...msg,
//               isError: true,
//               mode: 'project_stage_draft',
//               text: e?.response?.data?.detail || e.message || '阶段优化稿生成失败，请稍后重试。',
//             }
//             : msg
//         ),
//       }));

//       if (updatedConversation) {
//         await persistConversation(
//           conversationId,
//           updatedConversation.messages,
//           updatedConversation.analysisSnapshot || {},
//           updatedConversation.title,
//           updatedConversation.lastMode || activeMode,
//           updatedConversation.kgContext || null
//         );
//       }
//     } finally {
//       setGeneratingStageId('');
//     }
//   };

//   const renderModeButton = (mode) => {
//     const disabled = !hasBoundDocument && (mode.id === 'project' || mode.id === 'competition');

//     return (
//       <button
//         key={mode.id}
//         onClick={() => {
//           if (!disabled) setActiveMode(mode.id);
//         }}
//         disabled={disabled}
//         className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 border ${activeMode === mode.id && !disabled
//           ? `${mode.bg} ${mode.color} shadow-sm`
//           : disabled
//             ? 'text-slate-300 bg-slate-100 border-slate-200 cursor-not-allowed'
//             : 'text-slate-500 hover:bg-slate-100 border-transparent'
//           }`}
//       >
//         {mode.icon}
//         {mode.name}
//       </button>
//     );
//   };

//   return (
//     <div className="h-full min-h-0 flex overflow-hidden bg-white">
//       <div className="w-72 shrink-0 h-full min-h-0 bg-slate-50 border-r border-slate-200 flex flex-col">
//         <div className="p-4 shrink-0 border-b border-slate-200 space-y-3">
//           <button
//             onClick={handleNewConversation}
//             disabled={creatingConversation}
//             className="w-full flex items-center justify-center gap-2 bg-white border border-slate-200 hover:border-brand-500 hover:text-brand-600 text-slate-700 font-medium py-2.5 px-4 rounded-xl shadow-sm transition-all disabled:opacity-60"
//           >
//             {creatingConversation ? <Loader2 size={18} className="animate-spin" /> : <Plus size={18} />}
//             新建对话
//           </button>

//           <button
//             onClick={() => fileInputRef.current?.click()}
//             disabled={bindingFile || creatingConversation}
//             className="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-medium py-2.5 px-4 rounded-xl transition-colors disabled:opacity-60"
//           >
//             {bindingFile ? <Loader2 size={18} className="animate-spin" /> : <Paperclip size={18} />}
//             上传 / 更新绑定文档
//           </button>

//           <input
//             ref={fileInputRef}
//             type="file"
//             className="hidden"
//             accept=".pdf,.doc,.docx,.txt,.md"
//             onChange={handleBindFileChange}
//           />
//         </div>

//         <div className="flex-1 min-h-0 overflow-y-auto px-3 py-4 space-y-2">
//           <div className="text-xs font-bold text-slate-400 px-2">我的对话</div>

//           {loadingConversations && (
//             <div className="flex items-center gap-2 text-sm text-slate-500 px-2 py-3">
//               <Loader2 size={16} className="animate-spin" />
//               正在加载会话...
//             </div>
//           )}

//           {!loadingConversations && conversations.length === 0 && (
//             <div className="px-3 py-8 text-sm text-slate-400 text-center">
//               还没有会话。点击上方“新建对话”开始使用。
//             </div>
//           )}

//           {conversations.map((conversation) => (
//             <div
//               key={conversation.id}
//               className={`w-full px-3 py-3 rounded-xl transition-all border ${
//                 activeConversationId === conversation.id
//                   ? 'bg-brand-50 border-brand-200'
//                   : 'bg-white border-slate-200 hover:border-brand-200'
//               }`}
//             >
//               <div className="flex items-start justify-between gap-2">
//                 <button
//                   type="button"
//                   onClick={() => {
//                     void handleSelectConversation(conversation.id);
//                   }}
//                   className="min-w-0 flex-1 text-left"
//                 >
//                   <div className="flex items-start justify-between gap-2 mb-1">
//                     <div className="flex items-center gap-2 min-w-0">
//                       <MessageSquare
//                         size={15}
//                         className={
//                           activeConversationId === conversation.id ? 'text-brand-500' : 'text-slate-400'
//                         }
//                       />
//                       <span className="text-sm font-medium text-slate-700 truncate">
//                         {conversation.title}
//                       </span>
//                     </div>
//                     <div className="flex items-center gap-1 shrink-0">
//                       {hasUnreadTeacherMessages(conversation.messages || []) && (
//                         <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
//                           教师新消息
//                         </span>
//                       )}
//                       {conversation.documentStatus === 'bound' && (
//                         <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-700 shrink-0">
//                           已绑文档
//                         </span>
//                       )}
//                     </div>
//                   </div>

//                   <div className="text-xs text-slate-400 truncate">
//                     {conversation.boundFileName
//                       ? conversation.boundFileName
//                       : conversation.messages.length > 0
//                         ? getMessagePreview(conversation.messages[conversation.messages.length - 1])
//                         : '未绑定文档'}
//                   </div>
//                 </button>

//                 <button
//                   type="button"
//                   onClick={(e) => {
//                     e.stopPropagation();
//                     void handleDeleteConversation(conversation.id);
//                   }}
//                   className="shrink-0 mt-0.5 p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
//                   title="删除对话"
//                 >
//                   <Trash2 size={15} />
//                 </button>
//               </div>
//             </div>
//           ))}
//         </div>
//       </div>

//       <div className="flex-1 min-w-0 h-full min-h-0 flex flex-col overflow-hidden bg-white">
//         {!activeConversation ? (
//           <div className="flex-1 min-h-0 flex flex-col items-center justify-center text-center px-6">
//             <div className="w-16 h-16 bg-gradient-to-tr from-brand-100 to-brand-50 rounded-2xl flex items-center justify-center shadow-sm border border-brand-100 mb-5">
//               <Bot size={36} className="text-brand-600" />
//             </div>
//             <h2 className="text-2xl font-semibold tracking-tight text-slate-800 mb-2">
//               欢迎使用创新创业教学智能体
//             </h2>
//             <p className="text-slate-500 text-sm max-w-xl leading-relaxed">
//               新建一个对话后，你可以先用学习模式提问；也可以给这个对话绑定一份 BP，让它升级为围绕该文档持续分析的工作会话。
//             </p>
//           </div>
//         ) : (
//           <>
//             <div className="relative shrink-0 border-b border-slate-200 bg-white">
//               {/* 顶部的文档与图谱状态栏 */}
//               <div className={`px-5 py-2 border-b ${hasBoundDocument ? 'bg-blue-50 border-blue-100' : 'bg-amber-50 border-amber-100'}`}>
//                 <div className="flex items-center justify-between gap-3">

//                   {/* ====== 左侧：显示当前会话状态文本 ====== */}
//                   <div className="min-w-0 flex items-center gap-2">
//                     {hasBoundDocument ? (
//                       <>
//                         <button
//                           onClick={() => setDocViewerOpen(true)}
//                           className="flex items-center gap-2 hover:bg-blue-100/50 px-2 py-1 -ml-2 rounded-lg transition-colors text-left"
//                           title="点击查看文档内容"
//                         >
//                           <FileText size={15} className="text-blue-600 shrink-0" />
//                           <span className="text-sm text-blue-800 truncate font-medium hover:underline cursor-pointer">
//                             {activeConversation.boundFileName}
//                           </span>
//                         </button>
//                         <span className="text-xs text-blue-500 shrink-0">
//                           {formatDateTime(activeConversation.boundFileUploadedAt)}
//                         </span>
//                       </>
//                     ) : (
//                       <>
//                         <AlertCircle size={15} className="text-amber-600 shrink-0" />
//                         <span className="text-sm text-amber-800 truncate font-medium">
//                           未绑定 BP 文档，目前处于通用学习模式
//                         </span>
//                       </>
//                     )}
//                   </div>

//                   {/* ====== 右侧：整齐排列的操作按钮组 ====== */}
//                   <div className="flex items-center gap-2 shrink-0">
//                     {/* 按钮 1：知识网络按钮 (只要有图谱数据就高亮) */}
//                     <button
//                       onClick={() => setKgOverlayOpen(true)}
//                       className={`inline-flex items-center gap-1 text-xs rounded-full px-3 py-1 border transition-all ${activeConversation?.kgContext?.hit_nodes?.length > 0
//                           ? 'bg-blue-50 text-blue-700 border-blue-200 shadow-sm'
//                           : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'
//                         }`}
//                     >
//                       <Network size={14} className={activeConversation?.kgContext?.hit_nodes?.length > 0 ? 'text-blue-500' : ''} />
//                       知识网络
//                       {activeConversation?.kgContext?.hit_nodes?.length > 0 && (
//                         <span className="ml-1 bg-blue-500 text-white px-1.5 py-0.5 rounded-full text-[10px] leading-none">
//                           {activeConversation.kgContext.hit_nodes.length}
//                         </span>
//                       )}
//                     </button>

//                     {/* 按钮 2：去绑定 (仅未绑文档时显示) */}
//                     {!hasBoundDocument && (
//                       <button
//                         onClick={() => fileInputRef.current?.click()}
//                         className="shrink-0 text-xs text-red-700 bg-white border border-red-200 rounded-full px-3 py-1 hover:bg-red-50"
//                       >
//                         去绑定
//                       </button>
//                     )}

//                     {/* 按钮 3：项目分析面板 (仅已绑文档时显示) */}
//                     {hasBoundDocument && (
//                       <button
//                         onClick={() => setSnapshotOpen((v) => !v)}
//                         className="shrink-0 inline-flex items-center gap-1 text-xs text-amber-700 bg-white border border-amber-200 rounded-full px-3 py-1 hover:bg-amber-50"
//                       >
//                         文档分析面板
//                         {snapshotOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
//                       </button>
//                     )}
//                   </div>
//                 </div>
//               </div>

//               {/* 教师干预横幅 */}
//               {(activeConversation.analysisSnapshot?.assessment_review?.status === 'sent' ||
//                 (activeConversation.analysisSnapshot?.teacher_interventions || []).length > 0) && (
//                   <div className="px-5 py-2 bg-emerald-50 border-b border-emerald-100 flex items-center justify-between gap-3">
//                     <div className="text-sm text-emerald-700 truncate">
//                       {activeConversation.analysisSnapshot?.assessment_review?.status === 'sent'
//                         ? '该项目已收到教师复核意见，请及时查看并根据要求修改。'
//                         : `当前会话已有 ${(activeConversation.analysisSnapshot?.teacher_interventions || []).length} 条教师干预规则正在生效。`}
//                     </div>
//                   </div>
//                 )}

//               {/* 项目阶段横幅 */}
//               {hasBoundDocument && (
//                 <ProjectStageBanner
//                   stageFlow={getProjectStageFlow(activeConversation)}
//                   stageArtifacts={activeConversation?.analysisSnapshot?.project?.stage_artifacts || {}}
//                   onGenerateStageDraft={handleGenerateStageDraft}
//                   generatingStageId={generatingStageId}
//                 />
//               )}

//               {/* === 弹窗组件挂载区 === */}
//               <SnapshotOverlay
//                 open={snapshotOpen}
//                 snapshot={activeConversation.analysisSnapshot}
//                 onClose={() => setSnapshotOpen(false)}
//               />

//               <LearningGraphOverlay
//                 open={kgOverlayOpen}
//                 kgContext={activeConversation?.kgContext}
//                 onClose={() => setKgOverlayOpen(false)}
//               />

//               <DocumentViewerDrawer
//                 isOpen={docViewerOpen}
//                 onClose={() => setDocViewerOpen(false)}
//                 title={activeConversation.boundFileName}
//                 content={activeConversation.boundDocumentText}
//               />
//             </div>

//             <div className="flex-1 min-h-0 overflow-y-auto p-4 md:p-6 bg-slate-50/50">
//               <div className="w-full space-y-6">
//                 {activeConversation.messages.length === 0 ? (
//                   <div className="min-h-full flex flex-col items-center justify-center text-slate-700 space-y-8 px-4">
//                     <div className="flex flex-col items-center space-y-4 text-center">
//                       <div className="w-16 h-16 bg-gradient-to-tr from-brand-100 to-brand-50 rounded-2xl flex items-center justify-center shadow-sm border border-brand-100">
//                         <Bot size={36} className="text-brand-600" />
//                       </div>
//                       <h2 className="text-2xl font-semibold tracking-tight">
//                         {hasBoundDocument
//                           ? '文档已绑定，可以开始基于 BP 深度分析'
//                           : '先学习概念，或先绑定一份商业计划书'}
//                       </h2>
//                       <p className="text-slate-500 text-sm text-center max-w-2xl">
//                         {hasBoundDocument
//                           ? '现在你可以在项目模式和竞赛模式之间切换，系统会持续基于当前绑定文档进行诊断与迭代。'
//                           : '你可以先用学习模式提问基础概念；准备好后再给这个对话绑定一份 BP。'}
//                       </p>
//                     </div>

//                     {!hasBoundDocument && (
//                       <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
//                         {suggestedPrompts.map((prompt, index) => (
//                           <button
//                             key={index}
//                             onClick={() => handleSubmit(prompt)}
//                             className="text-left bg-white border border-slate-200 hover:border-brand-400 hover:shadow-md transition-all p-4 rounded-xl flex items-start gap-3 group"
//                           >
//                             <Sparkles
//                               size={18}
//                               className="text-brand-400 group-hover:text-brand-500 shrink-0 mt-0.5"
//                             />
//                             <span className="text-sm text-slate-600 group-hover:text-slate-800 leading-relaxed">
//                               {prompt}
//                             </span>
//                           </button>
//                         ))}
//                       </div>
//                     )}
//                   </div>
//                 ) : (

//                   activeConversation.messages.map((msg, index) => {
//                     const isUser = msg.role === 'user';
//                     const isTeacher = msg.role === 'teacher';
//                     return (
//                       <div
//                         key={msg.id || index}
//                         className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}
//                       >
//                         <div
//                           className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${isUser
//                             ? 'bg-brand-100 text-brand-600'
//                             : isTeacher
//                               ? 'bg-emerald-100 text-emerald-700'
//                               : 'bg-slate-800 text-white'
//                             }`}
//                         >
//                           {isUser ? <User size={18} /> : isTeacher ? <MessageSquare size={18} /> : <Bot size={18} />}
//                         </div>
//                         <div
//                           className={`flex flex-col gap-2 max-w-[82%] ${isUser ? 'items-end' : 'items-start'}`}
//                         >
//                           {isUser ? (
//                             <div className={`px-5 py-3 rounded-2xl rounded-tr-sm shadow-sm whitespace-pre-wrap ${msg.teacherHighlight ? 'bg-yellow-100 text-slate-800 ring-2 ring-yellow-300' : 'bg-brand-600 text-white'}`}>
//                               {msg.text}
//                             </div>
//                           ) : isTeacher ? (
//                             msg.kind === 'assessment_report' ? (
//                               <div className="w-full">
//                                 <TeacherAssessmentMessageCard msg={msg} />
//                               </div>
//                             ) : (
//                               <div className="bg-emerald-50 border border-emerald-200 px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full">
//                                 {msg.quote && (
//                                   <div className="mb-3 bg-white/80 border border-emerald-100 rounded-xl p-3 text-xs text-emerald-800">
//                                     <div className="font-bold mb-1">引用批注</div>
//                                     <div className="opacity-80">{msg.quote.sourceRoleLabel}：</div>
//                                     <div className="mt-1 whitespace-pre-wrap">“{msg.quote.text}”</div>
//                                   </div>
//                                 )}
//                                 {msg.text && (
//                                   <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">{msg.text}</p>
//                                 )}

//                                 {/* ====== 完全新增：专门用来渲染结构化案例卡片的区域 ====== */}
//                                 {/* 如果 msg 里没有 cardData（即规则干预），这里就不会渲染，完美兼容旧版 */}
//                                 {msg.cardData && (
//                                   <div className="mt-4 bg-white border border-emerald-200 rounded-xl overflow-hidden shadow-sm flex flex-col w-full">

//                                     {/* 头部：标题与类型 (使用高级渐变色) */}
//                                     <div className="bg-gradient-to-r from-emerald-600 to-teal-500 px-4 py-3 flex items-start justify-between gap-4">
//                                       <span className="font-bold text-white text-[15px] leading-tight">
//                                         {msg.cardData.title}
//                                       </span>
//                                       <span className="text-[11px] bg-white/20 text-white px-2 py-0.5 rounded flex-shrink-0 border border-white/30 backdrop-blur-sm">
//                                         {msg.cardData.card_type || '案例'}
//                                       </span>
//                                     </div>

//                                     {/* 标签栏：行业、阶段、客群 */}
//                                     <div className="px-4 py-2.5 bg-emerald-50/50 border-b border-emerald-100 flex flex-wrap gap-2 text-xs">
//                                       {msg.cardData.industry && msg.cardData.industry !== '无' && (
//                                         <span className="bg-blue-50 text-blue-700 border border-blue-200 px-2 py-1 rounded-md flex items-center gap-1">
//                                           🏭 行业: {msg.cardData.industry}
//                                         </span>
//                                       )}
//                                       {msg.cardData.applicable_stages && msg.cardData.applicable_stages !== '无' && (
//                                         <span className="bg-amber-50 text-amber-700 border border-amber-200 px-2 py-1 rounded-md flex items-center gap-1">
//                                           📈 阶段: {msg.cardData.applicable_stages}
//                                         </span>
//                                       )}
//                                       {msg.cardData.target_customer && msg.cardData.target_customer !== '无' && (
//                                         <span className="bg-purple-50 text-purple-700 border border-purple-200 px-2 py-1 rounded-md flex items-center gap-1">
//                                           🎯 客群: {msg.cardData.target_customer}
//                                         </span>
//                                       )}
//                                     </div>

//                                     {/* 主体内容区 */}
//                                     <div className="p-4 space-y-4">

//                                       {/* 痛点与解决方案（左右并排对比视图） */}
//                                       <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
//                                         <div className="bg-red-50 p-3 rounded-lg border border-red-100 text-sm">
//                                           <div className="font-bold text-red-800 mb-1.5 flex items-center gap-1 border-b border-red-200 pb-1">
//                                             🔴 核心痛点
//                                           </div>
//                                           <div className="text-red-900/80 leading-relaxed text-xs">
//                                             {msg.cardData.core_pain_point || msg.cardData.pain_point || '无'}
//                                           </div>
//                                         </div>

//                                         <div className="bg-emerald-50 p-3 rounded-lg border border-emerald-100 text-sm">
//                                           <div className="font-bold text-emerald-800 mb-1.5 flex items-center gap-1 border-b border-emerald-200 pb-1">
//                                             🟢 解决方案
//                                           </div>
//                                           <div className="text-emerald-900/80 leading-relaxed text-xs">
//                                             {msg.cardData.solution || '无'}
//                                           </div>
//                                         </div>
//                                       </div>

//                                       {/* 商业模式（如果有的话） */}
//                                       {msg.cardData.business_model && msg.cardData.business_model !== '无' && (
//                                         <div className="bg-indigo-50 p-3 rounded-lg border border-indigo-100 text-sm">
//                                           <div className="font-bold text-indigo-800 mb-1.5 flex items-center gap-1">
//                                             💎 商业模式
//                                           </div>
//                                           <div className="text-indigo-900/80 leading-relaxed text-xs">
//                                             {msg.cardData.business_model}
//                                           </div>
//                                         </div>
//                                       )}

//                                       {/* 证据链展示区（引言样式） */}
//                                       {msg.cardData.evidence_items && msg.cardData.evidence_items !== '无' && (
//                                         <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-sm">
//                                           <div className="font-bold text-slate-700 mb-1.5 flex items-center gap-1">
//                                             🔎 关键数据与证据
//                                           </div>
//                                           <div className="text-slate-600 text-xs italic border-l-2 border-slate-300 pl-2 leading-relaxed">
//                                             {msg.cardData.evidence_items}
//                                           </div>
//                                         </div>
//                                       )}

//                                       {/* 底部关联规则 */}
//                                       {msg.cardData.covered_rule_ids && msg.cardData.covered_rule_ids !== '无' && (
//                                         <div className="text-[10px] text-slate-400 pt-2 border-t border-slate-100 flex items-center justify-end gap-1">
//                                           🏷️ 关联规则: {msg.cardData.covered_rule_ids}
//                                         </div>
//                                       )}
//                                     </div>
//                                   </div>
//                                 )}
//                                 {/* ========================================================= */}

//                                 {Array.isArray(msg.attachments) && msg.attachments.length > 0 && (
//                                   <div className="mt-3 flex flex-wrap gap-2">
//                                     {msg.attachments.map((file, idx) => (
//                                       <a
//                                         key={idx}
//                                         href={buildAttachmentDownloadUrl(file)}
//                                         target="_blank"
//                                         rel="noreferrer"
//                                         className="text-xs px-2 py-1 rounded-full bg-white border border-emerald-200 text-emerald-700 inline-flex items-center gap-1 hover:bg-emerald-50"
//                                       >
//                                         <Paperclip size={12} /> {file.name}
//                                       </a>
//                                     ))}
//                                   </div>
//                                 )}
//                               </div>
//                             )
//                           ) : (
//                             <div className={`bg-white border px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full ${msg.teacherHighlight ? 'border-yellow-300 ring-2 ring-yellow-100' : 'border-slate-200'}`}>
//                               {msg.isError ? (
//                                 <>
//                                   <ThinkingProcess thinking={msg.thinking} />
//                                   <p className="text-red-500 whitespace-pre-wrap">{msg.text}</p>
//                                 </>
//                               ) : (
//                                 <>
//                                   <ThinkingProcess thinking={msg.thinking} />
//                                   {msg.mode && msg.content ? (
//                                     <StructuredResponseRenderer mode={msg.mode} content={msg.content} />
//                                   ) : msg.text ? (
//                                     <p className="text-slate-700 whitespace-pre-wrap">{msg.text}</p>
//                                   ) : null}
//                                 </>
//                               )}
//                             </div>
//                           )}
//                         </div>
//                       </div>
//                     );
//                   })

//                 )}

//                 <div ref={chatEndRef} />
//               </div>
//             </div>

//             <div className="shrink-0 bg-white border-t border-slate-200 p-4">
//               <div className="w-full">
//                 <div className="flex items-center justify-between mb-3 gap-4 flex-wrap">
//                   <div className="flex items-center gap-3 flex-wrap">
//                     <div className="flex gap-2 flex-wrap">
//                       {modes.map(renderModeButton)}
//                     </div>
//                     {!hasBoundDocument && (
//                       <div className="text-xs text-amber-600 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-full whitespace-nowrap">
//                         当前仅学习模式可用
//                       </div>
//                     )}
//                   </div>

//                   <button
//                     onClick={() => fileInputRef.current?.click()}
//                     disabled={bindingFile}
//                     className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 bg-white hover:border-brand-300 hover:text-brand-600 text-slate-600 text-sm transition-colors disabled:opacity-60 shrink-0 ml-auto"
//                   >
//                     {bindingFile ? <Loader2 size={16} className="animate-spin" /> : <RefreshCcw size={16} />}
//                     更新文档
//                   </button>
//                 </div>

//                 <div className="relative flex items-end bg-white border border-slate-300 focus-within:border-brand-500 focus-within:ring-1 focus-within:ring-brand-500 rounded-xl shadow-sm transition-all overflow-hidden">
//                   <button
//                     onClick={() => fileInputRef.current?.click()}
//                     className="p-3 text-slate-400 hover:text-brand-500 transition-colors"
//                     title="上传并绑定文档"
//                   >
//                     <Paperclip size={20} />
//                   </button>

//                   <textarea
//                     value={input}
//                     onChange={(e) => setInput(e.target.value)}
//                     onKeyDown={(e) => {
//                       if (e.key === 'Enter' && !e.shiftKey) {
//                         e.preventDefault();
//                         handleSubmit();
//                       }
//                     }}
//                     placeholder={
//                       hasBoundDocument
//                         ? '在此继续基于当前绑定文档提问，按 Enter 发送（Shift+Enter 换行）...'
//                         : '先用学习模式提问，或点击左侧回形针绑定商业计划书文档...'
//                     }
//                     className={`flex-1 p-3 bg-transparent resize-none focus:outline-none text-slate-700 text-sm transition-all duration-200 ${isInputExpanded ? 'h-64' : 'max-h-40'}`}
//                     rows={isInputExpanded ? 10 : 1}
//                     style={{ minHeight: '52px' }}
//                   />

//                   <div className="flex items-center p-2 gap-1">
//                     <button
//                       onClick={() => setIsInputExpanded(!isInputExpanded)}
//                       className="p-2 text-slate-400 hover:text-brand-600 hover:bg-slate-100 rounded-lg transition-colors"
//                       title={isInputExpanded ? '收起输入框' : '展开输入框 (支持大篇幅长文本)'}
//                     >
//                       {isInputExpanded ? <Minimize size={18} /> : <Maximize size={18} />}
//                     </button>
//                     <button
//                       onClick={() => handleSubmit()}
//                       disabled={loadingReply || !input.trim()}
//                       className="p-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 disabled:hover:bg-brand-600 transition-colors"
//                     >
//                       {loadingReply ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
//                     </button>
//                   </div>
//                 </div>

//                 <p className="text-center text-xs text-slate-400 mt-2">
//                   AI 输出仅作为教学辅助，请结合指导教师意见使用。
//                 </p>
//               </div>
//             </div>
//           </>
//         )}
//       </div>
//     </div>
//   );
// }




import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Plus, MessageSquare, Send, FileText, BookOpen, Briefcase, Trophy,
  Bot, User, Sparkles, ChevronDown, ChevronUp, Loader2, Paperclip, AlertCircle, RefreshCcw, CheckCircle2, Lock, Maximize, Minimize, Network, X, Tag, Target, Lightbulb, ShieldAlert, Trash2, Download
} from 'lucide-react';
import {
  API_BASE_URL, bindConversationFile, createConversation, deleteConversation, fetchConversationDetail, fetchConversations,
  exportFinalProjectBookStream, generateProjectStageDraft, runAgentStream, syncConversationState
} from '../../api';

import SnapshotOverlay from './SnapshotOverlay';
import ThinkingProcess from './ThinkingProcess';
import StructuredResponseRenderer from './StructuredResponseRenderer';
import LearningGraphOverlay from './LearningGraphOverlay';

// --- 工具函数区 ---
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
  const analysisSnapshot = safeParseJSON(item.analysis_snapshot, {});
  const detailsLoaded =
    Object.prototype.hasOwnProperty.call(item, 'chat_history') ||
    Object.prototype.hasOwnProperty.call(item, 'bound_document_text') ||
    Object.prototype.hasOwnProperty.call(item, 'analysis_snapshot') ||
    Object.prototype.hasOwnProperty.call(item, 'kg_context');

  return {
    id: item.id,
    studentId: item.student_id,
    title: item.title || '新对话',
    messages: safeParseJSON(item.chat_history, []),
    documentStatus: item.document_status || 'none',
    boundFileName: item.bound_file_name || '',
    boundDocumentText: item.bound_document_text || '',
    boundFileUploadedAt: item.bound_file_uploaded_at || '',
    analysisSnapshot,
    lastMode: item.last_mode || 'learning',
    createdAt: item.created_at || '',
    updatedAt: item.updated_at || '',
    threadId: item.id,
    detailsLoaded,

    // ✅ 核心修复：彻底抛弃旧版的嵌套逻辑覆盖，直接读取从数据库拿出来的真实字段！
    kgContext: safeParseJSON(item.kg_context, null),
  };
}

function sanitizeMessagesForSave(messages = []) {
  return messages.map((msg) => ({
    ...msg,
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

function hasUnreadTeacherMessages(messages = []) {
  return messages.some((msg) => msg.role === 'teacher' && msg.unreadByStudent);
}

function getMessagePreview(msg) {
  if (!msg) return '暂无文本';
  if (msg.kind === 'assessment_report') return '老师下发了评估复核报告';
  if (msg.text) return msg.text;
  if (msg.content?.stage_draft?.title) return msg.content.stage_draft.title;
  if (msg.content?.reply) return msg.content.reply;
  return '暂无文本';
}

function buildAttachmentDownloadUrl(file) {
  if (!file) return '#';
  if (file.download_url?.startsWith('http')) return file.download_url;
  return `${API_BASE_URL.replace(/\/api\/v1$/, '')}${file.download_url || ''}`;
}
// --- 工具函数区结束 ---

const modes = [
  { id: 'learning', name: '学习模式', icon: <BookOpen size={18} />, color: 'text-blue-600', bg: 'bg-blue-50' },
  { id: 'project', name: '项目模式', icon: <Briefcase size={18} />, color: 'text-orange-600', bg: 'bg-orange-50' },
  { id: 'competition', name: '竞赛模式', icon: <Trophy size={18} />, color: 'text-purple-600', bg: 'bg-purple-50' },
];

const suggestedPrompts = [
  '我不清楚什么是 TAM（目标可达市场），请结合实际例子给我讲一下？',
  '能给我一个标准的大学生双创项目商业计划书（BP）的结构示例吗？',
  '路演答辩时，评委最喜欢问的 3 个致命问题是什么？该怎么准备？',
  '我的项目是关于校园跑腿外卖的，我应该如何进行竞品分析？',
];

function getProjectStageFlow(conversation) {
  return conversation?.analysisSnapshot?.project?.stage_flow || null;
}

function StageChip({ label, status }) {
  const statusClass =
    status === 'passed'
      ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
      : status === 'current'
        ? 'bg-orange-50 border-orange-200 text-orange-700'
        : 'bg-slate-50 border-slate-200 text-slate-400';

  return (
    <div className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-xs font-semibold ${statusClass}`}>
      {status === 'passed' ? <CheckCircle2 size={14} /> : status === 'current' ? <Sparkles size={14} /> : <Lock size={14} />}
      <span>{label}</span>
    </div>
  );
}

function ProjectStageBanner({ stageFlow, stageArtifacts = {}, onGenerateStageDraft, generatingStageId = "", onGenerateFinalExport, finalExportState = null, finalExportFile = null }) {
  const [expanded, setExpanded] = useState(false);
  if (!stageFlow) return null;

  const stages = Object.values(stageFlow.stages || {}).sort((a, b) => (a.index || 0) - (b.index || 0));
  const currentStage = stages.find((item) => item.id === stageFlow.current_stage_id) || stages[0];
  const passedStages = stages.filter((item) => item.status === 'passed');
  const allStagesPassed = stages.length > 0 && passedStages.length === stages.length && stageFlow.overall_status === 'completed';
  const followups = stageFlow.current_followup_questions || [];
  const summary = stageFlow.stage_progress_summary || {};
  const gate = stageFlow.current_stage_gate || {};
  const blockers = gate.blocked_reasons || [];
  const blockerSummary = blockers.map((item) => item.label).join('、');
  const compactStatusText = gate.ready
    ? '已满足当前阶段进阶条件'
    : (blockerSummary || '仍有条件未满足');

  return (
    <div className="px-4 py-2.5 bg-amber-50/60 border-b border-amber-100">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="min-w-0 flex-1">
          <div className="text-[11px] font-bold text-amber-500 mb-1">项目模式 · 三阶段推进</div>
          <div className="flex items-center gap-2 flex-wrap">
            <div className="text-sm font-bold text-slate-800">
              第{stageFlow.current_stage_index}阶段【{stageFlow.current_stage_label}】
            </div>
            <span className="inline-flex items-center gap-1 rounded-full bg-white border border-amber-200 px-2 py-0.5 text-[11px] font-semibold text-amber-700">
              进度 {currentStage?.progress_pct ?? 0}%
            </span>
            <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold border ${gate.ready ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-white border-slate-200 text-slate-600'}`}>
              {compactStatusText}
            </span>
          </div>
          <div className="text-[11px] text-slate-500 mt-1 leading-relaxed">
            通关条件：进度≥{currentStage?.pass_threshold ?? 80}% + 关键高危规则控制在允许范围内 + 结构锚点达到要求
          </div>
        </div>

        <button
          type="button"
          onClick={() => setExpanded((prev) => !prev)}
          className="inline-flex items-center gap-1 rounded-lg bg-white border border-amber-200 px-2.5 py-1.5 text-xs font-semibold text-amber-700 hover:bg-amber-50 shrink-0"
        >
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          {expanded ? '收起详情' : '展开详情'}
        </button>
      </div>

      {expanded && (
        <div className="mt-3 space-y-3">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="min-w-0">
              <div className="text-xs text-slate-600 leading-relaxed">
                {currentStage?.coach_hint || stageFlow.current_stage_entry_message || '系统会优先围绕当前阶段问题做追问和推进。'}
              </div>
            </div>
            <div className="rounded-xl bg-white border border-amber-200 px-3 py-2 text-right shadow-sm">
              <div className="text-[11px] text-amber-600 font-semibold">当前阶段进度</div>
              <div className="text-lg font-bold text-amber-700">{currentStage?.progress_pct ?? 0}%</div>
              <div className="text-[11px] text-slate-500">门槛 {currentStage?.pass_threshold ?? 80}%</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            {stages.map((stage) => (
              <StageChip key={stage.id} label={stage.label} status={stage.status} />
            ))}
          </div>

          <div className="flex items-center gap-3 flex-wrap text-xs text-slate-600">
            <span className="inline-flex items-center gap-1 rounded-full bg-white border border-slate-200 px-2.5 py-1">
              已解 {summary.resolved_rules ?? 0}/{summary.total_rules ?? 0} 条本轮规则
            </span>
            <span className="inline-flex items-center gap-1 rounded-full bg-white border border-slate-200 px-2.5 py-1">
              关键高危剩余 {summary.critical_remaining ?? 0} 条
            </span>
            {(summary.sticky_watchlist ?? 0) > 0 && (
              <span className="inline-flex items-center gap-1 rounded-full bg-white border border-slate-200 px-2.5 py-1">
                待观察回摆 {summary.sticky_watchlist ?? 0} 条
              </span>
            )}
          </div>



          {passedStages.length > 0 && (
            <div className="rounded-xl bg-white border border-amber-100 p-3 space-y-3">
              <div>
                <div className="text-xs font-bold text-amber-700 mb-2">阶段优化稿整理</div>
                <div className="flex flex-wrap gap-2">
                  {passedStages.map((stage) => {
                    const hasArtifact = !!stageArtifacts?.[stage.id];
                    const isGenerating = generatingStageId === stage.id;
                    return (
                      <button
                        key={stage.id}
                        type="button"
                        onClick={() => onGenerateStageDraft?.(stage)}
                        disabled={isGenerating || finalExportState?.status === 'running'}
                        className="inline-flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-800 hover:bg-amber-100 disabled:opacity-60"
                      >
                        {isGenerating ? <Loader2 size={14} className="animate-spin" /> : <FileText size={14} />}
                        {hasArtifact ? `重新生成${stage.short_label || stage.label}优化稿` : `生成${stage.short_label || stage.label}优化稿`}
                      </button>
                    );
                  })}
                </div>
                <div className="text-[11px] text-slate-500 mt-2">该功能只整理已通关阶段的正式稿增量内容，不会改动原有教练回复与防代写护栏。</div>
              </div>

              {allStagesPassed && (
                <div className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-3">
                  <div className="flex items-center justify-between gap-3 flex-wrap">
                    <div className="min-w-0">
                      <div className="text-xs font-bold text-emerald-700 mb-1">最终优化项目书导出</div>
                      <div className="text-xs text-slate-600 leading-relaxed">
                        三阶段已全部通关。点击后系统会自动补齐缺失的阶段增量稿，并整合为一份可直接下载的 Word 正稿。
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => onGenerateFinalExport?.()}
                      disabled={finalExportState?.status === 'running'}
                      className="inline-flex items-center gap-2 rounded-xl border border-emerald-300 bg-white px-3 py-2 text-xs font-semibold text-emerald-700 hover:bg-emerald-100 disabled:opacity-60"
                    >
                      {finalExportState?.status === 'running' ? <Loader2 size={14} className="animate-spin" /> : <FileText size={14} />}
                      {finalExportState?.status === 'running' ? '正在导出最终优化项目书…' : '导出最终优化项目书（Word）'}
                    </button>
                  </div>

                  {finalExportState?.status === 'running' && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-[11px] text-emerald-700 mb-1">
                        <span>{finalExportState?.message || '正在导出…'}</span>
                        <span>{Math.max(0, Math.min(100, finalExportState?.percent || 0))}%</span>
                      </div>
                      <div className="h-2 rounded-full bg-white/80 border border-emerald-100 overflow-hidden">
                        <div
                          className="h-full bg-emerald-500 transition-all duration-300"
                          style={{ width: `${Math.max(0, Math.min(100, finalExportState?.percent || 0))}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {finalExportState?.status === 'success' && (
                    <div className="mt-3 space-y-2">
                      <div className="text-[11px] text-emerald-700">
                        {finalExportState?.message || '最终优化项目书已导出完成。'}
                      </div>
                      {finalExportFile?.download_url && (
                        <div className="flex flex-wrap items-center gap-2">
                          <a
                            href={buildAttachmentDownloadUrl(finalExportFile)}
                            download={finalExportFile?.name || '最终优化项目书.docx'}
                            className="inline-flex items-center gap-2 rounded-xl border border-emerald-300 bg-white px-3 py-2 text-xs font-semibold text-emerald-700 hover:bg-emerald-100"
                          >
                            <Download size={14} />
                            下载最终优化项目书（Word）
                          </a>
                          <span className="text-[11px] text-slate-500">若浏览器拦截了自动下载，可点击这里重新下载。</span>
                        </div>
                      )}
                    </div>
                  )}

                  {finalExportState?.status === 'error' && (
                    <div className="mt-3 space-y-2">
                      <div className="text-[11px] text-rose-600">
                        {finalExportState?.message || '导出失败，请稍后重试。'}
                      </div>
                      {finalExportFile?.download_url && (
                        <div className="flex flex-wrap items-center gap-2">
                          <a
                            href={buildAttachmentDownloadUrl(finalExportFile)}
                            download={finalExportFile?.name || '最终优化项目书.docx'}
                            className="inline-flex items-center gap-2 rounded-xl border border-emerald-300 bg-white px-3 py-2 text-xs font-semibold text-emerald-700 hover:bg-emerald-100"
                          >
                            <Download size={14} />
                            下载上一次已生成的 Word
                          </a>
                        </div>
                      )}
                    </div>
                  )}

                  {finalExportState?.status !== 'running' && finalExportState?.status !== 'success' && finalExportFile?.download_url && (
                    <div className="mt-3 flex flex-wrap items-center gap-2">
                      <a
                        href={buildAttachmentDownloadUrl(finalExportFile)}
                        download={finalExportFile?.name || '最终优化项目书.docx'}
                        className="inline-flex items-center gap-2 rounded-xl border border-emerald-300 bg-white px-3 py-2 text-xs font-semibold text-emerald-700 hover:bg-emerald-100"
                      >
                        <Download size={14} />
                        下载最近一次导出的 Word
                      </a>
                      <span className="text-[11px] text-slate-500">这份文件会保留在当前会话中，可随时重新下载。</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {blockers.length > 0 && (
            <div className="rounded-xl bg-white border border-amber-100 p-3">
              <div className="text-xs font-bold text-amber-700 mb-2">当前未进阶原因</div>
              <ul className="space-y-1.5">
                {blockers.map((item, idx) => (
                  <li key={`${item.code}-${idx}`} className="text-xs text-slate-700 leading-relaxed">
                    <span className="font-semibold text-amber-700 mr-1">• {item.label}</span>
                    {item.detail}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {followups.length > 0 && (
            <div className="rounded-xl bg-white border border-amber-100 p-3">
              <div className="text-xs font-bold text-amber-700 mb-2">本轮建议优先追问</div>
              <ul className="space-y-1.5">
                {followups.slice(0, 2).map((item, idx) => (
                  <li key={`${item.rule_id}-${idx}`} className="text-xs text-slate-700 leading-relaxed">
                    <span className="font-semibold text-amber-700 mr-1">[{item.rule_id}]</span>
                    {item.question}
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

function TeacherAssessmentMessageCard({ msg }) {
  const report = msg?.report || {};
  const items = report.rubric_table || [];
  return (
    <div className="rounded-2xl border border-emerald-200 bg-white overflow-hidden shadow-sm w-full">
      <div className="px-4 py-3 bg-emerald-50 border-b border-emerald-100 flex items-center gap-2 text-emerald-800 font-bold text-sm">
        <Sparkles size={16} /> 教师复核评估报告
      </div>
      <div className="p-4 space-y-4">
        {msg.text ? (
          <div className="rounded-xl bg-slate-50 border border-slate-200 p-3 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
            {msg.text}
          </div>
        ) : null}
        <div className="rounded-xl border border-slate-200 overflow-hidden">
          <div className="px-3 py-2 bg-slate-50 border-b border-slate-200 font-bold text-slate-800 text-sm">Rubric Table</div>
          <div className="divide-y divide-slate-100">
            {items.map((row, idx) => (
              <div key={idx} className="p-3 space-y-2">
                <div className="flex items-center justify-between gap-3">
                  <div className="font-semibold text-slate-800 text-sm">{row.dimension}</div>
                  <div className="text-xs rounded-full px-2 py-1 bg-emerald-100 text-emerald-700 font-bold">
                    教师评分 {row.teacher_score ?? row.score ?? 0} 分
                  </div>
                </div>
                {row.evidence_trace ? (
                  <div className="text-xs text-slate-600 bg-blue-50 border border-blue-100 rounded-lg p-3 leading-relaxed">
                    <strong>Evidence Trace：</strong> {row.evidence_trace}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        </div>
        {report.revision_suggestions ? (
          <div className="rounded-xl bg-blue-50 border border-blue-100 p-3">
            <div className="font-bold text-blue-800 text-sm mb-2">Revision Suggestions</div>
            <div className="text-sm text-blue-700 whitespace-pre-wrap leading-relaxed">{report.revision_suggestions}</div>
          </div>
        ) : null}
        {report.instructor_review_notes ? (
          <div className="rounded-xl bg-slate-50 border border-slate-200 p-3">
            <div className="font-bold text-slate-800 text-sm mb-2">Instructor Review Notes</div>
            <div className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{report.instructor_review_notes}</div>
          </div>
        ) : null}
        {Array.isArray(msg.attachments) && msg.attachments.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {msg.attachments.map((file, idx) => (
              <a
                key={idx}
                href={buildAttachmentDownloadUrl(file)}
                target="_blank"
                rel="noreferrer"
                className="text-xs px-2 py-1 rounded-full bg-white border border-emerald-200 text-emerald-700 inline-flex items-center gap-1 hover:bg-emerald-50"
              >
                <Paperclip size={12} /> {file.name}
              </a>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}

// --- 新增：文档预览抽屉组件 ---
function DocumentViewerDrawer({ isOpen, onClose, title, content }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* 遮罩层，点击可关闭 */}
      <div
        className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      {/* 右侧滑出面板 */}
      <div className="relative w-full max-w-lg h-full bg-white shadow-2xl flex flex-col border-l border-slate-200 animate-in slide-in-from-right duration-300">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 bg-slate-50">
          <div className="flex items-center gap-2 min-w-0">
            <FileText size={18} className="text-blue-600 shrink-0" />
            <h3 className="font-bold text-slate-800 truncate text-sm">
              {title || '文档预览'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-200 rounded-md transition-colors"
          >
            <X size={18} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-6 bg-white">
          {content ? (
            <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap font-serif">
              {content}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 gap-2">
              <FileText size={32} className="opacity-20" />
              <p>暂无文档内容</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function FreeChatView({ currentUser }) {
  const [conversations, setConversations] = useState([]);
  const conversationsRef = useRef([]);
  const [activeConversationId, setActiveConversationId] = useState(null);

  const [input, setInput] = useState('');
  const [isInputExpanded, setIsInputExpanded] = useState(false);
  const [activeMode, setActiveMode] = useState('learning');

  const [loadingConversations, setLoadingConversations] = useState(true);
  const [creatingConversation, setCreatingConversation] = useState(false);
  const [bindingFile, setBindingFile] = useState(false);
  const [loadingReply, setLoadingReply] = useState(false);
  const [generatingStageId, setGeneratingStageId] = useState('');
  const [finalExportState, setFinalExportState] = useState({ status: 'idle', percent: 0, message: '' });
  const [snapshotOpen, setSnapshotOpen] = useState(false);    // 项目/竞赛分析面板
  const [kgOverlayOpen, setKgOverlayOpen] = useState(false);  // 学习模式知识图谱面板
  const [docViewerOpen, setDocViewerOpen] = useState(false);  // <--- 新增：控制文档抽屉状态

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
  const finalExportFile = activeConversation?.analysisSnapshot?.project?.final_export?.file || null;

  const applyConversationUpdate = (conversationId, updater) => {
    const nextList = conversationsRef.current.map((conv) => {
      if (conv.id !== conversationId) return conv;
      return updater(conv);
    });
    conversationsRef.current = nextList;
    setConversations(nextList);
    return nextList.find((conv) => conv.id === conversationId) || null;
  };

  const loadConversationDetail = async (conversationId) => {
    const targetConversation = conversationsRef.current.find((conv) => conv.id === conversationId);
    if (!targetConversation || targetConversation.detailsLoaded) {
      return targetConversation || null;
    }

    const detail = await fetchConversationDetail(conversationId);
    const mappedDetail = mapConversationFromApi(detail);
    return applyConversationUpdate(conversationId, (conv) => ({
      ...conv,
      ...mappedDetail,
      detailsLoaded: true,
    }));
  };

  const markConversationTeacherMessagesRead = async (conversationId) => {
    const targetConversation = conversationsRef.current.find((conv) => conv.id === conversationId);
    if (!targetConversation || !hasUnreadTeacherMessages(targetConversation.messages || [])) return;

    const nextConversation = applyConversationUpdate(conversationId, (conv) => ({
      ...conv,
      messages: conv.messages.map((msg) =>
        msg.role === 'teacher' && msg.unreadByStudent ? { ...msg, unreadByStudent: false } : msg
      ),
    }));

    if (nextConversation) {
      await persistConversation(
        nextConversation.id,
        nextConversation.messages,
        nextConversation.analysisSnapshot || {},
        nextConversation.title,
        nextConversation.lastMode || activeMode,
        nextConversation.kgContext || null
      );
    }
  };

  const handleSelectConversation = async (conversationId) => {
    setActiveConversationId(conversationId);
    setSnapshotOpen(false);
    await loadConversationDetail(conversationId);
    await markConversationTeacherMessagesRead(conversationId);
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
    setFinalExportState({ status: 'idle', percent: 0, message: '' });
  }, [activeConversationId]);

  useEffect(() => {
    if (!activeConversationId) return;
    const active = conversationsRef.current.find((conv) => conv.id === activeConversationId);
    if (active?.detailsLoaded) return;

    loadConversationDetail(activeConversationId).catch((e) => {
      console.error('加载会话详情失败', e);
    });
  }, [activeConversationId]);

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

  const handleDeleteConversation = async (conversationId) => {
    if (!currentUser?.id || !conversationId) return;

    const targetConversation = conversationsRef.current.find((conv) => conv.id === conversationId);
    const title = targetConversation?.title || '该对话';

    if (!window.confirm(`确定删除“${title}”吗？删除后不可恢复。`)) return;

    try {
      await deleteConversation(conversationId, currentUser.id);

      const nextList = conversationsRef.current.filter((conv) => conv.id !== conversationId);
      conversationsRef.current = nextList;
      setConversations(nextList);

      if (activeConversationId === conversationId) {
        const nextActiveId = nextList[0]?.id || null;
        setActiveConversationId(nextActiveId);
        setSnapshotOpen(false);
        setKgOverlayOpen(false);
        setDocViewerOpen(false);

        if (!nextActiveId) {
          setInput('');
          setActiveMode('learning');
        }
      }
    } catch (e) {
      alert(e?.response?.data?.detail || e.message || '删除会话失败');
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

  const persistConversation = async (conversationId, messages, analysisSnapshot, title, lastMode, kgContext) => {
    try {
      await syncConversationState(
        conversationId,
        sanitizeMessagesForSave(messages),
        analysisSnapshot,
        title,
        lastMode,
        kgContext
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
        boundDocumentText: response.bound_document_text || '', // <--- 新增这一行
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
          'learning',
          updatedConversation.kgContext || null
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
    const activeTeacherInterventions = (currentConv?.analysisSnapshot?.teacher_interventions || [])
      .filter((item) => item && item.active !== false);
    const interventionPrefix = activeTeacherInterventions.length > 0
      ? [
        '【教师反向干预要求】（请在本轮回答中优先执行）',
        ...activeTeacherInterventions.map((item, idx) => `- 干预${idx + 1}：${item.content}`),
        '',
      ].join('\n')
      : '';

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
      currentConv && currentConv.title && currentConv.title !== '新对话'
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
        activeMode,
        draftConversation.kgContext || null
      );
    }

    setInput('');
    setLoadingReply(true);

    try {
      const data = await runAgentStream(
        interventionPrefix
          ? `${interventionPrefix}\n【学生本轮真实问题】\n${userMessage.text}`
          : userMessage.text,
        activeMode,
        currentConv?.threadId || conversationId,
        [],
        async (event) => {
          if (event.type === 'log') {

            // 🌟 绝招：拦截后端的思考日志，实时提取图谱数据更新前端！
            if (event.meta) {
              if (event.meta.phase === 'kg_subgraph_result') {
                console.log("🎯 成功拦截到知识图谱数据包:", event.meta);
                // 如果命中，直接把 meta 里的三元组画出来
                const nextConversation = applyConversationUpdate(conversationId, (conv) => ({
                  ...conv,
                  kgContext: {
                    hit_nodes: event.meta.hit_nodes || [],
                    triples: event.meta.triples || []
                  }
                }));
              } else if (event.meta.phase === 'kg_no_hit') {
                console.log("🎯 本轮未命中图谱，清空旧数据");
                // 如果本轮没命中，清空上一轮的图谱
                const nextConversation = applyConversationUpdate(conversationId, (conv) => ({
                  ...conv,
                  kgContext: { hit_nodes: [], triples: [] }
                }));
                if (nextConversation) {
                  await persistConversation(
                    conversationId,
                    nextConversation.messages,
                    nextConversation.analysisSnapshot || {},
                    nextConversation.title,
                    nextConversation.lastMode || activeMode,
                    nextConversation.kgContext || null
                  );
                }
              }
            }

            appendThinkingLog(conversationId, assistantMessageId, event);
            return;
          }

          if (event.type === 'final') {
            const updatedConversation = applyConversationUpdate(conversationId, (conv) => {
              const nextSnapshot = event.data.analysis_snapshot || conv.analysisSnapshot;
              const incomingKg = event.data.kg_context;
              const nextKgContext = (incomingKg && incomingKg.hit_nodes && incomingKg.hit_nodes.length > 0)
                ? incomingKg
                : conv.kgContext;

              const nextStageFlow = nextSnapshot?.project?.stage_flow || null;
              const shouldAppendMilestone =
                activeMode === 'project' &&
                nextStageFlow?.just_upgraded &&
                nextStageFlow?.milestone_message;

              const nextMessages = conv.messages.map((msg) =>
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
              );

              if (shouldAppendMilestone) {
                nextMessages.push({
                  id: `assistant-stage-${Date.now()}`,
                  role: 'assistant',
                  text: `🎉 ${nextStageFlow.milestone_message}`,
                });
              }

              return {
                ...conv,
                documentStatus: event.data.document_status || conv.documentStatus,
                boundFileName: event.data.bound_file_name || conv.boundFileName,
                boundFileUploadedAt: event.data.bound_file_uploaded_at || conv.boundFileUploadedAt,
                analysisSnapshot: nextSnapshot,
                kgContext: nextKgContext,
                lastMode: activeMode,
                threadId: event.data.thread_id || conv.threadId,
                messages: nextMessages,
              };
            });

            if (updatedConversation) {
              await persistConversation(
                conversationId,
                updatedConversation.messages,
                updatedConversation.analysisSnapshot,
                updatedConversation.title,
                activeMode,
                updatedConversation.kgContext || null
              );
            }
            if (activeMode === 'project' || activeMode === 'competition') {
              setSnapshotOpen(true);
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
                activeMode,
                updatedConversation.kgContext || null
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
          activeMode,
          updatedConversation.kgContext || null
        );
      }
    } finally {
      setLoadingReply(false);
    }
  };


  const handleGenerateStageDraft = async (stage) => {
    if (!stage?.id) return;
    const conversationId = activeConversationId || activeConversation?.id;
    if (!conversationId) return;

    setGeneratingStageId(stage.id);
    const messageId = `stage-draft-${stage.id}-${Date.now()}`;

    const draftConversation = applyConversationUpdate(conversationId, (conv) => ({
      ...conv,
      messages: [
        ...conv.messages,
        {
          id: messageId,
          role: 'assistant',
          mode: 'project_stage_draft',
          text: `📝 正在生成${stage.label}的优化项目书增量稿...`,
        },
      ],
    }));

    if (draftConversation) {
      await persistConversation(
        conversationId,
        draftConversation.messages,
        draftConversation.analysisSnapshot || {},
        draftConversation.title,
        draftConversation.lastMode || activeMode,
        draftConversation.kgContext || null
      );
    }

    try {
      const response = await generateProjectStageDraft(conversationId, stage.id);
      const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
        ...conv,
        analysisSnapshot: response.analysis_snapshot || conv.analysisSnapshot,
        messages: conv.messages.map((msg) =>
          msg.id === messageId
            ? {
              ...msg,
              text: '',
              mode: 'project_stage_draft',
              content: { stage_draft: response.artifact },
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
          updatedConversation.lastMode || activeMode,
          updatedConversation.kgContext || null
        );
      }
    } catch (e) {
      const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
        ...conv,
        messages: conv.messages.map((msg) =>
          msg.id === messageId
            ? {
              ...msg,
              isError: true,
              mode: 'project_stage_draft',
              text: e?.response?.data?.detail || e.message || '阶段优化稿生成失败，请稍后重试。',
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
          updatedConversation.lastMode || activeMode,
          updatedConversation.kgContext || null
        );
      }
    } finally {
      setGeneratingStageId('');
    }
  };



  const handleGenerateFinalProjectExport = async () => {
    const conversationId = activeConversationId || activeConversation?.id;
    if (!conversationId) return;

    setFinalExportState({ status: 'running', percent: 3, message: '正在校验阶段状态…' });

    try {
      const response = await exportFinalProjectBookStream(conversationId, async (event) => {
        if (event.type === 'progress') {
          setFinalExportState({
            status: 'running',
            percent: Number(event.percent || 0),
            message: event.message || '正在导出最终优化项目书…',
          });
        }
      });

      const file = response?.file || {};
      const nextSnapshot = response?.analysis_snapshot || activeConversation?.analysisSnapshot || {};
      const successText = response?.artifact?.generation_notice
        ? `✅ 最终优化项目书已导出完成。${response.artifact.generation_notice}`
        : '✅ 最终优化项目书已导出完成，请下载 Word 文档查看。';

      const updatedConversation = applyConversationUpdate(conversationId, (conv) => ({
        ...conv,
        analysisSnapshot: nextSnapshot,
        messages: [
          ...conv.messages,
          {
            id: `project-final-export-${Date.now()}`,
            role: 'assistant',
            text: successText,
            attachments: file?.download_url ? [{
              name: file.name || '最终优化项目书.docx',
              download_url: file.download_url,
              content_type: file.content_type || '',
            }] : [],
          },
        ],
      }));

      if (updatedConversation) {
        await persistConversation(
          conversationId,
          updatedConversation.messages,
          updatedConversation.analysisSnapshot || {},
          updatedConversation.title,
          updatedConversation.lastMode || activeMode,
          updatedConversation.kgContext || null
        );
      }

      setFinalExportState({
        status: 'success',
        percent: 100,
        message: '最终优化项目书已导出完成。若浏览器未自动开始下载，可点击下方按钮手动下载。',
      });

      if (file?.download_url) {
        const href = buildAttachmentDownloadUrl(file);
        const link = document.createElement('a');
        link.href = href;
        link.download = file?.name || '最终优化项目书.docx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (e) {
      const message = e?.message || e?.response?.data?.detail || '最终优化项目书导出失败，请稍后重试。';
      setFinalExportState({ status: 'error', percent: 0, message });
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
            <div
              key={conversation.id}
              className={`w-full px-3 py-3 rounded-xl transition-all border ${activeConversationId === conversation.id
                  ? 'bg-brand-50 border-brand-200'
                  : 'bg-white border-slate-200 hover:border-brand-200'
                }`}
            >
              <div className="flex items-start justify-between gap-2">
                <button
                  type="button"
                  onClick={() => {
                    void handleSelectConversation(conversation.id);
                  }}
                  className="min-w-0 flex-1 text-left"
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
                    <div className="flex items-center gap-1 shrink-0">
                      {hasUnreadTeacherMessages(conversation.messages || []) && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
                          教师新消息
                        </span>
                      )}
                      {conversation.documentStatus === 'bound' && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-700 shrink-0">
                          已绑文档
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="text-xs text-slate-400 truncate">
                    {conversation.boundFileName
                      ? conversation.boundFileName
                      : conversation.messages.length > 0
                        ? getMessagePreview(conversation.messages[conversation.messages.length - 1])
                        : '未绑定文档'}
                  </div>
                </button>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    void handleDeleteConversation(conversation.id);
                  }}
                  className="shrink-0 mt-0.5 p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                  title="删除对话"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
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
              {/* 顶部的文档与图谱状态栏 */}
              <div className={`px-5 py-2 border-b ${hasBoundDocument ? 'bg-blue-50 border-blue-100' : 'bg-amber-50 border-amber-100'}`}>
                <div className="flex items-center justify-between gap-3">

                  {/* ====== 左侧：显示当前会话状态文本 ====== */}
                  <div className="min-w-0 flex items-center gap-2">
                    {hasBoundDocument ? (
                      <>
                        <button
                          onClick={() => setDocViewerOpen(true)}
                          className="flex items-center gap-2 hover:bg-blue-100/50 px-2 py-1 -ml-2 rounded-lg transition-colors text-left"
                          title="点击查看文档内容"
                        >
                          <FileText size={15} className="text-blue-600 shrink-0" />
                          <span className="text-sm text-blue-800 truncate font-medium hover:underline cursor-pointer">
                            {activeConversation.boundFileName}
                          </span>
                        </button>
                        <span className="text-xs text-blue-500 shrink-0">
                          {formatDateTime(activeConversation.boundFileUploadedAt)}
                        </span>
                      </>
                    ) : (
                      <>
                        <AlertCircle size={15} className="text-amber-600 shrink-0" />
                        <span className="text-sm text-amber-800 truncate font-medium">
                          未绑定 BP 文档，目前处于通用学习模式
                        </span>
                      </>
                    )}
                  </div>

                  {/* ====== 右侧：整齐排列的操作按钮组 ====== */}
                  <div className="flex items-center gap-2 shrink-0">
                    {/* 按钮 1：知识网络按钮 (只要有图谱数据就高亮) */}
                    <button
                      onClick={() => setKgOverlayOpen(true)}
                      className={`inline-flex items-center gap-1 text-xs rounded-full px-3 py-1 border transition-all ${activeConversation?.kgContext?.hit_nodes?.length > 0
                        ? 'bg-blue-50 text-blue-700 border-blue-200 shadow-sm'
                        : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'
                        }`}
                    >
                      <Network size={14} className={activeConversation?.kgContext?.hit_nodes?.length > 0 ? 'text-blue-500' : ''} />
                      知识网络
                      {activeConversation?.kgContext?.hit_nodes?.length > 0 && (
                        <span className="ml-1 bg-blue-500 text-white px-1.5 py-0.5 rounded-full text-[10px] leading-none">
                          {activeConversation.kgContext.hit_nodes.length}
                        </span>
                      )}
                    </button>

                    {/* 按钮 2：去绑定 (仅未绑文档时显示) */}
                    {!hasBoundDocument && (
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="shrink-0 text-xs text-red-700 bg-white border border-red-200 rounded-full px-3 py-1 hover:bg-red-50"
                      >
                        去绑定
                      </button>
                    )}

                    {/* 按钮 3：项目分析面板 (仅已绑文档时显示) */}
                    {hasBoundDocument && (
                      <button
                        onClick={() => setSnapshotOpen((v) => !v)}
                        className="shrink-0 inline-flex items-center gap-1 text-xs text-amber-700 bg-white border border-amber-200 rounded-full px-3 py-1 hover:bg-amber-50"
                      >
                        文档分析面板
                        {snapshotOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* 教师干预横幅 */}
              {(activeConversation.analysisSnapshot?.assessment_review?.status === 'sent' ||
                (activeConversation.analysisSnapshot?.teacher_interventions || []).length > 0) && (
                  <div className="px-5 py-2 bg-emerald-50 border-b border-emerald-100 flex items-center justify-between gap-3">
                    <div className="text-sm text-emerald-700 truncate">
                      {activeConversation.analysisSnapshot?.assessment_review?.status === 'sent'
                        ? '该项目已收到教师复核意见，请及时查看并根据要求修改。'
                        : `当前会话已有 ${(activeConversation.analysisSnapshot?.teacher_interventions || []).length} 条教师干预规则正在生效。`}
                    </div>
                  </div>
                )}

              {/* 项目阶段横幅 */}
              {hasBoundDocument && (
                <ProjectStageBanner
                  stageFlow={getProjectStageFlow(activeConversation)}
                  stageArtifacts={activeConversation?.analysisSnapshot?.project?.stage_artifacts || {}}
                  onGenerateStageDraft={handleGenerateStageDraft}
                  generatingStageId={generatingStageId}
                  onGenerateFinalExport={handleGenerateFinalProjectExport}
                  finalExportState={finalExportState}
                  finalExportFile={finalExportFile}
                />
              )}

              {/* === 弹窗组件挂载区 === */}
              <SnapshotOverlay
                open={snapshotOpen}
                snapshot={activeConversation.analysisSnapshot}
                onClose={() => setSnapshotOpen(false)}
              />

              <LearningGraphOverlay
                open={kgOverlayOpen}
                kgContext={activeConversation?.kgContext}
                onClose={() => setKgOverlayOpen(false)}
              />

              <DocumentViewerDrawer
                isOpen={docViewerOpen}
                onClose={() => setDocViewerOpen(false)}
                title={activeConversation.boundFileName}
                content={activeConversation.boundDocumentText}
              />
            </div>

            <div className="flex-1 min-h-0 overflow-y-auto p-4 md:p-6 bg-slate-50/50">
              <div className="w-full space-y-6">
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
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
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

                  activeConversation.messages.map((msg, index) => {
                    const isUser = msg.role === 'user';
                    const isTeacher = msg.role === 'teacher';
                    return (
                      <div
                        key={msg.id || index}
                        className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}
                      >
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${isUser
                            ? 'bg-brand-100 text-brand-600'
                            : isTeacher
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-slate-800 text-white'
                            }`}
                        >
                          {isUser ? <User size={18} /> : isTeacher ? <MessageSquare size={18} /> : <Bot size={18} />}
                        </div>
                        <div
                          className={`flex flex-col gap-2 max-w-[82%] ${isUser ? 'items-end' : 'items-start'}`}
                        >
                          {isUser ? (
                            <div className={`px-5 py-3 rounded-2xl rounded-tr-sm shadow-sm whitespace-pre-wrap ${msg.teacherHighlight ? 'bg-yellow-100 text-slate-800 ring-2 ring-yellow-300' : 'bg-brand-600 text-white'}`}>
                              {msg.text}
                            </div>
                          ) : isTeacher ? (
                            msg.kind === 'assessment_report' ? (
                              <div className="w-full">
                                <TeacherAssessmentMessageCard msg={msg} />
                              </div>
                            ) : (
                              <div className="bg-emerald-50 border border-emerald-200 px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full">
                                {msg.quote && (
                                  <div className="mb-3 bg-white/80 border border-emerald-100 rounded-xl p-3 text-xs text-emerald-800">
                                    <div className="font-bold mb-1">引用批注</div>
                                    <div className="opacity-80">{msg.quote.sourceRoleLabel}：</div>
                                    <div className="mt-1 whitespace-pre-wrap">“{msg.quote.text}”</div>
                                  </div>
                                )}
                                {msg.text && (
                                  <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                                )}

                                {/* ====== 完全新增：专门用来渲染结构化案例卡片的区域 ====== */}
                                {/* 如果 msg 里没有 cardData（即规则干预），这里就不会渲染，完美兼容旧版 */}
                                {msg.cardData && (
                                  <div className="mt-4 bg-white border border-emerald-200 rounded-xl overflow-hidden shadow-sm flex flex-col w-full">

                                    {/* 头部：标题与类型 (使用高级渐变色) */}
                                    <div className="bg-gradient-to-r from-emerald-600 to-teal-500 px-4 py-3 flex items-start justify-between gap-4">
                                      <span className="font-bold text-white text-[15px] leading-tight">
                                        {msg.cardData.title}
                                      </span>
                                      <span className="text-[11px] bg-white/20 text-white px-2 py-0.5 rounded flex-shrink-0 border border-white/30 backdrop-blur-sm">
                                        {msg.cardData.card_type || '案例'}
                                      </span>
                                    </div>

                                    {/* 标签栏：行业、阶段、客群 */}
                                    <div className="px-4 py-2.5 bg-emerald-50/50 border-b border-emerald-100 flex flex-wrap gap-2 text-xs">
                                      {msg.cardData.industry && msg.cardData.industry !== '无' && (
                                        <span className="bg-blue-50 text-blue-700 border border-blue-200 px-2 py-1 rounded-md flex items-center gap-1">
                                          🏭 行业: {msg.cardData.industry}
                                        </span>
                                      )}
                                      {msg.cardData.applicable_stages && msg.cardData.applicable_stages !== '无' && (
                                        <span className="bg-amber-50 text-amber-700 border border-amber-200 px-2 py-1 rounded-md flex items-center gap-1">
                                          📈 阶段: {msg.cardData.applicable_stages}
                                        </span>
                                      )}
                                      {msg.cardData.target_customer && msg.cardData.target_customer !== '无' && (
                                        <span className="bg-purple-50 text-purple-700 border border-purple-200 px-2 py-1 rounded-md flex items-center gap-1">
                                          🎯 客群: {msg.cardData.target_customer}
                                        </span>
                                      )}
                                    </div>

                                    {/* 主体内容区 */}
                                    <div className="p-4 space-y-4">

                                      {/* 痛点与解决方案（左右并排对比视图） */}
                                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                        <div className="bg-red-50 p-3 rounded-lg border border-red-100 text-sm">
                                          <div className="font-bold text-red-800 mb-1.5 flex items-center gap-1 border-b border-red-200 pb-1">
                                            🔴 核心痛点
                                          </div>
                                          <div className="text-red-900/80 leading-relaxed text-xs">
                                            {msg.cardData.core_pain_point || msg.cardData.pain_point || '无'}
                                          </div>
                                        </div>

                                        <div className="bg-emerald-50 p-3 rounded-lg border border-emerald-100 text-sm">
                                          <div className="font-bold text-emerald-800 mb-1.5 flex items-center gap-1 border-b border-emerald-200 pb-1">
                                            🟢 解决方案
                                          </div>
                                          <div className="text-emerald-900/80 leading-relaxed text-xs">
                                            {msg.cardData.solution || '无'}
                                          </div>
                                        </div>
                                      </div>

                                      {/* 商业模式（如果有的话） */}
                                      {msg.cardData.business_model && msg.cardData.business_model !== '无' && (
                                        <div className="bg-indigo-50 p-3 rounded-lg border border-indigo-100 text-sm">
                                          <div className="font-bold text-indigo-800 mb-1.5 flex items-center gap-1">
                                            💎 商业模式
                                          </div>
                                          <div className="text-indigo-900/80 leading-relaxed text-xs">
                                            {msg.cardData.business_model}
                                          </div>
                                        </div>
                                      )}

                                      {/* 证据链展示区（引言样式） */}
                                      {msg.cardData.evidence_items && msg.cardData.evidence_items !== '无' && (
                                        <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-sm">
                                          <div className="font-bold text-slate-700 mb-1.5 flex items-center gap-1">
                                            🔎 关键数据与证据
                                          </div>
                                          <div className="text-slate-600 text-xs italic border-l-2 border-slate-300 pl-2 leading-relaxed">
                                            {msg.cardData.evidence_items}
                                          </div>
                                        </div>
                                      )}

                                      {/* 底部关联规则 */}
                                      {msg.cardData.covered_rule_ids && msg.cardData.covered_rule_ids !== '无' && (
                                        <div className="text-[10px] text-slate-400 pt-2 border-t border-slate-100 flex items-center justify-end gap-1">
                                          🏷️ 关联规则: {msg.cardData.covered_rule_ids}
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                )}
                                {/* ========================================================= */}

                                {Array.isArray(msg.attachments) && msg.attachments.length > 0 && (
                                  <div className="mt-3 flex flex-wrap gap-2">
                                    {msg.attachments.map((file, idx) => (
                                      <a
                                        key={idx}
                                        href={buildAttachmentDownloadUrl(file)}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-xs px-2 py-1 rounded-full bg-white border border-emerald-200 text-emerald-700 inline-flex items-center gap-1 hover:bg-emerald-50"
                                      >
                                        <Paperclip size={12} /> {file.name}
                                      </a>
                                    ))}
                                  </div>
                                )}
                              </div>
                            )
                          ) : (
                            <div className={`bg-white border px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full ${msg.teacherHighlight ? 'border-yellow-300 ring-2 ring-yellow-100' : 'border-slate-200'}`}>
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
                    );
                  })

                )}

                <div ref={chatEndRef} />
              </div>
            </div>

            <div className="shrink-0 bg-white border-t border-slate-200 p-4">
              <div className="w-full">
                <div className="flex items-center justify-between mb-3 gap-4 flex-wrap">
                  <div className="flex items-center gap-3 flex-wrap">
                    <div className="flex gap-2 flex-wrap">
                      {modes.map(renderModeButton)}
                    </div>
                    {!hasBoundDocument && (
                      <div className="text-xs text-amber-600 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-full whitespace-nowrap">
                        当前仅学习模式可用
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={bindingFile}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 bg-white hover:border-brand-300 hover:text-brand-600 text-slate-600 text-sm transition-colors disabled:opacity-60 shrink-0 ml-auto"
                  >
                    {bindingFile ? <Loader2 size={16} className="animate-spin" /> : <RefreshCcw size={16} />}
                    更新文档
                  </button>
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
                        : '先用学习模式提问，或点击左侧回形针绑定商业计划书文档...'
                    }
                    className={`flex-1 p-3 bg-transparent resize-none focus:outline-none text-slate-700 text-sm transition-all duration-200 ${isInputExpanded ? 'h-64' : 'max-h-40'}`}
                    rows={isInputExpanded ? 10 : 1}
                    style={{ minHeight: '52px' }}
                  />

                  <div className="flex items-center p-2 gap-1">
                    <button
                      onClick={() => setIsInputExpanded(!isInputExpanded)}
                      className="p-2 text-slate-400 hover:text-brand-600 hover:bg-slate-100 rounded-lg transition-colors"
                      title={isInputExpanded ? '收起输入框' : '展开输入框 (支持大篇幅长文本)'}
                    >
                      {isInputExpanded ? <Minimize size={18} /> : <Maximize size={18} />}
                    </button>
                    <button
                      onClick={() => handleSubmit()}
                      disabled={loadingReply || !input.trim()}
                      className="p-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 disabled:hover:bg-brand-600 transition-colors"
                    >
                      {loadingReply ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                    </button>
                  </div>
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



