// import React, { useEffect, useMemo, useState } from 'react';
// import {
//   Search, Loader2, FileCheck, Send, Quote, Highlighter, CheckCircle2, Paperclip
// } from 'lucide-react';
// import {
//   fetchTeacherConversationDetail,
//   fetchTeacherProjectConversations,
//   runAgent,
//   syncConversationState,
// } from '../api';
// import StructuredResponseRenderer from './chat/StructuredResponseRenderer';

// function safeParseJSON(raw, fallback) {
//   if (!raw) return fallback;
//   if (typeof raw === 'object') return raw;
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

// function extractCandidateQuotesFromConversation(messages = []) {
//   const quotes = [];
//   messages.forEach((msg) => {
//     if (msg.role !== 'user') return;
//     const text = (msg.text || '').trim();
//     if (!text) return;
//     text
//       .split(/[\n。；!?？]/)
//       .map((item) => item.trim().replace(/^["“”]+|["“”]+$/g, ''))
//       .filter((item) => item.length >= 10 && item.length <= 80)
//       .forEach((item) => {
//         if (!quotes.includes(item)) quotes.push(item);
//       });
//   });
//   return quotes.slice(0, 8);
// }

// function normalizeAssessmentResult(rawContent, messages = []) {
//   const content = rawContent || {};
//   const fallbackQuotes = extractCandidateQuotesFromConversation(messages);
//   let quoteCursor = 0;

//   const rubricTable = (content.rubric_table || []).map((row) => {
//     const nextRow = { ...row };
//     if (!nextRow.reason) {
//       nextRow.reason = '请结合证据链进行教师复核。';
//     }
//     let evidenceQuotes = Array.isArray(nextRow.evidence_quotes) ? [...nextRow.evidence_quotes] : [];
//     evidenceQuotes = evidenceQuotes.filter(Boolean).map((item) => String(item).trim());

//     while (evidenceQuotes.length < 2 && quoteCursor < fallbackQuotes.length) {
//       const candidate = fallbackQuotes[quoteCursor++];
//       if (!evidenceQuotes.includes(candidate)) evidenceQuotes.push(candidate);
//     }

//     nextRow.evidence_quotes = evidenceQuotes.slice(0, 3);

//     if (!nextRow.evidence_trace) {
//       nextRow.evidence_trace =
//         nextRow.evidence_quotes.length > 0
//           ? nextRow.evidence_quotes.map((item) => `“${item}”`).join('；')
//           : '请结合学生原文进一步核证。';
//     }
//     return nextRow;
//   });

//   return {
//     rubric_table: rubricTable,
//     revision_suggestions:
//       content.revision_suggestions || '请优先补齐高权重维度的证据链，再对照 Rubric 逐项修订。',
//     feedback_templates:
//       content.feedback_templates || '建议先补齐证据，再重写关键段落，不要直接推倒重来。',
//     instructor_review_notes:
//       content.instructor_review_notes || '建议教师重点核查系统证据链是否准确，并给出下一轮修订重点。',
//   };
// }

// function getMessagePreview(msg) {
//   if (!msg) return '暂无内容';
//   if (msg.text) return msg.text;
//   if (msg.content?.reply) return msg.content.reply;
//   return '暂无内容';
// }

// export default function ProjectAssessmentView({ currentUser }) {
//   const [items, setItems] = useState([]);
//   const [loadingList, setLoadingList] = useState(true);
//   const [search, setSearch] = useState('');

//   const [activeId, setActiveId] = useState('');
//   const [detail, setDetail] = useState(null);
//   const [loadingDetail, setLoadingDetail] = useState(false);

//   const [loadingAssessment, setLoadingAssessment] = useState(false);
//   const [sendingReview, setSendingReview] = useState(false);
//   const [assessmentResult, setAssessmentResult] = useState(null);
//   const [editedScores, setEditedScores] = useState({});
//   const [reviewNotes, setReviewNotes] = useState('');
//   const [quoteTarget, setQuoteTarget] = useState(null);
//   const [teacherReply, setTeacherReply] = useState('');
//   const [attachmentFiles, setAttachmentFiles] = useState([]);
//   const [sent, setSent] = useState(false);

//   const parsedMessages = useMemo(
//     () => safeParseJSON(detail?.chat_history, []),
//     [detail?.chat_history]
//   );
//   const parsedSnapshot = useMemo(
//     () => safeParseJSON(detail?.analysis_snapshot, {}),
//     [detail?.analysis_snapshot]
//   );

//   useEffect(() => {
//     async function loadList() {
//       if (!currentUser?.id) return;
//       setLoadingList(true);
//       try {
//         const data = await fetchTeacherProjectConversations(currentUser.id, search);
//         setItems(data || []);
//         if (!activeId && data?.length) {
//           setActiveId(data[0].id);
//         }
//       } catch (error) {
//         console.error('教师项目会话列表加载失败', error);
//       } finally {
//         setLoadingList(false);
//       }
//     }
//     loadList();
//   }, [currentUser?.id, search]);

//   useEffect(() => {
//     async function loadDetail() {
//       if (!activeId || !currentUser?.id) return;
//       setLoadingDetail(true);
//       try {
//         const data = await fetchTeacherConversationDetail(activeId, currentUser.id);
//         setDetail(data);

//         const snapshot = safeParseJSON(data.analysis_snapshot, {});
//         const review = snapshot.assessment_review || null;
//         if (review) {
//           setAssessmentResult(review);
//           const scoreMap = {};
//           (review.rubric_table || []).forEach((item, idx) => {
//             scoreMap[idx] = item.teacher_score ?? item.score ?? 0;
//           });
//           setEditedScores(scoreMap);
//           setReviewNotes(review.instructor_review_notes || '');
//         } else {
//           setAssessmentResult(null);
//           setEditedScores({});
//           setReviewNotes('');
//         }

//         setQuoteTarget(null);
//         setTeacherReply('');
//         setAttachmentFiles([]);
//         setSent(false);
//       } catch (error) {
//         console.error('教师项目会话详情加载失败', error);
//       } finally {
//         setLoadingDetail(false);
//       }
//     }
//     loadDetail();
//   }, [activeId, currentUser?.id]);

//   const persistFullConversation = async (nextMessages, nextSnapshot) => {
//     if (!detail?.id) return;
//     const updated = await syncConversationState(
//       detail.id,
//       nextMessages,
//       nextSnapshot,
//       detail.title,
//       detail.last_mode || 'project'
//     );

//     setDetail((prev) => ({
//       ...prev,
//       chat_history: updated.chat_history,
//       analysis_snapshot: updated.analysis_snapshot,
//       title: updated.title,
//       last_mode: updated.last_mode,
//       updated_at: updated.updated_at,
//     }));
//   };

//   const handleGenerateAssessment = async () => {
//     if (!detail?.id) return;
//     setLoadingAssessment(true);
//     setSent(false);

//     try {
//       const prompt = [
//         '请基于当前绑定商业计划书与本会话历史，为该项目生成一份形成性评价。',
//         '必须包含：Rubric Table、Evidence Trace、Revision Suggestions、Instructor Review Notes。',
//         '请优先关注：问题定义、用户证据、方案可行性、商业模式、市场与竞争、团队执行。',
//       ].join('\n');

//       const data = await runAgent(
//         prompt,
//         'assessment',
//         `teacher_assessment_${detail.id}_${Date.now()}`,
//         [],
//         detail.id
//       );

//       const normalized = normalizeAssessmentResult(data.generated_content, parsedMessages);

//       const scoreMap = {};
//       normalized.rubric_table.forEach((item, idx) => {
//         scoreMap[idx] = item.score ?? 0;
//       });

//       setAssessmentResult(normalized);
//       setEditedScores(scoreMap);
//       setReviewNotes(normalized.instructor_review_notes || '');

//       const nextSnapshot = {
//         ...parsedSnapshot,
//         assessment_review: {
//           ...normalized,
//           status: 'draft',
//           sent_at: null,
//           sent_by: null,
//           generated_at: new Date().toISOString(),
//         },
//       };

//       await persistFullConversation(parsedMessages, nextSnapshot);
//     } catch (error) {
//       alert(error?.response?.data?.detail || error.message || '获取评价失败，请检查后端状态。');
//     } finally {
//       setLoadingAssessment(false);
//     }
//   };

//   const handleScoreChange = (index, value) => {
//     setEditedScores((prev) => ({ ...prev, [index]: Number(value) }));
//   };

//   const toggleHighlightMessage = async (messageId) => {
//     const nextMessages = parsedMessages.map((msg) =>
//       msg.id === messageId ? { ...msg, teacherHighlight: !msg.teacherHighlight } : msg
//     );
//     await persistFullConversation(nextMessages, parsedSnapshot);
//   };

//   const handleSendReview = async () => {
//     if (!detail?.id || !assessmentResult) return;

//     setSendingReview(true);
//     try {
//       const rubricTable = (assessmentResult.rubric_table || []).map((row, idx) => ({
//         ...row,
//         teacher_score: editedScores[idx] ?? row.score ?? 0,
//       }));

//       const teacherMessage = {
//         id: `teacher-${Date.now()}`,
//         role: 'teacher',
//         mode: 'teacher_review',
//         text: teacherReply || '老师已下发本轮复核意见，请查看右侧 Rubric 与修订建议。',
//         quote: quoteTarget
//           ? {
//               messageId: quoteTarget.id,
//               text: quoteTarget.text,
//               sourceRole: quoteTarget.role,
//               sourceRoleLabel:
//                 quoteTarget.role === 'user'
//                   ? '学生'
//                   : quoteTarget.role === 'assistant'
//                     ? 'AI'
//                     : '老师',
//             }
//           : null,
//         attachments: attachmentFiles.map((file) => ({
//           name: file.name,
//           size: file.size,
//           type: file.type,
//         })),
//         unreadByStudent: true,
//         createdAt: new Date().toISOString(),
//       };

//       const nextMessages = [...parsedMessages, teacherMessage];
//       const nextSnapshot = {
//         ...parsedSnapshot,
//         assessment_review: {
//           ...assessmentResult,
//           rubric_table: rubricTable,
//           instructor_review_notes: reviewNotes || assessmentResult.instructor_review_notes,
//           status: 'sent',
//           sent_at: new Date().toISOString(),
//           sent_by: currentUser?.id || '',
//           teacher_reply_text: teacherReply || '',
//         },
//       };

//       await persistFullConversation(nextMessages, nextSnapshot);
//       setSent(true);
//       setQuoteTarget(null);
//       setTeacherReply('');
//       setAttachmentFiles([]);
//     } catch (error) {
//       alert(error?.response?.data?.detail || error.message || '下发教师复核失败');
//     } finally {
//       setSendingReview(false);
//     }
//   };

//   const activeHeader = (
//     <div className="flex items-center justify-between gap-4">
//       <div>
//         <div className="text-base font-bold text-slate-800">
//           {detail?.bound_file_name || detail?.title || '未命名项目'}
//         </div>
//         <div className="text-xs text-slate-500 mt-1">
//           {detail?.student_name || '未知学生'} · {detail?.class_name || '未分班'} · 绑定时间 {formatDateTime(detail?.bound_file_uploaded_at)}
//         </div>
//       </div>
//       <button
//         onClick={handleGenerateAssessment}
//         disabled={!detail?.id || loadingAssessment}
//         className="bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-slate-900 disabled:opacity-50 flex items-center gap-2"
//       >
//         {loadingAssessment && <Loader2 size={16} className="animate-spin" />}
//         AI 生成预评估报告
//       </button>
//     </div>
//   );

//   return (
//     <div className="flex-1 min-h-0 flex overflow-hidden">
//       <div className="w-80 shrink-0 border-r border-slate-200 bg-white flex flex-col">
//         <div className="p-5 border-b border-slate-200">
//           <h1 className="text-xl font-bold text-slate-800">📝 单项目复核与批改</h1>
//           <p className="text-slate-500 mt-1 text-sm">
//             以已绑定文档的会话为单位进行搜索、复核、批注与下发
//           </p>

//           <div className="mt-4 relative">
//             <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
//             <input
//               value={search}
//               onChange={(e) => setSearch(e.target.value)}
//               placeholder="检索项目名称 / 学生名称 / 文档名"
//               className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-300 text-sm outline-none focus:ring-2 focus:ring-brand-500"
//             />
//           </div>
//         </div>

//         <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-2">
//           {loadingList ? (
//             <div className="flex items-center gap-2 text-sm text-slate-500 p-3">
//               <Loader2 size={16} className="animate-spin" />
//               正在加载项目会话...
//             </div>
//           ) : items.length === 0 ? (
//             <div className="text-sm text-slate-400 p-4 text-center">暂无可复核项目</div>
//           ) : (
//             items.map((item) => {
//               const reviewStatus = safeParseJSON(item.analysis_snapshot, {}).assessment_review?.status;
//               return (
//                 <button
//                   key={item.id}
//                   onClick={() => setActiveId(item.id)}
//                   className={`w-full text-left border rounded-2xl p-4 transition-all ${
//                     activeId === item.id
//                       ? 'border-brand-300 bg-brand-50'
//                       : 'border-slate-200 bg-white hover:border-brand-200'
//                   }`}
//                 >
//                   <div className="flex items-start justify-between gap-2">
//                     <div className="font-bold text-slate-800 text-sm leading-relaxed line-clamp-2">
//                       {item.bound_file_name || item.title}
//                     </div>
//                     {reviewStatus === 'sent' && (
//                       <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
//                         已下发
//                       </span>
//                     )}
//                   </div>
//                   <div className="text-xs text-slate-500 mt-2">
//                     {item.student_name} · {item.class_name}
//                   </div>
//                   <div className="text-xs text-slate-400 mt-1">
//                     {formatDateTime(item.bound_file_uploaded_at)}
//                   </div>
//                   <div className="text-xs text-slate-500 mt-2 line-clamp-2">
//                     {getMessagePreview(safeParseJSON(item.chat_history, []).slice(-1)[0])}
//                   </div>
//                 </button>
//               );
//             })
//           )}
//         </div>
//       </div>

//       <div className="flex-1 min-h-0 flex flex-col bg-slate-50">
//         <div className="p-5 border-b border-slate-200 bg-white">
//           {detail ? activeHeader : <div className="text-slate-400 text-sm">请先从左侧选择一个项目会话</div>}
//         </div>

//         <div className="flex-1 min-h-0 flex">
//           <div className="flex-1 min-h-0 flex flex-col border-r border-slate-200 bg-slate-50/30">
//             <div className="flex-1 min-h-0 overflow-y-auto p-5 space-y-6">
//               {loadingDetail ? (
//                 <div className="flex items-center gap-2 text-sm text-slate-500">
//                   <Loader2 size={16} className="animate-spin" />
//                   正在加载会话详情...
//                 </div>
//               ) : !detail ? (
//                 <div className="text-sm text-slate-400">请选择项目会话</div>
//               ) : parsedMessages.length === 0 ? (
//                 <div className="text-sm text-slate-400">该会话暂无消息</div>
//               ) : (
//                 parsedMessages.map((msg, idx) => {
//                   const isUser = msg.role === 'user';
//                   const isTeacher = msg.role === 'teacher';

//                   return (
//                     <div key={msg.id || idx} className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
//                       <div
//                         className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${
//                           isUser
//                             ? 'bg-brand-100 text-brand-600'
//                             : isTeacher
//                               ? 'bg-emerald-100 text-emerald-700'
//                               : 'bg-slate-800 text-white'
//                         }`}
//                       >
//                         {isUser ? '学' : isTeacher ? '师' : 'AI'}
//                       </div>

//                       <div className={`flex flex-col gap-2 max-w-[86%] ${isUser ? 'items-end' : 'items-start'}`}>
//                         {!isTeacher && (
//                           <div className="flex gap-2">
//                             <button
//                               onClick={() =>
//                                 setQuoteTarget({
//                                   id: msg.id,
//                                   role: msg.role,
//                                   text: msg.text || msg.content?.reply || JSON.stringify(msg.content || {}),
//                                 })
//                               }
//                               className="text-xs px-2 py-1 rounded-full border border-slate-200 bg-white text-slate-600 hover:border-brand-300 hover:text-brand-600 flex items-center gap-1"
//                             >
//                               <Quote size={12} /> 引用批复
//                             </button>
//                             <button
//                               onClick={() => toggleHighlightMessage(msg.id)}
//                               className={`text-xs px-2 py-1 rounded-full border flex items-center gap-1 ${
//                                 msg.teacherHighlight
//                                   ? 'border-yellow-300 bg-yellow-100 text-yellow-700'
//                                   : 'border-slate-200 bg-white text-slate-600 hover:border-yellow-300 hover:text-yellow-700'
//                               }`}
//                             >
//                               <Highlighter size={12} /> 标记重点
//                             </button>
//                           </div>
//                         )}

//                         {isUser ? (
//                           <div className={`px-5 py-3 rounded-2xl rounded-tr-sm shadow-sm whitespace-pre-wrap ${msg.teacherHighlight ? 'bg-yellow-100 text-slate-800 ring-2 ring-yellow-300' : 'bg-brand-600 text-white'}`}>
//                             {msg.text}
//                           </div>
//                         ) : isTeacher ? (
//                           <div className="bg-emerald-50 border border-emerald-200 px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full">
//                             {msg.quote && (
//                               <div className="mb-3 bg-white/80 border border-emerald-100 rounded-xl p-3 text-xs text-emerald-800">
//                                 <div className="font-bold mb-1">引用批注</div>
//                                 <div className="opacity-80">{msg.quote.sourceRoleLabel}：</div>
//                                 <div className="mt-1 whitespace-pre-wrap">“{msg.quote.text}”</div>
//                               </div>
//                             )}
//                             <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">{msg.text}</p>
//                             {Array.isArray(msg.attachments) && msg.attachments.length > 0 && (
//                               <div className="mt-3 flex flex-wrap gap-2">
//                                 {msg.attachments.map((file, fileIdx) => (
//                                   <span key={fileIdx} className="text-xs px-2 py-1 rounded-full bg-white border border-emerald-200 text-emerald-700">
//                                     附件：{file.name}
//                                   </span>
//                                 ))}
//                               </div>
//                             )}
//                           </div>
//                         ) : (
//                           <div className={`bg-white border px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full ${msg.teacherHighlight ? 'border-yellow-300 ring-2 ring-yellow-100' : 'border-slate-200'}`}>
//                             {msg.mode && msg.content ? (
//                               <StructuredResponseRenderer mode={msg.mode} content={msg.content} />
//                             ) : (
//                               <p className="text-slate-700 whitespace-pre-wrap">{msg.text}</p>
//                             )}
//                           </div>
//                         )}
//                       </div>
//                     </div>
//                   );
//                 })
//               )}
//             </div>

//             {detail && (
//               <div className="border-t border-slate-200 bg-white p-4">
//                 {quoteTarget && (
//                   <div className="mb-3 bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-600">
//                     <div className="flex items-center justify-between gap-3">
//                       <div className="font-bold">当前引用</div>
//                       <button className="text-slate-400 hover:text-slate-700" onClick={() => setQuoteTarget(null)}>
//                         清除
//                       </button>
//                     </div>
//                     <div className="mt-2 whitespace-pre-wrap line-clamp-3">{quoteTarget.text}</div>
//                   </div>
//                 )}

//                 <textarea
//                   value={teacherReply}
//                   onChange={(e) => setTeacherReply(e.target.value)}
//                   placeholder="输入教师批复，可引用上方任意一条消息。"
//                   className="w-full border border-slate-300 rounded-xl p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-500"
//                   rows={3}
//                 />

//                 <div className="mt-3 flex items-center justify-between gap-4 flex-wrap">
//                   <label className="text-sm text-slate-600 flex items-center gap-2 cursor-pointer">
//                     <Paperclip size={16} />
//                     附带附件（仅记录附件名）
//                     <input
//                       type="file"
//                       multiple
//                       className="hidden"
//                       onChange={(e) => setAttachmentFiles(Array.from(e.target.files || []))}
//                     />
//                   </label>

//                   <button
//                     onClick={handleSendReview}
//                     disabled={!assessmentResult || sendingReview || (!teacherReply.trim() && !quoteTarget)}
//                     className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 disabled:opacity-50"
//                   >
//                     {sendingReview ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
//                     下发教师复核
//                   </button>
//                 </div>

//                 {attachmentFiles.length > 0 && (
//                   <div className="mt-2 flex flex-wrap gap-2">
//                     {attachmentFiles.map((file, idx) => (
//                       <span key={idx} className="text-xs px-2 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
//                         {file.name}
//                       </span>
//                     ))}
//                   </div>
//                 )}

//                 {sent && (
//                   <div className="mt-3 text-sm text-emerald-700 flex items-center gap-2">
//                     <CheckCircle2 size={16} /> 已成功写入会话，学生端会显示新消息提醒
//                   </div>
//                 )}
//               </div>
//             )}
//           </div>

//           <div className="w-[420px] shrink-0 bg-white flex flex-col">
//             <div className="p-5 border-b border-slate-200">
//               <h3 className="font-bold text-slate-800 flex items-center gap-2">
//                 <FileCheck size={18} /> 教师批改面板
//               </h3>
//               <p className="text-xs text-slate-500 mt-1">
//                 Rubric / Evidence Trace / Revision Suggestions / Instructor Review Notes
//               </p>
//             </div>

//             <div className="flex-1 min-h-0 overflow-y-auto p-5 space-y-5">
//               {!assessmentResult ? (
//                 <div className="text-sm text-slate-400">请先点击上方按钮生成 AI 预评估报告</div>
//               ) : (
//                 <>
//                   <div className="border border-slate-200 rounded-2xl overflow-hidden">
//                     <div className="px-4 py-3 bg-slate-50 border-b border-slate-200 font-bold text-slate-800 text-sm">
//                       Rubric Table
//                     </div>
//                     <div className="divide-y divide-slate-100">
//                       {(assessmentResult.rubric_table || []).map((row, idx) => (
//                         <div key={idx} className="p-4 space-y-3">
//                           <div className="flex items-start justify-between gap-3">
//                             <div className="font-semibold text-slate-800 text-sm">{row.dimension}</div>
//                             <select
//                               value={editedScores[idx] ?? row.score ?? 0}
//                               onChange={(e) => handleScoreChange(idx, e.target.value)}
//                               className="border border-slate-300 rounded-lg px-2 py-1 text-sm outline-none focus:ring-2 focus:ring-brand-500"
//                             >
//                               {[0, 1, 2, 3, 4, 5].map((score) => (
//                                 <option key={score} value={score}>{score} 分</option>
//                               ))}
//                             </select>
//                           </div>

//                           {row.reason && (
//                             <div className="text-xs text-slate-600 bg-slate-50 border border-slate-200 rounded-lg p-3">
//                               <strong>评分理由：</strong>{row.reason}
//                             </div>
//                           )}

//                           <div className="text-xs text-slate-500 bg-blue-50 border border-blue-100 rounded-lg p-3 leading-relaxed">
//                             <strong>Evidence Trace：</strong> {row.evidence_trace}
//                           </div>

//                           {Array.isArray(row.evidence_quotes) && row.evidence_quotes.length > 0 && (
//                             <div className="space-y-2">
//                               {row.evidence_quotes.map((quote, quoteIdx) => (
//                                 <div key={quoteIdx} className="text-xs text-slate-600 border-l-4 border-brand-300 pl-3 py-1 bg-slate-50 rounded-r-lg">
//                                   “{quote}”
//                                 </div>
//                               ))}
//                             </div>
//                           )}
//                         </div>
//                       ))}
//                     </div>
//                   </div>

//                   <div className="bg-blue-50 border border-blue-100 rounded-2xl p-4">
//                     <div className="font-bold text-blue-800 text-sm mb-2">Revision Suggestions</div>
//                     <div className="text-sm text-blue-700 whitespace-pre-wrap leading-relaxed">
//                       {assessmentResult.revision_suggestions}
//                     </div>
//                   </div>

//                   <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4">
//                     <div className="font-bold text-slate-800 text-sm mb-2">系统生成的 Instructor Review Notes 草案</div>
//                     <div className="text-sm text-slate-600 whitespace-pre-wrap leading-relaxed">
//                       {assessmentResult.instructor_review_notes}
//                     </div>
//                   </div>

//                   <div>
//                     <div className="font-bold text-slate-800 text-sm mb-2">教师复核备注</div>
//                     <textarea
//                       value={reviewNotes}
//                       onChange={(e) => setReviewNotes(e.target.value)}
//                       rows={5}
//                       className="w-full border border-slate-300 rounded-xl p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-500"
//                       placeholder="在此填写最终 Instructor Review Notes ..."
//                     />
//                   </div>
//                 </>
//               )}
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }
import React, { useEffect, useMemo, useState } from 'react';
import {
  Search, Loader2, Send, Quote, Highlighter, CheckCircle2, Paperclip,
  ChevronLeft, ChevronRight, MessageSquareText, ClipboardCheck, Download, Sparkles,
  FileText, ChevronDown, ChevronUp,
} from 'lucide-react';
import {
  API_BASE_URL,
  fetchTeacherConversationDetail,
  fetchTeacherProjectConversations,
  runAgent,
  syncConversationState,
  uploadConversationAttachment,
} from '../api';
import StructuredResponseRenderer from './chat/StructuredResponseRenderer';
import SnapshotOverlay from './chat/SnapshotOverlay';

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

function extractCandidateQuotesFromConversation(messages = []) {
  const quotes = [];
  messages.forEach((msg) => {
    if (msg.role !== 'user') return;
    const text = (msg.text || '').trim();
    if (!text) return;
    text
      .split(/[\n。；!?？]/)
      .map((item) => item.trim().replace(/^["“”]+|["“”]+$/g, ''))
      .filter((item) => item.length >= 10 && item.length <= 80)
      .forEach((item) => {
        if (!quotes.includes(item)) quotes.push(item);
      });
  });
  return quotes.slice(0, 8);
}

function normalizeAssessmentResult(rawContent, messages = []) {
  const content = rawContent || {};
  const fallbackQuotes = extractCandidateQuotesFromConversation(messages);
  let quoteCursor = 0;

  const rubricTable = (content.rubric_table || []).map((row) => {
    const nextRow = { ...row };
    if (!nextRow.reason) {
      nextRow.reason = '请结合证据链进行教师复核。';
    }
    let evidenceQuotes = Array.isArray(nextRow.evidence_quotes) ? [...nextRow.evidence_quotes] : [];
    evidenceQuotes = evidenceQuotes.filter(Boolean).map((item) => String(item).trim());

    while (evidenceQuotes.length < 2 && quoteCursor < fallbackQuotes.length) {
      const candidate = fallbackQuotes[quoteCursor++];
      if (!evidenceQuotes.includes(candidate)) evidenceQuotes.push(candidate);
    }

    nextRow.evidence_quotes = evidenceQuotes.slice(0, 3);

    if (!nextRow.evidence_trace) {
      nextRow.evidence_trace =
        nextRow.evidence_quotes.length > 0
          ? nextRow.evidence_quotes.map((item) => `“${item}”`).join('；')
          : '请结合学生原文进一步核证。';
    }
    return nextRow;
  });

  return {
    rubric_table: rubricTable,
    revision_suggestions:
      content.revision_suggestions || '请优先补齐高权重维度的证据链，再对照 Rubric 逐项修订。',
    feedback_templates:
      content.feedback_templates || '建议先补齐证据，再重写关键段落，不要直接推倒重来。',
    instructor_review_notes:
      content.instructor_review_notes || '建议教师重点核查系统证据链是否准确，并给出下一轮修订重点。',
  };
}

function getMessagePreview(msg) {
  if (!msg) return '暂无内容';
  if (msg.kind === 'assessment_report') return '老师下发了评估复核报告';
  if (msg.text) return msg.text;
  if (msg.content?.reply) return msg.content.reply;
  return '暂无内容';
}

function buildDownloadUrl(file) {
  if (!file) return '#';
  if (file.download_url?.startsWith('http')) return file.download_url;
  return `${API_BASE_URL.replace(/\/api\/v1$/, '')}${file.download_url || ''}`;
}

function TeacherAssessmentCard({ report, coverNote = '', compact = false }) {
  if (!report) return null;
  const items = report.rubric_table || [];
  return (
    <div className="rounded-2xl border border-emerald-200 bg-white overflow-hidden shadow-sm w-full">
      <div className="px-4 py-3 bg-emerald-50 border-b border-emerald-100 flex items-center gap-2 text-emerald-800 font-bold text-sm">
        <ClipboardCheck size={16} /> 教师复核评估报告
      </div>
      <div className="p-4 space-y-4">
        {coverNote ? (
          <div className="rounded-xl bg-slate-50 border border-slate-200 p-3 text-sm text-slate-700 whitespace-pre-wrap">
            {coverNote}
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
                {!compact && row.evidence_trace ? (
                  <div className="text-xs text-slate-600 bg-blue-50 border border-blue-100 rounded-lg p-3 leading-relaxed">
                    <strong>Evidence Trace：</strong> {row.evidence_trace}
                  </div>
                ) : null}
                {!compact && Array.isArray(row.evidence_quotes) && row.evidence_quotes.length > 0 ? (
                  <div className="space-y-2">
                    {row.evidence_quotes.slice(0, 2).map((quote, quoteIdx) => (
                      <div key={quoteIdx} className="text-xs text-slate-600 border-l-4 border-brand-300 pl-3 py-1 bg-slate-50 rounded-r-lg">
                        “{quote}”
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        </div>
        {!compact ? (
          <>
            <div className="rounded-xl bg-blue-50 border border-blue-100 p-3">
              <div className="font-bold text-blue-800 text-sm mb-2">Revision Suggestions</div>
              <div className="text-sm text-blue-700 whitespace-pre-wrap leading-relaxed">{report.revision_suggestions}</div>
            </div>
            <div className="rounded-xl bg-slate-50 border border-slate-200 p-3">
              <div className="font-bold text-slate-800 text-sm mb-2">Instructor Review Notes</div>
              <div className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{report.instructor_review_notes}</div>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

function AttachmentList({ attachments = [] }) {
  if (!attachments.length) return null;
  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {attachments.map((file, idx) => (
        <a
          key={idx}
          href={buildDownloadUrl(file)}
          target="_blank"
          rel="noreferrer"
          className="text-xs px-2 py-1 rounded-full bg-white border border-emerald-200 text-emerald-700 inline-flex items-center gap-1 hover:bg-emerald-50"
        >
          <Download size={12} /> {file.name}
        </a>
      ))}
    </div>
  );
}

function ReportSection({ title, open, onToggle, children, badge = null }) {
  return (
    <div className="border border-slate-200 rounded-2xl overflow-hidden bg-white">
      <button
        type="button"
        onClick={onToggle}
        className="w-full px-4 py-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between gap-3 text-left"
      >
        <div className="font-bold text-slate-800 text-sm">{title}</div>
        <div className="flex items-center gap-2">
          {badge}
          {open ? <ChevronRight size={16} className="rotate-90 text-slate-500" /> : <ChevronRight size={16} className="text-slate-500" />}
        </div>
      </button>
      {open ? <div className="p-4 space-y-4">{children}</div> : null}
    </div>
  );
}

export default function ProjectAssessmentView({ currentUser }) {
  const [items, setItems] = useState([]);
  const [loadingList, setLoadingList] = useState(true);
  const [search, setSearch] = useState('');

  const [activeId, setActiveId] = useState('');
  const [detail, setDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const [loadingAssessment, setLoadingAssessment] = useState(false);
  const [sendingReply, setSendingReply] = useState(false);
  const [sendingAssessment, setSendingAssessment] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState(null);
  const [editedScores, setEditedScores] = useState({});
  const [reviewNotes, setReviewNotes] = useState('');
  const [quoteTarget, setQuoteTarget] = useState(null);
  const [teacherReply, setTeacherReply] = useState('');
  const [attachmentFiles, setAttachmentFiles] = useState([]);
  const [replySent, setReplySent] = useState(false);
  const [assessmentSent, setAssessmentSent] = useState(false);
  const [reportPanelOpen, setReportPanelOpen] = useState(false);
  const [teacherSnapshotOpen, setTeacherSnapshotOpen] = useState(false);
  const [openSections, setOpenSections] = useState({ rubric: true, suggestions: true, notes: true });

  const parsedMessages = useMemo(
    () => safeParseJSON(detail?.chat_history, []),
    [detail?.chat_history]
  );
  const parsedSnapshot = useMemo(
    () => safeParseJSON(detail?.analysis_snapshot, {}),
    [detail?.analysis_snapshot]
  );

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
        console.error('教师项目会话列表加载失败', error);
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

        const snapshot = safeParseJSON(data.analysis_snapshot, {});
        const review = snapshot.assessment_review || null;
        if (review) {
          setAssessmentResult(review);
          const scoreMap = {};
          (review.rubric_table || []).forEach((item, idx) => {
            scoreMap[idx] = item.teacher_score ?? item.score ?? 0;
          });
          setEditedScores(scoreMap);
          setReviewNotes(review.instructor_review_notes || '');
        } else {
          setAssessmentResult(null);
          setEditedScores({});
          setReviewNotes('');
        }

        setQuoteTarget(null);
        setTeacherReply('');
        setAttachmentFiles([]);
        setReplySent(false);
        setAssessmentSent(false);
        setTeacherSnapshotOpen(false);
        setReportPanelOpen(false);
      } catch (error) {
        console.error('教师项目会话详情加载失败', error);
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

  const uploadSelectedAttachments = async () => {
    if (!attachmentFiles.length) return [];
    return Promise.all(attachmentFiles.map((file) => uploadConversationAttachment(file)));
  };

  const handleGenerateAssessment = async () => {
    if (!detail?.id) return;
    setLoadingAssessment(true);
    setAssessmentSent(false);

    try {
      const prompt = [
        '请基于当前绑定商业计划书与本会话历史，为该项目生成一份形成性评价。',
        '必须包含：Rubric Table、Evidence Trace、Revision Suggestions、Instructor Review Notes。',
        '请优先关注：问题定义、用户证据、方案可行性、商业模式、市场与竞争、团队执行。',
      ].join('\n');

      const data = await runAgent(
        prompt,
        'assessment',
        `teacher_assessment_${detail.id}_${Date.now()}`,
        [],
        detail.id
      );

      const normalized = normalizeAssessmentResult(data.generated_content, parsedMessages);

      const scoreMap = {};
      normalized.rubric_table.forEach((item, idx) => {
        scoreMap[idx] = item.score ?? 0;
      });

      setAssessmentResult(normalized);
      setEditedScores(scoreMap);
      setReviewNotes(normalized.instructor_review_notes || '');
      setReportPanelOpen(true);
      setOpenSections({ rubric: true, suggestions: true, notes: true });

      const nextSnapshot = {
        ...parsedSnapshot,
        assessment_review: {
          ...normalized,
          status: 'draft',
          sent_at: null,
          sent_by: null,
          generated_at: new Date().toISOString(),
        },
      };

      await persistFullConversation(parsedMessages, nextSnapshot);
    } catch (error) {
      alert(error?.response?.data?.detail || error.message || '获取评价失败，请检查后端状态。');
    } finally {
      setLoadingAssessment(false);
    }
  };

  const handleScoreChange = (index, value) => {
    setEditedScores((prev) => ({ ...prev, [index]: Number(value) }));
  };

  const toggleHighlightMessage = async (messageId) => {
    const nextMessages = parsedMessages.map((msg) =>
      msg.id === messageId ? { ...msg, teacherHighlight: !msg.teacherHighlight } : msg
    );
    await persistFullConversation(nextMessages, parsedSnapshot);
  };

  const handleSendReply = async () => {
    if (!detail?.id) return;
    if (!teacherReply.trim() && !quoteTarget && attachmentFiles.length === 0) return;

    setSendingReply(true);
    try {
      const uploadedAttachments = await uploadSelectedAttachments();
      const teacherMessage = {
        id: `teacher-reply-${Date.now()}`,
        role: 'teacher',
        kind: 'reply',
        mode: 'teacher_reply',
        text: teacherReply || '老师补充了一条会话批注，请查看。',
        quote: quoteTarget
          ? {
              messageId: quoteTarget.id,
              text: quoteTarget.text,
              sourceRole: quoteTarget.role,
              sourceRoleLabel:
                quoteTarget.role === 'user'
                  ? '学生'
                  : quoteTarget.role === 'assistant'
                    ? 'AI'
                    : '老师',
            }
          : null,
        attachments: uploadedAttachments,
        unreadByStudent: true,
        createdAt: new Date().toISOString(),
      };

      const nextMessages = [...parsedMessages, teacherMessage];
      await persistFullConversation(nextMessages, parsedSnapshot);
      setReplySent(true);
      setAssessmentSent(false);
      setQuoteTarget(null);
      setTeacherReply('');
      setAttachmentFiles([]);
    } catch (error) {
      alert(error?.response?.data?.detail || error.message || '发送教师回复失败');
    } finally {
      setSendingReply(false);
    }
  };

  const handleSendAssessment = async () => {
    if (!detail?.id || !assessmentResult) return;
    setSendingAssessment(true);
    try {
      const rubricTable = (assessmentResult.rubric_table || []).map((row, idx) => ({
        ...row,
        teacher_score: editedScores[idx] ?? row.score ?? 0,
      }));
      const finalReport = {
        ...assessmentResult,
        rubric_table: rubricTable,
        instructor_review_notes: reviewNotes || assessmentResult.instructor_review_notes,
      };
      const uploadedAttachments = await uploadSelectedAttachments();

      const teacherMessage = {
        id: `teacher-assessment-${Date.now()}`,
        role: 'teacher',
        kind: 'assessment_report',
        mode: 'teacher_review',
        text: teacherReply || '老师已下发本轮项目复核评估报告，请查看并按要求修改。',
        report: finalReport,
        attachments: uploadedAttachments,
        unreadByStudent: true,
        createdAt: new Date().toISOString(),
      };

      const nextMessages = [...parsedMessages, teacherMessage];
      const nextSnapshot = {
        ...parsedSnapshot,
        assessment_review: {
          ...finalReport,
          status: 'sent',
          sent_at: new Date().toISOString(),
          sent_by: currentUser?.id || '',
          teacher_reply_text: teacherReply || '',
          attachments: uploadedAttachments,
        },
      };

      await persistFullConversation(nextMessages, nextSnapshot);
      setAssessmentResult(finalReport);
      setAssessmentSent(true);
      setReplySent(false);
      setTeacherReply('');
      setAttachmentFiles([]);
    } catch (error) {
      alert(error?.response?.data?.detail || error.message || '下发教师复核报告失败');
    } finally {
      setSendingAssessment(false);
    }
  };

  const activeHeader = detail ? (
    <div className="flex min-w-0 items-center justify-between gap-3">
      <div className="min-w-0 flex-1">
        <div className="text-base font-bold text-slate-800 truncate">
          {detail.bound_file_name || detail.title || '未命名项目'}
        </div>
        <div className="text-xs text-slate-500 mt-1 truncate">
          {detail.student_name || '未知学生'} · {detail.class_name || '未分班'} · 绑定时间 {formatDateTime(detail.bound_file_uploaded_at)}
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <button
          onClick={() => setReportPanelOpen((v) => !v)}
          className="border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 p-2 rounded-lg"
          title={reportPanelOpen ? '折叠评估面板' : '展开评估面板'}
        >
          {reportPanelOpen ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
        <button
          onClick={handleGenerateAssessment}
          disabled={!detail?.id || loadingAssessment}
          className="bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-slate-900 disabled:opacity-50 flex items-center gap-2 whitespace-nowrap"
        >
          {loadingAssessment && <Loader2 size={16} className="animate-spin" />}
          AI 生成预评估报告
        </button>
      </div>
    </div>
  ) : (
    <div className="text-slate-400 text-sm">请先从左侧选择一个项目会话</div>
  );

  return (
    <div className="flex-1 min-h-0 flex overflow-hidden bg-slate-50">
      <div className="w-[250px] shrink-0 border-r border-slate-200 bg-white flex flex-col">
        <div className="p-4 border-b border-slate-200">
          <h1 className="text-xl font-bold text-slate-800">📝 单项目复核与批改</h1>
          <p className="text-slate-500 mt-1 text-sm">以已绑定文档的会话为单位进行搜索、复核、批注与下发</p>

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
            <div className="text-sm text-slate-400 p-4 text-center">暂无可复核项目</div>
          ) : (
            items.map((item) => {
              const reviewStatus = safeParseJSON(item.analysis_snapshot, {}).assessment_review?.status;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveId(item.id)}
                  className={`w-full text-left border rounded-2xl p-4 transition-all ${
                    activeId === item.id
                      ? 'border-brand-300 bg-brand-50'
                      : 'border-slate-200 bg-white hover:border-brand-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="font-bold text-slate-800 text-sm leading-relaxed line-clamp-2">
                      {item.bound_file_name || item.title}
                    </div>
                    {reviewStatus === 'sent' && (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
                        已下发
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-500 mt-2">
                    {item.student_name} · {item.class_name}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    {formatDateTime(item.bound_file_uploaded_at)}
                  </div>
                  <div className="text-xs text-slate-500 mt-2 line-clamp-2">
                    {getMessagePreview(safeParseJSON(item.chat_history, []).slice(-1)[0])}
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>

      <div className="flex-1 min-w-0 min-h-0 flex overflow-hidden bg-slate-50">
        <div className="flex-1 min-w-0 min-h-0 flex flex-col bg-white border-r border-slate-200">
          <div className="relative shrink-0 border-b border-slate-200 bg-white">
            <div className="px-4 py-4 border-b border-slate-100">{activeHeader}</div>
            {detail && (
              <div className="px-4 py-2 bg-red-50 border-b border-red-100">
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0 flex items-center gap-2">
                    <FileText size={15} className="text-red-600 shrink-0" />
                    <span className="text-sm text-red-800 truncate font-medium">
                      {detail.bound_file_name || detail.title}
                    </span>
                    <span className="text-xs text-red-500 shrink-0">
                      {formatDateTime(detail.bound_file_uploaded_at)}
                    </span>
                  </div>
                  <button
                    onClick={() => setTeacherSnapshotOpen((v) => !v)}
                    className="shrink-0 inline-flex items-center gap-1 text-xs text-amber-700 bg-white border border-amber-200 rounded-full px-3 py-1 hover:bg-amber-50"
                  >
                    文档分析面板
                    {teacherSnapshotOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>
                </div>
              </div>
            )}
            <SnapshotOverlay open={teacherSnapshotOpen} snapshot={parsedSnapshot} />
          </div>

          <div className="flex-1 min-w-0 min-h-0 overflow-y-auto p-4 space-y-6 bg-slate-50/40">
            {loadingDetail ? (
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Loader2 size={16} className="animate-spin" />
                正在加载会话详情...
              </div>
            ) : !detail ? (
              <div className="text-sm text-slate-400">请选择项目会话</div>
            ) : parsedMessages.length === 0 ? (
              <div className="text-sm text-slate-400">该会话暂无消息</div>
            ) : (
              parsedMessages.map((msg, idx) => {
                const isUser = msg.role === 'user';
                const isTeacher = msg.role === 'teacher';
                const isAssessment = isTeacher && msg.kind === 'assessment_report';

                return (
                  <div key={msg.id || idx} className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${
                        isUser
                          ? 'bg-brand-100 text-brand-600'
                          : isTeacher
                            ? 'bg-emerald-100 text-emerald-700'
                            : 'bg-slate-800 text-white'
                      }`}
                    >
                      {isUser ? '学' : isTeacher ? '师' : 'AI'}
                    </div>

                    <div className={`flex flex-col gap-2 max-w-[88%] ${isUser ? 'items-end' : 'items-start'}`}>
                      {!isTeacher && (
                        <div className="flex gap-2 flex-wrap">
                          <button
                            onClick={() =>
                              setQuoteTarget({
                                id: msg.id,
                                role: msg.role,
                                text: msg.text || msg.content?.reply || JSON.stringify(msg.content || {}),
                              })
                            }
                            className="text-xs px-2 py-1 rounded-full border border-slate-200 bg-white text-slate-600 hover:border-brand-300 hover:text-brand-600 flex items-center gap-1"
                          >
                            <Quote size={12} /> 引用批复
                          </button>
                          <button
                            onClick={() => toggleHighlightMessage(msg.id)}
                            className={`text-xs px-2 py-1 rounded-full border flex items-center gap-1 ${
                              msg.teacherHighlight
                                ? 'border-yellow-300 bg-yellow-100 text-yellow-700'
                                : 'border-slate-200 bg-white text-slate-600 hover:border-yellow-300 hover:text-yellow-700'
                            }`}
                          >
                            <Highlighter size={12} /> 标记重点
                          </button>
                        </div>
                      )}

                      {isUser ? (
                        <div className={`px-5 py-3 rounded-2xl rounded-tr-sm shadow-sm whitespace-pre-wrap ${msg.teacherHighlight ? 'bg-yellow-100 text-slate-800 ring-2 ring-yellow-300' : 'bg-brand-600 text-white'}`}>
                          {msg.text}
                        </div>
                      ) : isTeacher ? (
                        isAssessment ? (
                          <div className="w-full max-w-3xl">
                            <TeacherAssessmentCard report={msg.report} coverNote={msg.text} compact={false} />
                            <AttachmentList attachments={msg.attachments || []} />
                          </div>
                        ) : (
                          <div className="bg-emerald-50 border border-emerald-200 px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full max-w-3xl">
                            {msg.quote && (
                              <div className="mb-3 bg-white/80 border border-emerald-100 rounded-xl p-3 text-xs text-emerald-800">
                                <div className="font-bold mb-1">引用批注</div>
                                <div className="opacity-80">{msg.quote.sourceRoleLabel}：</div>
                                <div className="mt-1 whitespace-pre-wrap">“{msg.quote.text}”</div>
                              </div>
                            )}
                            <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                            <AttachmentList attachments={msg.attachments || []} />
                          </div>
                        )
                      ) : (
                        <div className={`bg-white border px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm w-full max-w-3xl ${msg.teacherHighlight ? 'border-yellow-300 ring-2 ring-yellow-100' : 'border-slate-200'}`}>
                          {msg.mode && msg.content ? (
                            <StructuredResponseRenderer mode={msg.mode} content={msg.content} />
                          ) : (
                            <p className="text-slate-700 whitespace-pre-wrap">{msg.text}</p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {detail && (
            <div className="border-t border-slate-200 bg-white p-4 space-y-4 shrink-0">
              {quoteTarget && (
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-600">
                  <div className="flex items-center justify-between gap-3">
                    <div className="font-bold">当前引用</div>
                    <button className="text-slate-400 hover:text-slate-700" onClick={() => setQuoteTarget(null)}>
                      清除
                    </button>
                  </div>
                  <div className="mt-2 whitespace-pre-wrap line-clamp-3">{quoteTarget.text}</div>
                </div>
              )}

              <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_auto] gap-4 items-start">
                <div className="space-y-3 min-w-0">
                  <textarea
                    value={teacherReply}
                    onChange={(e) => setTeacherReply(e.target.value)}
                    placeholder="输入教师批注 / 引用回复；若要发送评估报告，这里也可作为附带说明。"
                    className="w-full border border-slate-300 rounded-xl p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-500"
                    rows={3}
                  />

                  <div className="flex items-center justify-between gap-4 flex-wrap">
                    <label className="text-sm text-slate-600 flex items-center gap-2 cursor-pointer">
                      <Paperclip size={16} />
                      附带附件（可下载）
                      <input
                        type="file"
                        multiple
                        className="hidden"
                        onChange={(e) => setAttachmentFiles(Array.from(e.target.files || []))}
                      />
                    </label>

                    {attachmentFiles.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {attachmentFiles.map((file, idx) => (
                          <span key={idx} className="text-xs px-2 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                            {file.name}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex flex-col gap-2 min-w-[180px] shrink-0">
                  <button
                    onClick={handleSendReply}
                    disabled={sendingReply || (!teacherReply.trim() && !quoteTarget && attachmentFiles.length === 0)}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {sendingReply ? <Loader2 size={16} className="animate-spin" /> : <MessageSquareText size={16} />}
                    发送引用回复
                  </button>
                  <button
                    onClick={handleSendAssessment}
                    disabled={!assessmentResult || sendingAssessment}
                    className="bg-slate-800 hover:bg-slate-900 text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {sendingAssessment ? <Loader2 size={16} className="animate-spin" /> : <ClipboardCheck size={16} />}
                    发送评估报告
                  </button>
                </div>
              </div>

              {replySent && (
                <div className="text-sm text-emerald-700 flex items-center gap-2">
                  <CheckCircle2 size={16} /> 已成功发送教师引用回复
                </div>
              )}
              {assessmentSent && (
                <div className="text-sm text-emerald-700 flex items-center gap-2">
                  <CheckCircle2 size={16} /> 已成功发送教师评估复核报告
                </div>
              )}
            </div>
          )}
        </div>

        <div
          className={`${reportPanelOpen ? 'w-[360px] basis-[360px]' : 'w-14 basis-14'} shrink-0 min-w-0 min-h-0 overflow-hidden bg-white border-l border-slate-200 transition-all duration-200`}
        >
          {reportPanelOpen ? (
            <>
              <div className="p-4 border-b border-slate-200 flex items-center justify-between gap-2">
                <div className="min-w-0">
                  <h3 className="font-bold text-slate-800 flex items-center gap-2">
                    <Sparkles size={16} /> 教师批改面板
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">可折叠查看 Rubric / Evidence Trace / Suggestions / Notes</p>
                </div>
                <button
                  onClick={() => setReportPanelOpen(false)}
                  className="border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 p-2 rounded-lg shrink-0"
                  title="折叠批改面板"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
              <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-4 bg-slate-50/40">
                {!assessmentResult ? (
                  <div className="text-sm text-slate-400 bg-white border border-slate-200 rounded-2xl p-4">
                    请点击顶部“AI 生成预评估报告”查看详细批改面板。
                  </div>
                ) : (
                  <>
                    <ReportSection
                      title="Rubric Table"
                      open={openSections.rubric}
                      onToggle={() => setOpenSections((prev) => ({ ...prev, rubric: !prev.rubric }))}
                      badge={<span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">{(assessmentResult.rubric_table || []).length} 项</span>}
                    >
                      {(assessmentResult.rubric_table || []).map((row, idx) => (
                        <div key={idx} className="rounded-xl border border-slate-200 p-3 space-y-3">
                          <div className="flex items-center justify-between gap-3">
                            <div className="font-semibold text-slate-800 text-sm">{row.dimension}</div>
                            <select
                              value={editedScores[idx] ?? row.score ?? 0}
                              onChange={(e) => handleScoreChange(idx, e.target.value)}
                              className="border border-slate-300 rounded-lg px-2 py-1 text-sm outline-none focus:ring-2 focus:ring-brand-500"
                            >
                              {[0, 1, 2, 3, 4, 5].map((score) => (
                                <option key={score} value={score}>{score} 分</option>
                              ))}
                            </select>
                          </div>
                          {row.reason && (
                            <div className="text-xs text-slate-600 bg-slate-50 border border-slate-200 rounded-lg p-3">
                              <strong>评分理由：</strong>{row.reason}
                            </div>
                          )}
                          <div className="text-xs text-slate-500 bg-blue-50 border border-blue-100 rounded-lg p-3 leading-relaxed">
                            <strong>Evidence Trace：</strong> {row.evidence_trace}
                          </div>
                          {Array.isArray(row.evidence_quotes) && row.evidence_quotes.length > 0 && (
                            <div className="space-y-2">
                              {row.evidence_quotes.map((quote, quoteIdx) => (
                                <div key={quoteIdx} className="text-xs text-slate-600 border-l-4 border-brand-300 pl-3 py-1 bg-slate-50 rounded-r-lg">
                                  “{quote}”
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </ReportSection>

                    <ReportSection
                      title="Revision Suggestions"
                      open={openSections.suggestions}
                      onToggle={() => setOpenSections((prev) => ({ ...prev, suggestions: !prev.suggestions }))}
                    >
                      <div className="bg-blue-50 border border-blue-100 rounded-2xl p-4">
                        <div className="text-sm text-blue-700 whitespace-pre-wrap leading-relaxed">{assessmentResult.revision_suggestions}</div>
                      </div>
                    </ReportSection>

                    <ReportSection
                      title="Instructor Review Notes"
                      open={openSections.notes}
                      onToggle={() => setOpenSections((prev) => ({ ...prev, notes: !prev.notes }))}
                    >
                      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4">
                        <div className="font-bold text-slate-800 text-sm mb-2">系统草案</div>
                        <div className="text-sm text-slate-600 whitespace-pre-wrap leading-relaxed">{assessmentResult.instructor_review_notes}</div>
                      </div>
                      <textarea
                        value={reviewNotes}
                        onChange={(e) => setReviewNotes(e.target.value)}
                        rows={6}
                        className="w-full border border-slate-300 rounded-xl p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-500"
                        placeholder="在此填写最终 Instructor Review Notes ..."
                      />
                    </ReportSection>
                  </>
                )}
              </div>
            </>
          ) : (
            <div className="h-full flex flex-col items-center justify-between py-4 bg-white">
              <button
                onClick={() => setReportPanelOpen(true)}
                className="border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 p-2 rounded-lg"
                title="展开批改面板"
              >
                <ChevronLeft size={16} />
              </button>
              <div className="text-[11px] text-slate-500 [writing-mode:vertical-rl] [text-orientation:mixed] tracking-[0.15em] select-none">
                教师批改面板
              </div>
              <div className="h-8" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
